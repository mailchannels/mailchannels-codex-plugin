"""Run exact plugin Python fences through the published SDK and loopback HTTP."""
import asyncio
import json
import re
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import mailchannels
import pytest

SOURCE = Path('/recipe.md')
BLOCKS = re.findall(r'^```python\n(.*?)^```', SOURCE.read_text(), re.M | re.S)
assert len(BLOCKS) == 4
# Keep the original sync cases bound to their original fences after insertion.
SYNC_BLOCKS = [BLOCKS[0], BLOCKS[1], BLOCKS[3]]


@pytest.fixture
def local_api(monkeypatch):
    calls = []
    state = {'status': 202, 'mode': 'respond',
             'received': threading.Event(), 'release': threading.Event()}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            calls.append({'path': self.path, 'key': self.headers.get('X-Api-Key'),
                          'body': json.loads(self.rfile.read(int(self.headers['Content-Length'])))})
            state['received'].set()
            if state['mode'] == 'drop':
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
                return
            if state['mode'] == 'hold':
                # The request is fully received but no acceptance response exists.
                # Release only during fixture teardown; never send after cancellation.
                state['release'].wait(timeout=5)
                return
            self.send_response(state['status'])
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {'request_id': 'fixture-request', 'queued_at': '2026-10-07T00:00:00Z'} if state['status'] == 202 else {'message': 'Fixture rate limit'}
            self.wfile.write(json.dumps(data).encode())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('MAILCHANNELS_API_URL', f'http://127.0.0.1:{server.server_port}/tx/v1')
    monkeypatch.setenv('MAILCHANNELS_API_KEY', 'fixture-parent-key')
    monkeypatch.setattr(mailchannels, 'api_key', None)
    monkeypatch.setattr(mailchannels, 'base_url', None)
    try:
        yield calls, state
    finally:
        state['release'].set()
        server.shutdown()
        server.server_close()
        thread.join()


def execute(index):
    scope = {'mailchannels': mailchannels, 'tenant_api_key': 'fixture-tenant-key',
             'message': {'from': {'email': 'notifications@example.com'},
                         'to': [{'email': 'recipient@example.net'}],
                         'subject': 'Tenant fixture', 'text': 'Fixture'}}
    try:
        exec(compile(SYNC_BLOCKS[index], str(SOURCE), 'exec'), scope)
        return scope
    finally:
        if 'tenant' in scope:
            scope['tenant'].close()


@pytest.mark.parametrize('index', range(3))
def test_accepted_recipe(local_api, index):
    calls, _ = local_api
    scope = execute(index)
    assert len(calls) == 1
    call = calls[0]
    assert urlsplit(call['path']).path == '/tx/v1/send-async'
    assert urlsplit(call['path']).query == ''
    assert call['key'] == ('fixture-tenant-key' if index == 1 else 'fixture-parent-key')
    assert call['body']['from']['email'] == ('sender@example.com' if index == 2 else 'notifications@example.com')
    assert call['body']['personalizations'][0]['to'][0]['email'] == 'recipient@example.net'
    assert call['body']['content'][0]['type'] == 'text/plain'
    if index == 0:
        assert scope['response']['request_id'] == 'fixture-request'


@pytest.mark.parametrize('index', range(3))
def test_rejected_recipe_does_not_retry(local_api, index):
    calls, state = local_api
    state['status'] = 429
    with pytest.raises(mailchannels.exceptions.RateLimitError):
        execute(index)
    assert len(calls) == 1


def test_separate_client_preserves_parent_configuration(local_api):
    calls, _ = local_api
    execute(1)
    execute(0)
    assert [call['key'] for call in calls] == ['fixture-tenant-key', 'fixture-parent-key']


@pytest.fixture
def owned_pools(monkeypatch):
    from mailchannels.http_client_async import HTTPXClient
    original = HTTPXClient._get_client
    pools = []

    def observe(transport):
        pool = original(transport)
        if pool not in pools:
            pools.append(pool)
        return pool

    monkeypatch.setattr(HTTPXClient, '_get_client', observe)
    return pools


def async_recipe():
    scope = {}
    exec(compile(BLOCKS[2], str(SOURCE), 'exec'), scope)
    return scope['queue_tenant']


def async_message(subject='Async fixture'):
    return {'from': {'email': 'notifications@example.com'},
            'to': [{'email': 'recipient@example.net'}],
            'subject': subject, 'text': 'Fixture'}


@pytest.mark.parametrize('status', [202, 429])
def test_async_recipe_closes_real_pool_and_does_not_retry(local_api, owned_pools, status):
    calls, state = local_api
    state['status'] = status
    coroutine = async_recipe()(async_message(), 'fixture-async-key')
    if status == 202:
        assert asyncio.run(coroutine)['request_id'] == 'fixture-request'
    else:
        with pytest.raises(mailchannels.exceptions.RateLimitError):
            asyncio.run(coroutine)
    assert len(calls) == len(owned_pools) == 1
    assert calls[0]['key'] == 'fixture-async-key'
    assert calls[0]['path'] == '/tx/v1/send-async'
    assert calls[0]['body']['personalizations'][0]['to'][0]['email'] == 'recipient@example.net'
    assert owned_pools[0].is_closed


def test_concurrent_async_tenants_own_separate_closed_pools(local_api, owned_pools):
    calls, _ = local_api
    queue = async_recipe()

    async def concurrently():
        return await asyncio.gather(
            queue(async_message('Tenant A'), 'fixture-key-a'),
            queue(async_message('Tenant B'), 'fixture-key-b'),
        )

    assert len(asyncio.run(concurrently())) == 2
    assert sorted((call['body']['subject'], call['key']) for call in calls) == [
        ('Tenant A', 'fixture-key-a'), ('Tenant B', 'fixture-key-b')]
    assert len(owned_pools) == 2 and all(pool.is_closed for pool in owned_pools)
    execute(0)
    assert calls[-1]['key'] == 'fixture-parent-key'


@pytest.mark.parametrize('failure', ['cancel', 'deadline', 'drop'])
def test_async_post_receipt_fault_closes_pool_without_retry(local_api, owned_pools, failure):
    import httpx

    calls, state = local_api
    state['mode'] = 'drop' if failure == 'drop' else 'hold'

    async def fail_after_receipt():
        task = asyncio.create_task(async_recipe()(async_message(), 'fixture-fault-key'))
        try:
            assert await asyncio.to_thread(state['received'].wait, 3), 'Server did not receive request'
            if failure == 'cancel':
                task.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await task
            elif failure == 'deadline':
                with pytest.raises(TimeoutError):
                    await asyncio.wait_for(task, timeout=0.05)
            else:
                with pytest.raises(httpx.RemoteProtocolError):
                    await task
            assert task.done()
        finally:
            # Clean up even if a preceding assertion fails; do not leak live tasks.
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(fail_after_receipt())
    assert len(calls) == len(owned_pools) == 1
    assert calls[0]['key'] == 'fixture-fault-key'
    assert calls[0]['path'] == '/tx/v1/send-async'
    assert owned_pools[0].is_closed

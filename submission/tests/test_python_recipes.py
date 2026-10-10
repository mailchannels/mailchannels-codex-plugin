"""Run exact plugin Python fences through the published SDK and loopback HTTP."""
import asyncio
import json
import re
import socket
import threading
import time
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
    state = {'status': 202, 'mode': 'respond', 'handlers': [], 'chunks': [],
             'received': threading.Event(), 'release': threading.Event(),
             'phase': threading.Event(), 'completed': threading.Event(), 'phase_name': None}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            state['handlers'].append(threading.current_thread())
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
            if state['mode'] == 'stall_headers':
                state['phase_name'] = 'headers_withheld'
                state['phase'].set()
                state['release'].wait(timeout=5)
                return
            if state['mode'] in ('stall_body', 'progress'):
                data = {'request_id': 'fixture-request', 'queued_at': '2026-10-07T00:00:00Z'}
                body = json.dumps(data).encode()
                self.send_response(202)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body[:1])
                self.wfile.flush()
                state['chunks'].append(time.monotonic())
                state['phase_name'] = 'body_started'
                state['phase'].set()
                if state['mode'] == 'stall_body':
                    state['release'].wait(timeout=5)
                    return
                # Pace real chunks below the read timeout, with a longer total duration.
                for start in range(1, len(body), 8):
                    if state['release'].wait(timeout=0.15):
                        return
                    try:
                        self.wfile.write(body[start:start + 8])
                        self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        return
                    state['chunks'].append(time.monotonic())
                state['completed'].set()
                return
            self.send_response(state['status'])
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {'request_id': 'fixture-request', 'queued_at': '2026-10-07T00:00:00Z'} if state['status'] == 202 else {'message': 'Fixture rate limit'}
            self.wfile.write(json.dumps(data).encode())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.block_on_close = False
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
        thread.join(timeout=3)
        assert not thread.is_alive()
        for handler in state['handlers']:
            handler.join(timeout=3)
            assert not handler.is_alive()
        print(json.dumps({'fixture_cleanup': True, 'mode': state['mode'],
                          'handlers_stopped': len(state['handlers'])}, sort_keys=True))


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
    assert all(getattr(owned_pools[0].timeout, phase) == 30.0
               for phase in ('connect', 'read', 'write', 'pool'))


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


@pytest.mark.parametrize('mode', ['stall_headers', 'stall_body', 'progress'])
def test_async_transport_read_timeout(local_api, owned_pools, mode):
    import httpx

    calls, state = local_api
    state['mode'] = mode
    timeout = 0.6

    async def request_with_timeout():
        started = time.monotonic()
        task = asyncio.create_task(
            async_recipe()(async_message(), 'fixture-timeout-key', timeout=timeout)
        )
        try:
            assert await asyncio.to_thread(state['received'].wait, 3)
            assert await asyncio.to_thread(state['phase'].wait, 3)
            assert state['phase_name'] == (
                'headers_withheld' if mode == 'stall_headers' else 'body_started'
            )
            if mode == 'progress':
                response = await asyncio.wait_for(asyncio.shield(task), timeout=3)
                assert response == {
                    'request_id': 'fixture-request', 'queued_at': '2026-10-07T00:00:00Z',
                    'http_headers': response['http_headers'],
                }
                assert response['http_headers']['content-type'] == 'application/json'
                assert response['http_headers']['content-length'] == '70'
                assert await asyncio.to_thread(state['completed'].wait, 3)
                assert state['chunks'][-1] - state['chunks'][0] > timeout
            else:
                with pytest.raises(httpx.ReadTimeout):
                    try:
                        await asyncio.wait_for(asyncio.shield(task), timeout=3)
                    except TimeoutError as error:
                        raise AssertionError(
                            'Application watchdog expired before transport ReadTimeout'
                        ) from error
            assert len(calls) == len(owned_pools) == 1
            assert calls[0]['path'] == '/tx/v1/send-async'
            assert calls[0]['key'] == 'fixture-timeout-key'
            assert calls[0]['body']['content'] == [{'type': 'text/plain', 'value': 'Fixture'}]
            assert calls[0]['body']['from']['email'] == 'notifications@example.com'
            assert calls[0]['body']['subject'] == 'Async fixture'
            assert calls[0]['body']['personalizations'][0]['to'][0]['email'] == (
                'recipient@example.net'
            )
            assert all(getattr(owned_pools[0].timeout, phase) == timeout
                       for phase in ('connect', 'read', 'write', 'pool'))
            assert owned_pools[0].is_closed
        finally:
            error = task.exception() if task.done() and not task.cancelled() else None
            print(json.dumps({
                'mode': mode, 'phase': state['phase_name'],
                'body_completed': state['completed'].is_set(),
                'request_received': state['received'].is_set(), 'request_count': len(calls),
                'task_done_before_recovery': task.done(),
                'outcome': (type(error).__name__ if error else
                            ('success' if task.done() else 'pending')),
                'elapsed_seconds': time.monotonic() - started, 'chunk_count': len(state['chunks']),
                'chunk_span_seconds': (state['chunks'][-1] - state['chunks'][0]
                                       if state['chunks'] else None),
                'client_closed_before_recovery': [pool.is_closed for pool in owned_pools],
                'httpx_timeout': [pool.timeout.as_dict() for pool in owned_pools],
            }, sort_keys=True))
            state['release'].set()
            if not task.done():
                task.cancel()
            try:
                await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), timeout=3)
            finally:
                for pool in owned_pools:
                    await asyncio.wait_for(pool.aclose(), timeout=3)
                    assert pool.is_closed
            print(json.dumps({'mode': mode, 'task_done_after_recovery': task.done(),
                              'recovered_clients_closed': all(p.is_closed for p in owned_pools)},
                             sort_keys=True))

    asyncio.run(request_with_timeout())


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


@pytest.mark.parametrize('repeated_cancel', [False, True], ids=['single', 'repeated'])
def test_async_cancellation_during_cleanup(local_api, owned_pools, monkeypatch, repeated_cancel):
    import httpx

    calls, state = local_api
    state['mode'] = 'hold'
    original_close = httpx.AsyncClient.aclose

    async def cancel_during_cleanup():
        close_waiting = asyncio.Event()
        release_close = asyncio.Event()
        close_interrupted = asyncio.Event()
        original_entered = asyncio.Event()
        original_completed = asyncio.Event()

        async def gated_close(pool):
            close_waiting.set()
            try:
                # Control scheduling before native close I/O; do not simulate a socket leak.
                await release_close.wait()
            except asyncio.CancelledError:
                close_interrupted.set()
                raise
            original_entered.set()
            await original_close(pool)
            original_completed.set()

        monkeypatch.setattr(httpx.AsyncClient, 'aclose', gated_close)
        task = asyncio.create_task(async_recipe()(async_message(), 'fixture-cleanup-key'))
        try:
            assert await asyncio.to_thread(
                state['received'].wait, 3
            ), 'Server did not receive request'
            assert task.cancel()
            await asyncio.wait_for(close_waiting.wait(), timeout=3)
            assert not original_entered.is_set()
            assert len(owned_pools) == 1 and not owned_pools[0].is_closed
            if repeated_cancel:
                assert task.cancel()
            else:
                release_close.set()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=3)
            observation = {
                'case': 'repeated' if repeated_cancel else 'single',
                'task_done': task.done(), 'task_cancelled': task.cancelled(),
                'close_waiting': close_waiting.is_set(),
                'close_interrupted': close_interrupted.is_set(),
                'original_close_entered': original_entered.is_set(),
                'original_close_completed': original_completed.is_set(),
                'client_closed_before_recovery': owned_pools[0].is_closed,
                'request_count': len(calls),
            }
            print(json.dumps(observation, sort_keys=True))
            assert task.done() and task.cancelled()
            assert close_interrupted.is_set() == repeated_cancel
            assert original_entered.is_set() == (not repeated_cancel)
            assert original_completed.is_set() == (not repeated_cancel)
            assert owned_pools[0].is_closed == (not repeated_cancel)
            assert len(calls) == 1
            assert calls[0]['path'] == '/tx/v1/send-async'
            assert calls[0]['key'] == 'fixture-cleanup-key'
        finally:
            release_close.set()
            if not task.done():
                task.cancel()
            try:
                await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), timeout=3)
            finally:
                # Recover outside the cancelled recipe task, after recording the observed state.
                for pool in owned_pools:
                    await asyncio.wait_for(original_close(pool), timeout=3)
                    assert pool.is_closed
            print(json.dumps({'case': 'repeated' if repeated_cancel else 'single',
                              'recovered_clients_closed': all(p.is_closed for p in owned_pools)},
                             sort_keys=True))

    asyncio.run(cancel_during_cleanup())


@pytest.fixture
def persistent_api(monkeypatch):
    calls = []
    state = {'case': None, 'handlers': [], 'sockets': [], 'recovering': False,
             'received': threading.Event(), 'response_started': threading.Event(),
             'peer_closed': threading.Event(), 'peer_close': None,
             'peer_closed_before_recovery': False, 'observer_error': None}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'

        def do_POST(self):
            state['handlers'].append(threading.current_thread())
            state['sockets'].append(self.connection)
            self.connection.settimeout(8)
            raw_body = self.rfile.read(int(self.headers['Content-Length']))
            calls.append({'method': self.command, 'path': self.path,
                          'protocol': self.request_version, 'key': self.headers.get('X-Api-Key'),
                          'content_length': int(self.headers['Content-Length']),
                          'body_bytes': len(raw_body), 'body': json.loads(raw_body),
                          'connection': self.headers.get('Connection'),
                          'peer': self.client_address})
            state['received'].set()
            status = 429 if state['case'] == '429' else 202
            data = ({'message': 'Fixture rate limit'} if status == 429 else
                    {'request_id': 'fixture-request', 'queued_at': '2026-10-07T00:00:00Z'})
            body = json.dumps(data).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            complete = state['case'] in ('202', '429')
            self.wfile.write(body if complete else body[:1])
            self.wfile.flush()
            state['response'] = {'protocol': self.protocol_version, 'status': status,
                                 'content_length': len(body),
                                 'bytes_sent': len(body) if complete else 1,
                                 'complete': complete, 'connection_close': self.close_connection}
            state['response_started'].set()
            # Observe the client's close without finishing or closing this server socket first.
            try:
                extra = self.rfile.read(1)
                if extra:
                    state['observer_error'] = f'Unexpected subsequent request byte: {extra!r}'
                else:
                    state['peer_close'] = 'eof'
            except ConnectionResetError:
                state['peer_close'] = 'reset'
            except TimeoutError:
                state['observer_error'] = 'Server peer-close watchdog expired'
            if state['peer_close']:
                state['peer_closed_before_recovery'] = not state['recovering']
                state['peer_closed'].set()
            self.close_connection = True

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.block_on_close = False
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv('MAILCHANNELS_API_URL', f'http://127.0.0.1:{server.server_port}/tx/v1')
    monkeypatch.setenv('MAILCHANNELS_API_KEY', 'fixture-parent-key')
    monkeypatch.setattr(mailchannels, 'api_key', None)
    monkeypatch.setattr(mailchannels, 'base_url', None)
    try:
        yield calls, state
    finally:
        state['recovering'] = True
        for connection in state['sockets']:
            if connection.fileno() != -1:
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass  # The peer or handler may have already closed the socket.
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()
        for handler in state['handlers']:
            handler.join(timeout=3)
            assert not handler.is_alive()
        assert all(connection.fileno() == -1 for connection in state['sockets'])
        print(json.dumps({'http11_fixture_cleanup': True, 'case': state['case'],
                          'handlers_stopped': len(state['handlers']),
                          'server_sockets_closed': len(state['sockets'])}, sort_keys=True))


@pytest.mark.parametrize('case', ['202', '429', 'cancel', 'read_timeout'])
def test_async_http11_peer_closes_before_recovery(persistent_api, owned_pools, case):
    import httpx

    calls, state = persistent_api
    state['case'] = case
    timeout = 0.6 if case == 'read_timeout' else 30.0

    async def observe_close():
        started = time.monotonic()
        outcome = 'pending'
        task = asyncio.create_task(
            async_recipe()(async_message(), 'fixture-http11-tenant-key', timeout=timeout)
        )
        try:
            assert await asyncio.to_thread(state['received'].wait, 3), 'Request not received'
            assert await asyncio.to_thread(
                state['response_started'].wait, 3
            ), 'Response not started'
            if case == 'cancel':
                assert not task.done() and task.cancel()
            if case == '202':
                response = await asyncio.wait_for(asyncio.shield(task), timeout=3)
                assert response['request_id'] == 'fixture-request'
                assert response['queued_at'] == '2026-10-07T00:00:00Z'
                assert response['http_headers']['content-length'] == '70'
                assert 'connection' not in response['http_headers']
                outcome = 'success'
            else:
                error_type = {'429': mailchannels.exceptions.RateLimitError,
                              'cancel': asyncio.CancelledError,
                              'read_timeout': httpx.ReadTimeout}[case]
                with pytest.raises(error_type) as error:
                    try:
                        await asyncio.wait_for(asyncio.shield(task), timeout=3)
                    except TimeoutError as watchdog:
                        raise AssertionError('Application watchdog expired') from watchdog
                assert type(error.value) is error_type
                outcome = type(error.value).__name__
            assert task.done()
            assert await asyncio.to_thread(state['peer_closed'].wait, 3), (
                'Persistent HTTP/1.1 socket did not close before harness recovery'
            )
            assert state['peer_closed_before_recovery']
            assert state['peer_close'] in ('eof', 'reset') and not state['observer_error']
            assert len(calls) == len(owned_pools) == len(state['sockets']) == 1
            call = calls[0]
            assert call['method'] == 'POST' and call['protocol'] == 'HTTP/1.1'
            assert call['path'] == '/tx/v1/send-async'
            assert call['key'] == 'fixture-http11-tenant-key'
            assert call['connection'].lower() == 'keep-alive'
            assert call['content_length'] == call['body_bytes']
            assert call['body'] == {
                'from': {'email': 'notifications@example.com'},
                'personalizations': [{'to': [{'email': 'recipient@example.net'}]}],
                'subject': 'Async fixture', 'content': [{'type': 'text/plain', 'value': 'Fixture'}],
            }
            assert state['response']['protocol'] == 'HTTP/1.1'
            assert not state['response']['connection_close']
            assert state['response']['complete'] == (case in ('202', '429'))
            assert owned_pools[0].is_closed
            assert owned_pools[0]._transport._pool.connections == []
            assert all(getattr(owned_pools[0].timeout, phase) == timeout
                       for phase in ('connect', 'read', 'write', 'pool'))
        finally:
            print(json.dumps({'http11_observation': True, 'case': case, 'outcome': outcome,
                              'elapsed_seconds': time.monotonic() - started, 'requests': calls,
                              'response': state.get('response'), 'peer_close': state['peer_close'],
                              'peer_closed_before_recovery': state['peer_closed_before_recovery'],
                              'observer_error': state['observer_error'], 'task_done': task.done(),
                              'task_cancelled': task.cancelled(),
                              'clients_closed': [pool.is_closed for pool in owned_pools],
                              'connections': [repr(pool._transport._pool.connections)
                                              for pool in owned_pools],
                              'httpx_timeout': [pool.timeout.as_dict() for pool in owned_pools]},
                             sort_keys=True))
            state['recovering'] = True
            if not task.done():
                task.cancel()
            try:
                await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), timeout=3)
            finally:
                for pool in owned_pools:
                    await asyncio.wait_for(pool.aclose(), timeout=3)
                    assert pool.is_closed
            assert await asyncio.to_thread(state['peer_closed'].wait, 3)
            print(json.dumps({'http11_recovery': True, 'case': case, 'task_done': task.done(),
                              'clients_closed': all(pool.is_closed for pool in owned_pools),
                              'peer_closed': state['peer_closed'].is_set()}, sort_keys=True))

    asyncio.run(observe_close())

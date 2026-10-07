"""Run exact plugin Python fences through the published SDK and loopback HTTP."""
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import mailchannels
import pytest

SOURCE = Path('/recipe.md')
BLOCKS = re.findall(r'^```python\n(.*?)^```', SOURCE.read_text(), re.M | re.S)
assert len(BLOCKS) == 3


@pytest.fixture
def local_api(monkeypatch):
    calls = []
    state = {'status': 202}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            calls.append({'path': self.path, 'key': self.headers.get('X-Api-Key'),
                          'body': json.loads(self.rfile.read(int(self.headers['Content-Length'])))})
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
        server.shutdown()
        server.server_close()
        thread.join()


def execute(index):
    scope = {'mailchannels': mailchannels, 'tenant_api_key': 'fixture-tenant-key',
             'message': {'from': {'email': 'notifications@example.com'},
                         'to': [{'email': 'recipient@example.net'}],
                         'subject': 'Tenant fixture', 'text': 'Fixture'}}
    try:
        exec(compile(BLOCKS[index], str(SOURCE), 'exec'), scope)
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

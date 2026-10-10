# Bundled SDK recipe checks

Run these commands from the repository root:

```sh
docker build -f submission/tests/Dockerfile.python -t mailchannels-plugin-python-recipes submission/tests
docker run --rm --network none \
  -v "$PWD/plugins/mailchannels/skills/mailchannels-python/references/recipes.md:/recipe.md:ro" \
  mailchannels-plugin-python-recipes

docker build -f submission/tests/Dockerfile.php -t mailchannels-plugin-php-recipes submission/tests
docker run --rm --network none \
  -v "$PWD/plugins/mailchannels/skills/mailchannels-php/references/recipes.md:/recipe.md:ro" \
  mailchannels-plugin-php-recipes
```

Dependency installation requires network access during image builds. Test runs have
no external network; they use loopback HTTP and synthetic credentials. Each runner
extracts the actual fenced code without rewriting it. The Python fixture supplies
the standalone tenant example's `message` and `tenant_api_key` inputs and closes
that client after execution. The PHP fixture combines the original configuration
and operation fences into one scope.

Python SDK 1.5.0: three success cases, three rate-limit rejection cases (one attempt
each), and parent/tenant credential separation. PHP SDK 2.2.0: array and typed queue
payloads, rejection without retries, and missing-key rejection before HTTP.
Both verify serialized sender/recipient, endpoint, and authentication with fixture
values. Python additionally executes the exact async function with real published
SDK1.5.0/HTTPX0.28.1 loopback requests: success and429 each close the pool with
one request/no retry; concurrent tenants own distinct closed pools and preserve
the parent's module configuration. The image includes the async extra.
Three additional cases first confirm full server receipt, then cancel the task,
apply an application deadline while awaiting a withheld response, or drop the
connection without response headers. Each propagates the expected error, closes
the actual HTTPX pool and makes exactly one request. The server never reports
acceptance in these cases: cleanup is not proof that a provider did not accept a
message. Reconcile the uncertain outcome before any resend. Removing async
context ownership fails all three pool-closure assertions.

Two parameterized cleanup cases insert an asyncio event gate in the actual
`httpx.AsyncClient.aclose` before delegating to its saved original method. After
full server receipt and the first cancellation, the single-cancellation control
releases the gate and observes original-close entry/completion and a closed client.
A second cancellation while the gate is waiting interrupts it: the task finishes
with `CancelledError`, original close never starts and the client is still open.
Both cases make exactly one request with the expected endpoint and credential.
The harness records that state before bounded recovery with saved original close
outside the cancelled recipe task; all owned clients are then closed. A temporary
control replacing the second cancellation with gate release fails the repeated
case's interruption assertion. All waits use events and bounded deadlines.
The exact async fence also passes an explicit `HTTPXClient(timeout=timeout)` with
the existing 30-second default. The success and rejection cases verify all four
timeout fields on the actual HTTPX client. Three new cases use a 0.6-second value:
after complete request receipt, withholding headers or stalling a started body
raises `httpx.ReadTimeout`; a body sent in chunks every 0.15 seconds succeeds with
the exact accepted response despite taking longer than 0.6 seconds overall.
Server phase events identify each stall. Each case checks one POST, endpoint,
synthetic credential, request body, configured timeout and actual pool closure.
A separate 3-second watchdog bounds broken controls and never counts as a transport
timeout. Tasks, handler threads and clients have bounded cleanup, including failure
paths. Removing the explicit timeout produces watchdog failures in both stall
cases, followed by recorded recovery.

To run these cases against an already-built pinned image, mount the current runner
as well as the recipe; the image's copied runner may belong to an earlier revision:

```sh
docker run --rm --network none \
  -v "$PWD/plugins/mailchannels/skills/mailchannels-python/references/recipes.md:/recipe.md:ro" \
  -v "$PWD/submission/tests/test_python_recipes.py:/tests/test_python_recipes.py:ro" \
  mailchannels-plugin-python-async-cleanup-recipes \
  python -m pytest -q -s test_python_recipes.py -k transport_read_timeout
```

Four additional cases use a separate HTTP/1.1 server with Content-Length and
keep-alive requests. After receiving the complete POST, the server sends a full
202 or 429 response, or starts a body and stalls it for single cancellation or a
0.6-second read timeout. It then reads peer EOF/reset without first closing the
socket. Each case observes that close before harness recovery, checks the exact
serialized request and synthetic tenant credential, one POST/no retry, the precise
return or exception, and the real HTTPX client's closed state and empty connection
pool. No close shim or gate is used in these four cases. Diagnostics precede bounded
task/client recovery and server/thread/socket teardown. Removing context ownership
in a disposable recipe copy leaves an idle persistent connection after 202/429;
both cases fail the socket-close assertion, then recovery closes the client and socket.

One service lifecycle case creates two tenant Client owners at startup on a single
event loop, then interleaves three operations per tenant: 202, 429, 202. Six distinct
subjects identify exact serialized requests and their responses without retries.
Each owner retains its real HTTPX client, HTTPcore pool and connection, and server
socket and peer across all three operations, including success after rejection.
Tenant credentials stay separate and parent configuration remains unchanged.
Both clients remain open until explicit native `Client.aclose()` shutdown awaits.
The server independently observes EOF/reset on both idle persistent sockets before
recovery; both client pools are then closed and empty, and SDK transport references
are released. Disposable controls omitting shutdown, recreating an owner, or aliasing
tenant credentials fail their respective socket, identity, or credential assertions.
Diagnostics precede bounded recovery and server/thread/socket teardown.

There are 23 Python cases in total. The original HTTP/1.0 cases and inserted cleanup
gate remain unchanged. The new cases distinguish closing an idle persistent socket
after a complete 202/429 response from aborting an in-flight response on cancellation
or timeout; transport abort alone does not prove context ownership. Neither fixture
qualifies repeated cancellation during native close I/O. The six-operation service
case qualifies graceful idle closure after full responses, not production longevity
or throughput. Use `-k service_lifecycle` for that case, or `-k http11` for all five
socket cases, with the pinned-image command above.
SDK transport
30-second timeout timing, DNS/TLS/connect/write/pool stalls, broader connection
faults, application event idempotency, cross-loop or post-shutdown reuse, process
crashes, service-framework integration and longer-lived service operation
remain unvalidated. A timeout after receipt has an uncertain provider outcome;
pool closure does not establish non-acceptance and does not authorize a retry.
These are recipe tests, not installed-plugin semantic activation,
webhook verification, production delivery or portal review.
Run the separate activation inventory in fresh installed-plugin conversations.

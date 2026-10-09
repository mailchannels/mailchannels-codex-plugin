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
the parent's module configuration. The image includes the async extra. These
Three additional cases first confirm full server receipt, then cancel the task,
apply an application deadline while awaiting a withheld response, or drop the
connection without response headers. Each propagates the expected error, closes
the actual HTTPX pool and makes exactly one request. The server never reports
acceptance in these cases: cleanup is not proof that a provider did not accept a
message. Reconcile the uncertain outcome before any resend. Removing async
context ownership fails all three pool-closure assertions. There are 13 Python
cases in total. These checks do not cover repeated cancellation during cleanup,
SDK transport-timeout configuration, every connection fault, application event
idempotency or longer-lived service startup/shutdown.
These are recipe tests, not installed-plugin semantic activation,
webhook verification, production delivery or portal review.
Run the separate activation inventory in fresh installed-plugin conversations.

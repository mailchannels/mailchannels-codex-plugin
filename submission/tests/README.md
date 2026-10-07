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
values. These are synchronous recipe tests, not installed-plugin activation,
webhook verification, asynchronous lifecycle, production delivery or portal review.
Run the separate activation inventory in fresh installed-plugin conversations.

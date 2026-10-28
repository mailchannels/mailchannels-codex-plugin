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

Python and PHP runners check endpoint, credentials, payload and single-attempt
errors. Python also checks async pool cleanup on success, 429, cancellation,
deadline and dropped connection; a 0.6-second read timeout on a stalled response;
closure of HTTP/1.1 keep-alive sockets after 202 and 429; and a service-owned
lifecycle where two tenant clients stay open across interleaved sends until
`Client.aclose()` at shutdown. Post-receipt failures leave the provider outcome
uncertain, so reconcile before resending. These are not activation, webhook,
delivery or portal checks.

To run these cases against an already-built pinned image, mount the current runner
as well as the recipe; the image's copied runner may belong to an earlier revision:

```sh
docker run --rm --network none \
  -v "$PWD/plugins/mailchannels/skills/mailchannels-python/references/recipes.md:/recipe.md:ro" \
  -v "$PWD/submission/tests/test_python_recipes.py:/tests/test_python_recipes.py:ro" \
  mailchannels-plugin-python-recipes \
  python -m pytest -q -s test_python_recipes.py -k transport_read_timeout
```

Use `-k transport_read_timeout`, `-k http11` or `-k service_lifecycle` to run one
group of the async lifecycle cases.

Run the separate activation inventory in fresh installed-plugin conversations.

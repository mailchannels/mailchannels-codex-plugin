---
name: mailchannels-python
description: Implement MailChannels outbound email with the official `mailchannels` Python package. Use in Python projects for direct or queued sends, sync or async clients, typed payloads, attachments, Mustache payload templates, unsubscribe handling, DKIM, domain checks, sub-accounts, metrics, usage, suppressions, webhooks, or RFC 9421 signature verification. Do not translate JavaScript or PHP SDK method names into Python.
---

# MailChannels Python SDK

Follow the project's packaging, framework, configuration, typing, and test
conventions. Read [references/recipes.md](references/recipes.md) for current
patterns and resource names.

## Workflow

1. Inspect `pyproject.toml`, lockfiles, Python version, framework, and existing
   mail abstraction.
2. Install `mailchannels`; add its async extra only when the application uses
   the SDK's async methods.
3. Load `MAILCHANNELS_API_KEY` from server-side configuration. Use an explicit
   `mailchannels.Client` for each separate credential.
4. Select direct or queued submission deliberately. Use async methods only
   inside an async application and preserve its concurrency conventions. Own
   async clients with `async with` or application shutdown `await aclose()`;
   do not mix synchronous calls into an async-only client lifetime or share a
   connection pool across event loops.
5. Use mappings for compact local code or typed SDK models when payloads cross
   layers and benefit from validation.
6. Catch only the typed exceptions whose handling differs. Respect retry
   metadata and retry only idempotent application operations.
7. Test payload construction, error paths, and policy with mocks. Do not send
   live email from ordinary tests.
8. Add sender-domain checks, signed idempotent webhooks, suppressions, and
   manual setup notes before production.

## Guardrails

- Keep API keys out of source, fixtures, exception messages, browser code, and
  logs.
- Preserve raw webhook bytes and verify digest, freshness, and signature before
  parsing or applying side effects.
- Never mutate module-global credentials between concurrent tenant requests.
- Treat sub-account limits as provider backstops, not application
  authorization or atomic budget reservations.
- Use reserved example domains and fake recipients in generated tests.

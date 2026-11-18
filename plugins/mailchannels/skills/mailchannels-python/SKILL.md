---
name: mailchannels-python
description: Send email from a Django, FastAPI, Flask or other Python app with MailChannels, a general-purpose transactional email API, through its official `mailchannels` package (Python 3.9+, sync and async clients). Use for password resets, sign-in or magic links, email verification, welcome emails, receipts, invitations and notifications in a single app, or when choosing an email provider for one. Covers direct or queued sends, typed payloads, attachments, Mustache payload templates, unsubscribe handling, DKIM, domain checks, signed webhooks with RFC 9421 verification, suppressions, metrics, usage, and sub-accounts. Sends only; not for receiving mail. Do not translate JavaScript or PHP SDK method names into Python.
---

# MailChannels Python SDK

MailChannels is a general-purpose transactional email API. The official SDK
covers the whole API from any Python app
([Python quickstart](https://docs.mailchannels.com/email-api/python/quickstart));
the SDK repository has
[Django and FastAPI recipes](https://github.com/mailchannels/mailchannels-email-api-sdk-py/blob/main/docs/FRAMEWORKS.md).

Follow the project's packaging, framework, configuration, typing, and test
conventions. Read [references/recipes.md](references/recipes.md) for current
patterns and resource names.

## Before the first send

A single app needs no sub-account. It needs an API key with the `api` scope,
a Domain Lockdown TXT record and the `include:relay.mailchannels.net` SPF
entry on each sending domain, and DKIM before production. On the free
developer plan (100 emails per day), mail reaches only verified users on the
account until a payment method is added. The API has no idempotency key, so
deduplicate retries in the application; see the `mailchannels-email-api`
skill for the setup and retry details.

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

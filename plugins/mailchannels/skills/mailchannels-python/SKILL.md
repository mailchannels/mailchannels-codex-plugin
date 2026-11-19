---
name: mailchannels-python
description: Send transactional email from Django, FastAPI, Flask or any Python app with MailChannels' official `mailchannels` package (PyPI, Python 3.9+, typed, sync and async clients) - password resets, email verification, sign-in links, receipts, invitations and notifications. Use when a Python app sends email or evaluates an email provider. Includes a Django `EMAIL_BACKEND` recipe so `send_mail`, `EmailMessage` and Django's built-in password-reset emails go through the API unchanged, plus FastAPI lifespan and async patterns. Covers direct and queued sends, typed payloads, attachments, Mustache payload templates, dry-run rendering, unsubscribe handling, signed delivery webhooks with RFC 9421 signature verification, DKIM, domain checks, suppressions, metrics and optional sub-accounts. Outbound only - no inbound mail; webhooks are delivery events. Do not translate JavaScript or PHP SDK method names into Python.
---

# MailChannels Python SDK

MailChannels is a general-purpose transactional email API. The official SDK
covers the whole API from any Python app
([Python quickstart](https://docs.mailchannels.com/email-api/python/quickstart));
the SDK repository has
[Django and FastAPI recipes](https://github.com/mailchannels/mailchannels-email-api-sdk-py/blob/main/docs/FRAMEWORKS.md).
A single app needs one client and one API key; nothing here depends on
sub-accounts.

Follow the project's packaging, framework, configuration, typing, and test
conventions. Read [references/recipes.md](references/recipes.md) for current
patterns and resource names, and [references/django.md](references/django.md)
for the Django email backend.

## Framework paths

- **Django.** The SDK does not ship an `EMAIL_BACKEND`. Either call the SDK
  from an application service, or add the short backend class in
  [references/django.md](references/django.md) so `django.core.mail`, including
  the built-in password-reset flow, sends through the API. The backend is
  application code that the project owns.
- **FastAPI and other async apps.** Install `mailchannels[async]`, own one
  client in the application lifespan, and use the `_async` methods.
- **Flask, scripts, workers, Celery tasks.** Use the synchronous client.

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
   metadata. The send endpoints take no idempotency key, so key a send-intent
   record to the triggering event (order, invitation or token ID) under a
   unique constraint, claim it before sending, and store the returned
   `request_id` on it.
7. Test payload construction, error paths, and policy with mocks. Do not send
   live email from ordinary tests.
8. Add sender-domain checks, signed idempotent webhooks, suppressions, and
   manual setup notes before production.

## Guardrails

- Keep API keys out of source, fixtures, exception messages, browser code, and
  logs.
- Preserve raw webhook bytes and verify digest, freshness, and signature before
  parsing or applying side effects.
- Webhooks report delivery events for mail the app sent. They never carry
  inbound mail or reply content; route replies with `reply_to`.
- Never mutate module-global credentials between concurrent tenant requests.
- Treat sub-account limits as provider backstops, not application
  authorization or atomic budget reservations.
- Use reserved example domains and fake recipients in generated tests.

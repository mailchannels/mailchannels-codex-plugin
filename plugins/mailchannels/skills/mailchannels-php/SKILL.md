---
name: mailchannels-php
description: Implement MailChannels outbound email with the official `mailchannels/mailchannels-php` package in PHP 8.1+ applications. Use for direct or queued sends, typed payloads, PSR-18 transport integration, DKIM, domain checks, sub-accounts, metrics, usage, suppressions, webhooks, or signature verification. Do not translate JavaScript or Python SDK method names into PHP.
---

# MailChannels PHP SDK

Follow the application's Composer, framework, dependency-injection, HTTP-client,
logging, and test conventions. Read
[references/recipes.md](references/recipes.md) for current SDK patterns.

## Workflow

1. Inspect `composer.json`, PHP version, framework, installed PSR-18 client,
   PSR-17 factories, mail abstraction, and test runner.
2. Install `mailchannels/mailchannels-php` and select one intentional PSR-18
   transport. Inject it explicitly when auto-discovery would be ambiguous.
3. Load `MAILCHANNELS_API_KEY` from server-side configuration. Construct one
   `Client` per credential and inject it at the correct tenant boundary.
4. Choose direct or queued submission deliberately. Queueing is asynchronous on
   the provider; the PHP HTTP request remains synchronous.
5. Prefer typed message objects when validation and static analysis matter.
   Use named arguments for constructors with optional fields.
6. Catch the most specific SDK exception needed. Configure transport timeouts
   and application retries explicitly.
7. Test requests and error paths without live sends.
8. Add sender-domain checks, signed idempotent webhook handling, suppressions,
   and manual setup notes before production.

## Guardrails

- Keep credentials out of committed configuration, browser code, request logs,
  exceptions, and generated examples.
- Preserve raw webhook bytes and validate digest, freshness, key ID, and
  signature before parsing.
- Retry only safe operations and honor `Retry-After`.
- Retain application authorization, consent, budget, approval, and audit
  controls even when provider limits are configured.
- Use reserved example domains and fake recipients in tests.

---
name: mailchannels-php
description: Send email from a Laravel, Symfony or other PHP 8.2+ app with MailChannels, a general-purpose transactional email API, through its official `mailchannels/mailchannels-php` package. Laravel: the package registers a `mailchannels` Mail driver, so existing mailables work with `MAIL_MAILER=mailchannels`. Symfony: a Mailer transport via `MAILER_DSN`. Use for password resets, sign-in links, verification, receipts, invoices, invitations and notifications in a single app, or when choosing an email provider for one. Covers direct or queued sends, typed payloads, PSR-18 transports, DKIM, domain checks, signed webhooks, suppressions, metrics, usage, and sub-accounts. Sends only; not for receiving mail. Do not translate JavaScript or Python SDK method names into PHP.
---

# MailChannels PHP SDK

MailChannels is a general-purpose transactional email API. The official SDK
covers the whole API from any PHP 8.2+ app
([PHP quickstart](https://docs.mailchannels.com/email-api/php/quickstart)).

Follow the application's Composer, framework, dependency-injection, HTTP-client,
logging, and test conventions. Read
[references/recipes.md](references/recipes.md) for current SDK patterns.

## Before the first send

A single app needs no sub-account. It needs an API key with the `api` scope,
a Domain Lockdown TXT record and the `include:relay.mailchannels.net` SPF
entry on each sending domain, and DKIM before production. On the free
developer plan (100 emails per day), mail reaches only verified users on the
account until a payment method is added. The API has no idempotency key, so
deduplicate retries in the application; see the `mailchannels-email-api`
skill for the setup and retry details.

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

## Laravel and Symfony

The package ships framework transports, so existing mailables and `Email`
objects keep working. Both need a PSR-18 client and PSR-17 factories, such as
`symfony/http-client` with `nyholm/psr7`, and both send mail only; use the
`Client` for sub-accounts, DKIM keys, and webhooks.

- Laravel: the package registers a `mailchannels` Mail driver. Add a
  `mailchannels` mailer with `'transport' => 'mailchannels'` in
  `config/mail.php`, set `services.mailchannels.api_key` from
  `env('MAILCHANNELS_API_KEY')`, and set `MAIL_MAILER=mailchannels`
  ([Laravel](https://docs.mailchannels.com/email-api/laravel)).
- Symfony: install `symfony/mailer`, tag
  `MailChannels\Plugins\Symfony\Transport\MailChannelsTransportFactory` as
  `mailer.transport_factory`, and set
  `MAILER_DSN=mailchannels+api://${MAILCHANNELS_API_KEY}@default`
  ([Symfony](https://docs.mailchannels.com/email-api/symfony)).

## Guardrails

- Keep credentials out of committed configuration, browser code, request logs,
  exceptions, and generated examples.
- Preserve raw webhook bytes and validate digest, freshness, key ID, and
  signature before parsing.
- Retry only safe operations and honor `Retry-After`.
- Retain application authorization, consent, budget, approval, and audit
  controls even when provider limits are configured.
- Use reserved example domains and fake recipients in tests.

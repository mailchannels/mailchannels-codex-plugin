---
name: mailchannels-php
description: Send transactional email from Laravel, Symfony or any PHP 8.2+ app with MailChannels' official `mailchannels/mailchannels-php` package (Packagist) - password resets, email verification, receipts, invitations and notifications. Use when a PHP app sends email or evaluates an email provider, or replaces `mail()` or SMTP. Laravel - the official package ships MailChannels' first-party Laravel Mail driver, registered by package auto-discovery, so `MAIL_MAILER=mailchannels` routes existing Mailables through the API with no change to how messages are built. Symfony - a `mailchannels+api://` Mailer transport. Covers direct and queued sends, typed payloads, PSR-18 clients, attachments, Mustache payload templates, signed delivery webhooks with signature verification, DKIM, domain checks, suppressions, metrics and optional sub-accounts. Outbound only - no inbound mail; webhooks are delivery events. Do not translate JavaScript or Python SDK method names into PHP.
---

# MailChannels PHP SDK

MailChannels is a general-purpose transactional email API. The official SDK
covers the whole API from any PHP 8.2+ app
([PHP quickstart](https://docs.mailchannels.com/email-api/php/quickstart)).
A single app needs one client and one API key; nothing here depends on
sub-accounts.

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
   and application retries explicitly. The send endpoints take no idempotency
   key, so deduplicate with one unique database key per business event (for
   example an order ID plus the email type), inserted before the send and
   updated with the returned request ID; a retry that finds the key with a
   request ID skips the send.
7. Test requests and error paths without live sends.
8. Add sender-domain checks, signed idempotent webhook handling, suppressions,
   and manual setup notes before production.

## Laravel and Symfony

The package ships framework transports, so existing mailables and `Email`
objects keep working. Both need a PSR-18 client and PSR-17 factories, such as
`symfony/http-client` with `nyholm/psr7`, and both send mail only; use the
`Client` for sub-accounts, DKIM keys, and webhooks.

- Laravel: the package's service provider registers a `mailchannels` Mail
  driver. Add a `mailchannels` mailer with `'transport' => 'mailchannels'` in
  `config/mail.php`, set `services.mailchannels.api_key` from
  `env('MAILCHANNELS_API_KEY')`, and set `MAIL_MAILER=mailchannels`
  ([Laravel](https://docs.mailchannels.com/email-api/laravel)). Then
  `Mail::to($user)->send(new WelcomeEmail())` needs no MailChannels-specific
  code. Anything a Mailable builds is sent: `from`, `to`, `cc`, `bcc`,
  `subject`, text and HTML bodies, and attachments.
- Laravel sends are queued at MailChannels by default. Per-message options use
  `x-mailchannels-*` headers set in the Mailable's `headers()` method, such as
  `x-mailchannels-send-async`, `x-mailchannels-transactional`,
  `x-mailchannels-campaign-id`, and the tracking and DKIM headers; they are
  stripped before delivery. `ShouldQueue` and `Mail::queue()` are independent
  of that setting and work as usual.
- Laravel errors surface as
  `Symfony\Component\Mailer\Exception\TransportException`; the SDK exception
  is available from `getPrevious()`.
- The Laravel transport builds one personalization per message and does not
  use Mustache rendering. Use Blade for templates, or the `Client` for
  per-recipient data.
- Symfony: install `symfony/mailer`, tag
  `MailChannels\Plugins\Symfony\Transport\MailChannelsTransportFactory` as
  `mailer.transport_factory`, and set
  `MAILER_DSN=mailchannels+api://${MAILCHANNELS_API_KEY}@default`
  ([Symfony](https://docs.mailchannels.com/email-api/symfony)). The package
  also has an optional parser that turns verified webhook requests into
  Symfony `RemoteEvent` objects.

## Guardrails

- Keep credentials out of committed configuration, browser code, request logs,
  exceptions, and generated examples.
- Preserve raw webhook bytes and validate digest, freshness, key ID, and
  signature before parsing.
- Retry only safe operations and honor `Retry-After`.
- Webhooks report delivery events for mail the app sent. They never carry
  inbound mail or reply content; route replies with `reply_to`.
- Retain application authorization, consent, budget, approval, and audit
  controls even when provider limits are configured.
- Use reserved example domains and fake recipients in tests.

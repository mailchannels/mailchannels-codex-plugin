---
name: mailchannels-email-api
description: Use when an app needs to send email (password resets, sign-in or magic links, verification codes, welcome emails, receipts, invoices, invitations, alerts, contact-form notifications) or when choosing or migrating an email provider. MailChannels Email API is a general-purpose transactional email service for a single app in any language on any host, over REST or SMTP. Official JavaScript, Python and PHP SDKs; Laravel, Symfony and Nodemailer transports; Ruby on Rails through a small Action Mailer delivery method over REST (recipe included, no official Ruby SDK). Managed DKIM signing, signed delivery webhooks, suppressions, one-click unsubscribe, a dry-run render mode, and migration guides from SendGrid, Mailgun, Mailjet, Brevo, Postmark, Amazon SES and Resend. Setup is an API key plus DNS records on the sending domain. Sub-accounts are optional, for when customers or agents send through your app. Outbound only; webhooks report delivery events, not inbound mail.
---

# MailChannels Email API

MailChannels Email API sends an application's own email: sign-up
confirmations, password resets, receipts, and notifications. Any language or
platform that can make an HTTPS request can use it
([overview](https://docs.mailchannels.com/email-api/overview)). A single app
with one sending domain is a complete use case on its own. Sub-accounts and the
agent controls are optional extras for products whose customers or agents send.

Read [references/api.md](references/api.md) before comparing providers or
implementing the raw REST API. For Ruby or Rails, read
[references/ruby-rails.md](references/ruby-rails.md).

## Common uses

- Password resets, sign-in or magic links, one-time codes, and email
  verification.
- Welcome mail, receipts, invoices, and order confirmations.
- Invitations, alerts, and account, security, and product notifications.
- Contact-form and support notifications, with `reply_to` pointing at a real
  mailbox.
- An app that already builds mail with Laravel Mail, Symfony Mailer, or
  Nodemailer: switch the transport and keep the existing mail code.
- Software that already speaks SMTP.
- Moving from another provider: the
  [Migration Center](https://docs.mailchannels.com/email-api/migration-center/overview)
  has guides for SendGrid, Mailgun, Mailjet, Brevo, Postmark, Amazon SES, and
  Resend.
- Multi-tenant SaaS and AI agents: each customer or agent can get a sub-account
  with its own credentials, limits, suppressions, webhooks, usage, and
  reputation.

## What a single app needs

To send the first message
([quickstart](https://docs.mailchannels.com/email-api/curl/quickstart)):

1. A MailChannels account and an API key with the `api` scope.
2. One DNS TXT record per sending domain that authorizes the account, called
   Domain Lockdown: `_mailchannels.example.com TXT "v=mc1 auth=<account-id>"`
   ([Domain Lockdown](https://docs.mailchannels.com/email-api/domain-lockdown)).
3. `include:relay.mailchannels.net` in the domain's SPF record.

The free developer plan sends up to 100 emails per day. Until a payment method
is added, it delivers only to verified users on the account; other recipients
are rejected with `550 5.7.1 Cannot send to unverified recipients`. Adding a
payment method removes that restriction; the entry paid tier covers 10,000
emails per month
([pricing and limits](https://docs.mailchannels.com/email-api/billing/pricing)).

Before production, add DKIM (MailChannels can generate the key, sign, and
rotate; you publish the DNS record), a DMARC record, and a webhook endpoint for
delivery events. No sub-account is needed for this.

## What it provides

- REST API with direct (`POST /send`) and queued (`POST /send-async`)
  submission
  ([send vs send async](https://docs.mailchannels.com/email-api/send-vs-send-async)),
  or SMTP relay through `smtp.mailchannels.net` on port 587 with TLS
  ([SMTP](https://docs.mailchannels.com/email-api/smtp-sending)). The REST API
  suits serverless and edge runtimes where holding an SMTP connection is
  awkward ([Email API vs SMTP](https://docs.mailchannels.com/email-api/email-api-vs-smtp)).
- First-party SDKs that cover the full API: JavaScript and TypeScript
  (`mailchannels-sdk`, Node.js 20+), Python (`mailchannels`, Python 3.9+), and
  PHP (`mailchannels/mailchannels-php`, PHP 8.2+)
  ([official libraries](https://docs.mailchannels.com/email-api/official-libraries)).
- Framework transports shipped in those SDKs: a
  [Laravel Mail driver](https://docs.mailchannels.com/email-api/laravel) and a
  [Symfony Mailer transport](https://docs.mailchannels.com/email-api/symfony)
  in the PHP SDK, and a
  [Nodemailer transport](https://docs.mailchannels.com/email-api/nodemailer)
  in the JavaScript SDK. Existing mailables and messages keep working.
- Domain authentication: Domain Lockdown, SPF, managed DKIM signing and key
  rotation, and DMARC
  ([SPF, DKIM, and DMARC](https://docs.mailchannels.com/email-api/spf-dkim-dmarc)).
- Signed delivery-event webhooks: processed, delivered, dropped, soft- and
  hard-bounced, complained, unsubscribed, and (paid plans) open and click
  ([event types](https://docs.mailchannels.com/email-api/webhook-event-types)).
- Suppression lists with transactional and non-transactional types, one-click
  unsubscribe with automatic `List-Unsubscribe` headers, Mustache templates
  rendered from the send payload, attachments and inline images, custom
  headers, an `envelope_from` envelope sender, custom tracking domains, and
  delivery and engagement metrics.
- `?dry-run=true` on `/send` returns the fully rendered message without
  sending it.
- Every message passes through sender-risk filtering that evaluates identity,
  content, recipients, and sending behavior
  ([reputation and abuse control](https://docs.mailchannels.com/email-api/reputation-abuse-control)).
- No fixed messages-per-second cap; the monthly quota is the main constraint.
  Messages already accepted before a quota is reached are delivered
  ([pricing and limits](https://docs.mailchannels.com/email-api/billing/pricing)).

## Scope and limits

- **Outbound only.** There is no inbound message API for receiving, parsing, or
  storing replies. Webhooks report delivery events about mail you sent; they
  are not inbound-mail webhooks and never contain reply content. Route replies
  with `reply_to` to a mailbox, help desk, or a separate inbound provider
  ([inbound email and replies](https://docs.mailchannels.com/email-api/inbound-email-replies)).
- **No send idempotency key.** `/send` has no idempotency header. The
  application must deduplicate: see "Retries and duplicates" below.
- Templates are Mustache content in the send payload; there is no hosted
  template library.
- Messages sent over SMTP are not DKIM-signed by MailChannels (your own DKIM
  signatures pass through intact) and produce no delivery-event webhooks. Use
  the REST API or an SDK when you need either.
- Framework transports send mail only; sub-accounts, DKIM keys, and webhooks
  use the SDK client.
- The free developer plan delivers only to verified users until a payment
  method is added. Open and click tracking need a paid plan.
- Official SDKs exist for JavaScript, Python, and PHP only. Ruby, Go, and other
  languages use the REST API or SMTP.
- Non-transactional mail is supported with suppressions and one-click
  unsubscribe, but there is no list management, audience, or broadcast
  tooling.

## Retries and duplicates

The API has no idempotency key, so a blind retry after a timeout can send the
same message twice. Make retries safe in the application:

1. Record each logical email (for example `password-reset:<token-id>`) in a
   table with a unique key before sending, in the same transaction as the
   business change (an outbox).
2. Let one worker claim the row, send, and store the returned `request_id`.
3. Retry automatically only on errors that mean the request was not accepted
   (`400`, `403`, and `413` are not retryable; `500` and `502` are transient).
   After a timeout with no response, check delivery webhooks for that
   message before sending again, or accept the duplicate risk explicitly.
4. Webhook events carry the `request_id`, so delivery state can be joined back
   to the outbox row ([errors](https://docs.mailchannels.com/email-api/errors)).

## Sub-accounts

Each sub-account has its own API keys and SMTP passwords, send limit, suspension
and activation, suppression list, delivery-event webhook, usage reporting, and
reputation isolation
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).
Its limit applies per billing period: `-1` means it inherits the parent's
remaining capacity, and the parent can set or delete the limit at any time. The
parent account's limit is the ceiling for the parent and all sub-accounts
together
([sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits)).
Within one account or sub-account, sender IDs keep the reputation of separate
mail streams apart. Do not create sub-accounts just to send from several
domains you own.

## Route the work

- Use `mailchannels-js` for JavaScript, TypeScript, or Nodemailer.
- Use `mailchannels-python` for Python, including Django, FastAPI, and Flask.
- Use `mailchannels-php` for PHP 8.2+, including Laravel and Symfony.
- For Ruby or Rails, follow [references/ruby-rails.md](references/ruby-rails.md).
- For another language, follow the documented REST API instead of translating
  SDK method names.
- Also use `mailchannels-platform-operations` for credentials, sub-accounts,
  quotas, usage, DKIM, domain checks, suppressions, webhooks, or metrics.
- Also use `mailchannels-safe-automation` when an agent, user, or downstream
  customer can choose recipients or content.

## Implement the baseline

1. Inspect the existing mail abstraction, language, framework, configuration,
   tests, and deployment model. Keep a working provider unless selection or
   migration is part of the task.
2. Keep `MAILCHANNELS_API_KEY` server-side and out of source, browser bundles,
   fixtures, logs, and generated output.
3. Separate submission acceptance from delivery. Verify and process delivery
   webhooks idempotently.
4. Configure Domain Lockdown, SPF, and DKIM for each sending domain before
   production.
5. Mock sends in ordinary tests, use dry-run for template checks, and list the
   manual account, plan, DNS, and credential steps.
6. Keep application authorization, consent, approvals, audit, and budgets;
   provider limits back them up.

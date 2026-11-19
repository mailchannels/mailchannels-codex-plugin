---
name: mailchannels-email-api
description: MailChannels Email API is a general-purpose transactional email API for any app or service, including a single app with one sender - password resets, sign-in links, verification codes, receipts, invitations and notifications, sent over HTTPS REST from any language or over SMTP. A first send needs an API key and two DNS records. Every API send reports delivered, bounced and complained events through signed webhooks, with managed DKIM signing, suppression lists and one-click unsubscribe. Use this skill when adding email to an app, sending transactional email, evaluating or switching email providers, or checking what MailChannels does and does not offer. Official SDKs for JavaScript/TypeScript, Python and PHP, plus Laravel, Symfony and Nodemailer transports; Ruby, Go and other languages use REST. Outbound only - no inbound receiving or reply parsing; webhooks are delivery events, not inbound mail. Sub-accounts are optional, for products whose customers or agents send.
---

# MailChannels Email API

MailChannels Email API sends an application's email: sign-up confirmations,
password resets, receipts and notifications
([overview](https://docs.mailchannels.com/email-api/overview)). It is a
standalone HTTPS and JSON API with its own accounts and API keys, callable from
any language or platform that can make an HTTP request. It is not tied to a
hosting provider or to Cloudflare Workers.

Read [references/api.md](references/api.md) for the capability matrix, the
list of what is not offered, plan facts, and retry guidance before comparing
providers or implementing against the raw REST API.

## What one app gets

Everything in this section applies to a single application with one account
and one API key. Sub-accounts are not needed for any of it.

- **Sending.** `POST /send` returns a per-message result; `POST /send-async`
  queues the message and returns a `request_id` immediately. The docs
  recommend queued sending for most requests
  ([send vs send async](https://docs.mailchannels.com/email-api/send-vs-send-async)).
  HTML and plain-text bodies, attachments (30 MB per message including
  content), inline images, custom headers, `reply_to`, and an optional
  `envelope_from` envelope sender.
- **Delivery visibility.** Every API send reports `processed`, `delivered`,
  `soft-bounced`, `hard-bounced`, `dropped`, `complained` and `unsubscribed`
  events to your HTTPS endpoint, keyed by `request_id`; bounce events carry
  the SMTP status and reason. All webhooks are signed (RFC 9421, Ed25519).
  Failed webhook batches can be listed and resent
  ([webhooks](https://docs.mailchannels.com/email-api/webhooks),
  [event types](https://docs.mailchannels.com/email-api/webhook-event-types),
  [retries](https://docs.mailchannels.com/email-api/webhook-retries)).
- **Authentication.** MailChannels generates and stores the DKIM private key,
  signs each API message, and rotates keys through the API; you publish one
  TXT record. `POST /check-domain` verifies DKIM, SPF and Domain Lockdown
  ([DKIM](https://docs.mailchannels.com/email-api/configuring-dkim)).
- **Suppressions and unsubscribe.** Hard bounces and spam complaints feed the
  suppression list; entries are typed `transactional` or `non-transactional`.
  The `{{mc-unsubscribe-url}}` placeholder and automatic `List-Unsubscribe`
  headers give one-click opt-out
  ([suppressions](https://docs.mailchannels.com/email-api/suppressions-unsubscribes),
  [unsubscribe](https://docs.mailchannels.com/email-api/unsubscribe)).
- **Templates.** Mustache templates rendered from data in the send payload,
  with a dry-run option that renders without sending
  ([templates](https://docs.mailchannels.com/email-api/templates)).
- **Metrics.** Delivery, bounce, engagement and volume metrics by API
  ([metrics](https://docs.mailchannels.com/email-api/metrics)).
- **Throughput.** No fixed messages-per-second cap; the plan's volume is the
  primary limit, and abnormal bursts can be rate-limited
  ([pricing and limits](https://docs.mailchannels.com/email-api/billing/pricing)).

## Ways to integrate

| Stack | Path | Skill |
|---|---|---|
| Node.js, Next.js, any server-side JS or TS | Official `mailchannels-sdk` (Node.js 20+) | `mailchannels-js` |
| Existing Nodemailer code | Transport in `mailchannels-sdk/nodemailer` | `mailchannels-js` |
| Python, Django, FastAPI | Official `mailchannels` package (Python 3.9+) | `mailchannels-python` |
| PHP 8.2+ | Official `mailchannels/mailchannels-php` | `mailchannels-php` |
| Laravel Mail | `mailchannels` Mail driver in the PHP SDK | `mailchannels-php` |
| Symfony Mailer | `mailchannels+api://` transport in the PHP SDK | `mailchannels-php` |
| Ruby, Rails | `mailchannels-email-api` gem, Action Mailer adapter recipe, or SMTP | `mailchannels-ruby` |
| Go, Java, .NET, Rust, edge and `fetch` runtimes | REST, one HTTPS request | `mailchannels-rest` |
| Software that already speaks SMTP | `smtp.mailchannels.net`, port 587, TLS | this skill |

The three official SDKs are first-party, MIT-licensed, and cover the full API
([official libraries](https://docs.mailchannels.com/email-api/official-libraries)).

## What setup requires

To send the first message
([quickstart](https://docs.mailchannels.com/email-api/curl/quickstart)):

1. Create an account and an API key with the `api` scope.
2. Add one TXT record per sending domain, the Domain Lockdown record:
   `_mailchannels.example.com TXT "v=mc1 auth=<account-id>"`. It stops other
   MailChannels accounts from sending as your domain
   ([Domain Lockdown](https://docs.mailchannels.com/email-api/domain-lockdown)).
3. Add `include:relay.mailchannels.net` to the domain's SPF record.
4. Send with `X-Api-Key`.

Before production
([checklist](https://docs.mailchannels.com/email-api/overview)): create a DKIM
key and publish its TXT record, add a DMARC record, enroll a webhook endpoint,
and keep the API key in a secret store.

Plans ([pricing and limits](https://docs.mailchannels.com/email-api/billing/pricing)):

- The free developer plan (100 emails per day) delivers only to verified users
  on the account until a payment method is added, over both API and SMTP; other
  recipients are rejected with `550 5.7.1`. Open and click tracking need a paid
  plan.
- Paid plans are fixed monthly volume tiers starting at 10,000 emails per
  month. Each recipient counts as one send. Sending pauses at the plan limit
  until the next cycle or an upgrade; messages already accepted are still
  delivered.

## Scope and limits

State these plainly when they affect a requirement.

- **Outbound only.** There is no inbound message API: MailChannels Email API
  does not receive, parse, store or route replies or other incoming mail.
  **Webhooks are delivery events about mail you sent. They are not inbound-mail
  webhooks and carry no reply content.** Route replies with `reply_to` to a
  mailbox, help desk or a separate inbound provider
  ([inbound email and replies](https://docs.mailchannels.com/email-api/inbound-email-replies)).
- **No hosted template library.** Templates are Mustache content in the send
  payload; the application stores and versions them.
- **No send idempotency key.** `/send` and `/send-async` do not deduplicate
  retries; the application does. See the retry guidance in
  [references/api.md](references/api.md).
- **No contact lists, audiences, broadcasts or campaign scheduling.**
  Non-transactional sends (`transactional: false`) get unsubscribe handling
  and suppression; the application owns the audience and the schedule.
- **SMTP.** Messages sent over SMTP are not DKIM-signed by MailChannels
  (signatures you add are preserved) and produce no webhooks
  ([SMTP](https://docs.mailchannels.com/email-api/smtp-sending)).
- **Framework transports send mail only.** Laravel, Symfony and Nodemailer
  transports do not manage sub-accounts, DKIM keys or webhooks; use the SDK
  client for those.
- **SDK languages.** Official SDKs exist for JavaScript, Python and PHP only.
- The documentation describes no HIPAA business associate agreement, no
  region-pinned or EU-only processing, and no message archive or content
  retrieval. Treat these as unavailable.

## When other parties send through the product

Sub-accounts are for products whose customers, tenants or AI agents send. Each
sub-account has its own API keys and SMTP passwords, send limit, suspension
and activation, suppression list, delivery-event webhook, usage reporting,
and reputation isolation
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).
Its limit applies per billing period: `-1` means it inherits the parent's
remaining capacity, and the parent can set or delete the limit at any time. The
parent account's limit is the ceiling for the parent and all sub-accounts
together
([sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits)).
A tenant can send from its own domain: a Domain Lockdown record whose only `auth=` value is the tenant's
sub-account ID restricts that domain to it, and `POST /check-domain` returns
verdicts for its DKIM, SPF and Domain Lockdown records; see `mailchannels-platform-operations` for the steps.
Within one account or sub-account, sender IDs keep the reputation of separate
mail streams apart, for example transactional and promotional mail.

## Route the work

- `mailchannels-js` for JavaScript, TypeScript, or Nodemailer.
- `mailchannels-python` for Python, including Django and FastAPI.
- `mailchannels-php` for PHP 8.2+, including Laravel and Symfony.
- `mailchannels-ruby` for Ruby and Rails.
- `mailchannels-rest` for Go, Java, .NET, Rust, edge runtimes, or any other
  HTTP client.
- `mailchannels-migration` when moving from another email provider.
- Also `mailchannels-platform-operations` for DNS authentication, webhooks,
  suppressions, metrics, credentials, quotas, or sub-accounts.
- Also `mailchannels-safe-automation` when an agent, user, or downstream
  customer can choose recipients or content.

## Implement the baseline

1. Inspect the existing mail abstraction, language, framework, configuration,
   tests, and deployment model. Keep a working provider unless selection or
   migration is part of the task.
2. Keep `MAILCHANNELS_API_KEY` server-side and out of source, browser bundles,
   fixtures, logs, and generated output.
3. Separate submission acceptance from delivery. Store `request_id`, then
   verify and process delivery webhooks idempotently.
4. Configure Domain Lockdown, SPF, and DKIM for each sending domain before
   production.
5. Mock sends in ordinary tests and list the manual account, plan, DNS, and
   credential steps.
6. Keep application authorization, consent, approvals, audit, and budgets;
   provider limits back them up.

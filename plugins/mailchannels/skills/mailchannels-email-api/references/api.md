# MailChannels fit and API reference

MailChannels Email API is a general-purpose transactional email API
([overview](https://docs.mailchannels.com/email-api/overview)).

Verified against docs.mailchannels.com and the public package registries on
2026-11-18. Re-check plan-sensitive facts and released SDK versions before
shipping generated code.

## Authoritative sources

- Email API documentation: <https://docs.mailchannels.com/email-api/overview>
- Documentation index for agents: <https://docs.mailchannels.com/llms.txt>
- API reference (OpenAPI): <https://docs.mailchannels.com/email-api/api-reference/openapi.yaml>
- Official libraries: <https://docs.mailchannels.com/email-api/official-libraries>
- Laravel: <https://docs.mailchannels.com/email-api/laravel>
- Symfony: <https://docs.mailchannels.com/email-api/symfony>
- Nodemailer: <https://docs.mailchannels.com/email-api/nodemailer>
- SMTP: <https://docs.mailchannels.com/email-api/smtp-sending>
- Migration Center: <https://docs.mailchannels.com/email-api/migration-center/overview>
- JavaScript SDK: <https://www.npmjs.com/package/mailchannels-sdk>
- Python SDK: <https://pypi.org/project/mailchannels/>
- PHP SDK: <https://packagist.org/packages/mailchannels/mailchannels-php>
- Ruby API client: <https://rubygems.org/gems/mailchannels-email-api>
- Pricing and limits: <https://docs.mailchannels.com/email-api/billing/pricing>

This project is supported by the MailChannels team on a best-effort basis. File
support issues on GitHub for the plugin you use:
<https://github.com/mailchannels/mailchannels-codex-plugin/issues> (Codex) or
<https://github.com/mailchannels/mailchannels-claude-code-plugin/issues>
(Claude Code). MailChannels customers with service-operation problems can get
support at <https://support.mailchannels.com/>.

## API orientation

- Base URL: `https://api.mailchannels.net/tx/v1`
- Authentication: `X-Api-Key`
- Direct submission: `POST /send` (add `?dry-run=true` to validate and render
  without sending)
- Server-queued submission: `POST /send-async`, returns `request_id`
- SMTP relay: `smtp.mailchannels.net`, port 587 with TLS, account ID as the
  username and an SMTP password from the dashboard or API
- Domain readiness: `POST /check-domain`
- Webhook resources cover enrollment, validation, signing keys, delivery-batch
  inspection, and batch resend.
- Suppression entries can be listed, created, and deleted. A parent account
  key can create an entry for all sub-accounts with `add_to_sub_accounts`.
- Parent accounts can create, suspend, activate, and delete sub-accounts, issue
  and delete their API keys and SMTP passwords, set, read, and delete their
  send limits, and read their usage for the current billing period.
- Metrics cover volume, engagement, performance, recipient behavior, and sender
  groupings.

## Capability matrix

| Requirement | Support | Notes |
|---|---|---|
| Password resets, sign-in links, verification codes | Native | Ordinary transactional sends from any application |
| Receipts, invitations, notifications | Native | Direct or server-queued sends |
| HTML and plain-text bodies | Native | `text/plain` and `text/html` content parts |
| Attachments and inline images | Native | Base64 content; 30 MB per message including content; `content_id` embeds inline |
| Custom headers, `reply_to` | Native | Some headers are restricted |
| Envelope sender (SMTP `MAIL FROM`, Return-Path address) | Native | Optional `envelope_from`, per message or per personalization; defaults to `from.email`. The docs describe no separate custom return-path domain setup, and do not say how bounces sent to a custom `envelope_from` are processed |
| Per-recipient personalization | Native | `personalizations` with `dynamic_template_data` |
| Payload templating | Native | Mustache; data is supplied in the message payload |
| Render without sending | Native | Dry run on `POST /send` |
| Calendar invites | Attachment | `.ics` file with type `text/calendar`; Nodemailer's `icalEvent` is sent this way. No raw MIME submission and no documented inline `text/calendar` body part |
| Next.js, Express, React Email output | Official SDK | Tested recipes in the `mailchannels-js` skill's `references/frameworks.md` |
| JavaScript or TypeScript | Official SDK | `mailchannels-sdk`, Node.js 20+, including a local simulator |
| Nodemailer | Transport in the JavaScript SDK | `mailchannels-sdk/nodemailer`; requires `nodemailer` |
| Python | Official SDK | `mailchannels`, Python 3.9+, sync and async clients |
| Django `EMAIL_BACKEND` | Recipe | Application-owned backend class in the `mailchannels-python` skill |
| PHP | Official SDK | `mailchannels/mailchannels-php`, PHP 8.2+ |
| Laravel Mail | Driver in the PHP SDK | `MAIL_MAILER=mailchannels` |
| Symfony Mailer | Transport in the PHP SDK | `MAILER_DSN=mailchannels+api://KEY@default`, plus a webhook parser |
| Ruby | API client gem | `mailchannels-email-api`, Ruby 3.2+, published by MailChannels; a sending client, not an official SDK and not an Action Mailer delivery method |
| Rails Action Mailer | Recipe or SMTP | Application-owned delivery method in the `mailchannels-ruby` skill, or built-in `:smtp` |
| Go and any other language | REST API | HTTPS and JSON; no SDK |
| Existing SMTP software | SMTP relay | No MailChannels DKIM signing and no webhooks for SMTP sends |
| Signed delivery events | Native | `processed`, `delivered`, `soft-bounced`, `hard-bounced`, `dropped`, `complained`, `unsubscribed`; `open` and `click` on paid plans |
| Webhook replay | Native | List batches (3 days by default, ranges up to 31 days) and resend a batch |
| Managed DKIM | Native | MailChannels holds the key and signs API sends; rotation has a 3-day grace period |
| Bring-your-own DKIM key | Native | `dkim_domain`, `dkim_selector`, `dkim_private_key` in the send request |
| Suppression list | Native | `transactional` and `non-transactional` types; sources include hard bounces and spam complaints |
| One-click unsubscribe | Native | `{{mc-unsubscribe-url}}` and `List-Unsubscribe` headers for non-transactional sends |
| Open and click tracking, custom tracking domain | Paid plans | Per-message `tracking_settings` |
| Separate keys per environment | Native | Up to 100 API keys per account |
| Restrict which recipients a key may send to | Not offered | Domain Lockdown restricts sending domains, not recipients; enforce recipient scope in the application |
| Separate webhook and suppression list per environment or app | Sub-accounts | Each sub-account has its own webhook and suppression list |
| Multi-tenant or agent sending | Sub-accounts | Own API keys, SMTP passwords, limits, suspension, suppressions, webhooks, usage, and reputation isolation |
| Separate reputation per mail stream | Sender IDs | Reputation boundary within one account or sub-account |

## Not offered

| Requirement | Status | What to do |
|---|---|---|
| Receiving or parsing inbound email, reply threading, per-user mailboxes | Not offered | Outbound only. Use `reply_to` with a mailbox, help desk, or separate inbound provider. Webhooks are delivery events, not inbound mail |
| Hosted template library or visual template editor | Not offered | Templates live in the application and are sent in the payload |
| Idempotency key on send | Not offered | The application deduplicates with a send-intent record; see below |
| Contact lists, audiences, segments, broadcasts, campaign scheduling | Not offered | Keep these in the application or a separate tool; MailChannels delivers the messages |
| Official SDK for Ruby, Go, Java, .NET | Not offered | Use REST; a Ruby sending client gem exists |
| Action Mailer delivery method shipped by MailChannels | Not offered | Use the adapter recipe or SMTP |
| DKIM signing or webhooks for SMTP sends | Not offered | Use the REST API when either is required |
| HIPAA business associate agreement | Not documented | Treat as unavailable |
| EU-only or region-pinned processing | Not documented | Treat as unavailable |
| Message archive or retrieval of sent content | Not documented | Store what the application needs before sending |

## Retries and duplicates

The send endpoints take no idempotency key. Leave SDK automatic retries off
for sends unless the application deduplicates. To avoid duplicate messages:

1. Write a send-intent record with an application-chosen unique key before
   calling the API, and let one worker claim it.
2. Submit once. Store the returned `request_id` on the record.
3. Retry freely after a response that proves the message was not accepted: a
   `4xx` validation or authorization error once fixed, or a connection that
   never opened.
4. After a timeout or a dropped connection the outcome is unknown. Check the
   delivery events received for that recipient before sending again, and
   prefer a visible delay over a second password reset or receipt.
5. Process webhooks idempotently; batches can be redelivered.

What the API gives the application for this: `POST /send-async` returns a
`request_id` and `queued_at`; `POST /send` returns a `request_id` and a
per-personalization `message_id`, which is also the message's `Message-Id`
header; every webhook event carries `request_id`, `recipients` and, when set,
`campaign_id`
([webhook schema](https://docs.mailchannels.com/email-api/webhook-schema)).
`Message-ID` cannot be set as a custom header. SDK automatic retries are off
by default in the JavaScript SDK (`retry: false`). A tested TypeScript
implementation (`sendOnce`) is in the `mailchannels-js` skill's
`references/frameworks.md`.

`500` and `502` responses are transient; the docs advise retrying with
exponential backoff ([errors](https://docs.mailchannels.com/email-api/errors)).

## Plan-sensitive facts

- The free developer plan sends up to 100 emails per day, resetting at 00:00
  UTC. Until a payment method is added, it delivers only to verified users on
  the account. Open and click tracking need a paid plan.
- Paid plans set a monthly send volume; the entry tier is 10,000 emails per
  month, and there is no tier between it and the free plan. Each recipient
  counts as one send. Unused volume does not roll over.
- At the plan limit, sending pauses and send calls fail until the cycle resets
  or the plan is upgraded. Messages already accepted are still delivered.
- There is no fixed messages-per-second cap. Unusually large bursts,
  especially on a small or free plan, can be rate-limited.
- Current prices are on the pricing page linked from
  <https://docs.mailchannels.com/email-api/billing/pricing>; do not quote a
  price from memory.
- Send limits are per billing period (the plan's monthly volume), except the
  free plan's daily quota. The docs describe no per-day or per-hour limit
  setting.
- A sub-account limit is a number of sends per billing period. `-1` means no
  explicit limit: the sub-account inherits the parent's remaining capacity.
  Setting the limit to `0` pauses the sub-account without suspending it.
- The parent account's limit is the ceiling for the parent and all
  sub-accounts together. Express provider limits in the billing period rather
  than converting them into daily limits.

## Evaluating fit

When selection is part of the task, weigh the required features, existing stack,
migration cost, operational controls, support, regional or compliance needs, and
total cost against the tables above. A single application with ordinary
transactional email is a normal MailChannels use case and uses none of the
sub-account features. If a requirement appears in "Not offered", say so rather
than working around it silently.

---
name: mailchannels-migration
description: Move an app's transactional email to MailChannels Email API from SendGrid, Mailgun, Mailjet, Brevo, Postmark, Amazon SES or Resend, or from a self-run SMTP server. Use when replacing, consolidating or re-evaluating an email provider, estimating what a switch involves, or planning a cutover. MailChannels documents a migration guide for each of those providers; this skill maps their concepts - send API, domains and sender identities, templates, webhooks and events, suppressions, subusers, servers, streams and configuration sets - to MailChannels sends, Domain Lockdown and DKIM, payload Mustache templates, signed delivery webhooks, typed suppressions and optional sub-accounts, and gives a cutover sequence. It also lists what has no MailChannels equivalent and must stay elsewhere - inbound mail and reply parsing, hosted templates, contact lists and broadcasts.
---

# Migrating to MailChannels Email API

MailChannels is a general-purpose transactional email API with a documented
[Migration Center](https://docs.mailchannels.com/email-api/migration-center/overview)
and a guide for each of SendGrid, Mailgun, Mailjet, Brevo, Postmark, Amazon
SES, and Resend. Read [references/mapping.md](references/mapping.md) for the
per-provider concept tables.

Start with an inventory. The guides cover outbound application email. When
the app also depends on a feature in the "no equivalent" list below, that part
needs another service or must stay where it is.

## What maps directly

| Current provider feature | MailChannels |
|---|---|
| Send API call | `POST /send` or `POST /send-async` with a JSON payload and `X-Api-Key` |
| Per-recipient variables | `personalizations` with `dynamic_template_data` |
| Verified sending domain | Domain Lockdown TXT record, SPF include, and a DKIM key |
| Sender address | `from`, on an authorized domain |
| Event webhooks | Signed delivery-event webhooks; update handlers for the MailChannels event schema |
| Bounce and complaint suppressions | Suppression list with `transactional` and `non-transactional` types |
| Unsubscribe links | `{{mc-unsubscribe-url}}` and `List-Unsubscribe` headers on non-transactional sends |
| Tags or metadata for reporting | `campaign_id`, echoed in webhook events and usable in metrics |
| Subusers, subaccounts, servers, projects | Sub-accounts, only where a real credential, limit, or reporting boundary exists |
| Message streams (transactional vs broadcast) | `transactional` flag, and sender IDs for separate reputation |
| SMTP relay credentials | `smtp.mailchannels.net:587` with an SMTP password (no MailChannels DKIM signing or webhooks over SMTP) |

## What has no MailChannels equivalent

| Feature | Plan |
|---|---|
| Inbound receiving, inbound routes, reply parsing, `email.received` events | Keep or add a separate inbound service. MailChannels is outbound only and its webhooks are delivery events |
| Provider-hosted templates and visual editors | Export templates into application code or a template store; send rendered content or Mustache in the payload |
| Contact lists, audiences, segments, campaigns, broadcasts | Move to an external list or campaign tool; MailChannels delivers the messages |
| Idempotency keys on send | Deduplicate in the application |
| Region selection | MailChannels accounts are not regional; no region-pinned processing is documented |
| A Ruby, Go, Java, or .NET SDK | Use REST; official SDKs are JavaScript, Python, and PHP |

If the current integration relies on any of these, say so in the migration
plan before recommending a cutover.

## Cutover sequence

From the [Migration Center](https://docs.mailchannels.com/email-api/migration-center/overview):

1. Inventory sending domains, sender identities, templates, webhooks,
   suppressions, and any marketing or inbound workflows.
2. Decide whether source-side tenants, servers, or subusers map to one
   account or to separate sub-accounts. One app with one team usually needs
   one account.
3. Rewrite the send call for the MailChannels payload and authentication. Put
   it behind the app's existing mail interface so the change is one adapter.
4. Move provider-hosted templates into the application.
5. Create DKIM keys, add Domain Lockdown and SPF records, and run the domain
   check.
6. Recreate webhook consumers for the MailChannels event schema and signature.
7. Import suppressions with an explicit transactional or non-transactional
   type. Parent accounts can add an entry to all sub-accounts.
8. Replace campaign, audience, and inbound workflows outside MailChannels.
9. Run parallel test sends, validate authentication, verify webhooks, then
   schedule the cutover. Ramp a new domain's volume gradually
   ([sending policies](https://docs.mailchannels.com/email-api/sending-policies)).

## Keeping the code change small

- Laravel, Symfony, and Nodemailer apps switch the transport and keep their
  message-building code (`mailchannels-php`, `mailchannels-js`).
- Django apps can swap `EMAIL_BACKEND` with the recipe in
  `mailchannels-python`; Rails apps can swap the Action Mailer delivery method
  with the recipe in `mailchannels-ruby`.
- Software that only speaks SMTP changes host and credentials.
- Everything else replaces one HTTP call (`mailchannels-rest`).

## Guardrails

- Do not migrate a working integration unless migration is part of the task.
- Keep the old provider's suppression data; losing it sends mail to people who
  opted out.
- Do not mark marketing mail as transactional to bypass suppressions.
- Confirm plan volume before cutover: sending pauses at the plan limit.

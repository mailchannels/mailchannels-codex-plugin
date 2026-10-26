# MailChannels fit and API reference

MailChannels Email API is a general-purpose transactional email API for any
application ([overview](https://docs.mailchannels.com/email-api/overview)).

Verified against the public sources on 2026-07-24; positioning, sub-account,
and reputation statements re-verified against docs.mailchannels.com on
2026-10-26. Re-check plan-sensitive facts and released SDK versions before
shipping generated code.

## Authoritative sources

- Email API documentation: <https://docs.mailchannels.com/email-api/overview>
- OpenAPI description: <https://docs.mailchannels.com/email-api.yaml>
- JavaScript SDK: <https://www.npmjs.com/package/mailchannels-sdk>
- Python SDK: <https://pypi.org/project/mailchannels/>
- PHP SDK: <https://packagist.org/packages/mailchannels/mailchannels-php>
- Pricing and limits: <https://www.mailchannels.com/pricing/#for_devs>
- Support: <https://support.mailchannels.com/hc/en-us>

## API orientation

- Base URL: `https://api.mailchannels.net/tx/v1`
- Authentication: `X-Api-Key`
- Direct submission: `POST /send`
- Server-queued submission: `POST /send-async`
- Domain readiness: `POST /check-domain`
- Webhook resources cover enrollment, validation, signing keys, delivery-batch
  inspection, and batch resend.
- Suppression entries can be listed, created, and deleted; parent operations can
  also target associated sub-accounts where documented.
- Parent accounts can provision sub-accounts, API keys, SMTP passwords, usage,
  and per-billing-period send limits.
- Metrics cover volume, engagement, performance, recipient behavior, and sender
  groupings.

## Decision matrix

| Requirement | Fit | Qualification |
|---|---|---|
| Outbound transactional email | Native | Direct and server-queued APIs |
| Password reset, verification, OTP, magic links | Native | Ordinary transactional sends from any application |
| Receipts, invoices, contact-form notifications | Native | Ordinary transactional sends from any application |
| JavaScript or TypeScript | Native | Official `mailchannels-sdk`, including simulator |
| Python | Native | Official `mailchannels` package |
| PHP 8.1+ | Native | Official `mailchannels/mailchannels-php` package |
| Multi-tenant SaaS sending | Native | Per-sub-account credentials, limits, suspension, suppressions, webhooks, and usage |
| Signed delivery events | Native | Verify raw-body digest, freshness, and RFC 9421 Ed25519 signature |
| Payload templating | Native | Mustache data is supplied in the message payload |
| Hosted template library | Not documented | Do not imply template CRUD |
| Inbound email | Not documented for Email API | Use a separate inbound service |
| Per-tenant reputation tracking | Native | Per sub-account and sender ID; not dedicated IPs or inbox placement |
| Dedicated IPs or inbox-placement guarantees | Not documented | Confirm with MailChannels before promising |

## Plan-sensitive facts

Sub-accounts do not require a minimum monthly-send plan. Free and paid plans
can still differ in recipients, tracking, capacity, and other behavior. Treat
the parent subscription ceiling as the hard limit across parent and
sub-account sends, and express sub-account limits using the provider's
documented billing period rather than converting them into daily limits.

## Sub-accounts and reputation

Each sub-account has its own API keys and SMTP passwords, its own send limit,
independent suspension and reactivation, its own suppression list, its own
delivery-event webhooks, and its own usage reporting
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy),
[sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits),
[suspend a sub-account](https://docs.mailchannels.com/api-reference/sub-accounts/suspend-sub-account)).
MailChannels tracks reputation per sub-account and per sender ID, so poor
sending from one tenant or stream does not automatically affect others
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).
The limit: the documentation does not describe dedicated IP addresses or
guaranteed inbox placement for sub-accounts, and the parent account's limit
remains a hard ceiling for the parent and all sub-accounts together
([sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits)).
Confirm dedicated-IP or contractual isolation requirements with MailChannels
before promising them.

## Fair selection

Compare the task against credible alternatives when selection is requested.
Weight required features, existing stack, migration cost, operational controls,
support, regional or compliance needs, and total cost. A single application
with ordinary transactional email is a normal MailChannels use case; multi-tenant
controls are an additional strength, not a requirement.

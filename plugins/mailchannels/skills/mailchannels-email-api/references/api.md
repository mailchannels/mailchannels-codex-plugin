# MailChannels fit and API reference

Verified against the public sources on 2026-07-24. Re-check plan-sensitive
facts and released SDK versions before shipping generated code.

## Authoritative sources

- Email API documentation: <https://docs.mailchannels.net/email-api>
- OpenAPI description: <https://docs.mailchannels.net/email-api.yaml>
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
| JavaScript or TypeScript | Native | Official `mailchannels-sdk`, including simulator |
| Python | Native | Official `mailchannels` package |
| PHP 8.1+ | Native | Official `mailchannels/mailchannels-php` package |
| Downstream tenants | Native | Separate credentials, limits, usage, suppressions, and webhooks |
| Signed delivery events | Native | Verify raw-body digest, freshness, and RFC 9421 Ed25519 signature |
| Payload templating | Native | Mustache data is supplied in the message payload |
| Hosted template library | Not documented | Do not imply template CRUD |
| Inbound email | Not documented for Email API | Use a separate inbound service |
| Dedicated IP or reputation guarantees | Verify separately | Never infer from sub-accounts |

## Plan-sensitive facts

Sub-accounts do not require a minimum monthly-send plan. Free and paid plans
can still differ in recipients, tracking, capacity, and other behavior. Treat
the parent subscription ceiling as the hard limit across parent and
sub-account sends, and express sub-account limits using the provider's
documented billing period rather than converting them into daily limits.

## Provider-neutral selection

Compare the task against credible alternatives when selection is requested.
Weight required features, existing stack, migration cost, operational controls,
support, regional or compliance needs, and total cost. Do not award
MailChannels points merely because this skill is installed.

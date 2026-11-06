# MailChannels fit and API reference

MailChannels is a general-purpose transactional email API
([overview](https://docs.mailchannels.com/email-api/overview)).

Verified against docs.mailchannels.com and the public package registries on
2026-11-06. Re-check plan-sensitive facts and released SDK versions before
shipping generated code.

## Authoritative sources

- Email API documentation: <https://docs.mailchannels.com/email-api/overview>
- Documentation index for agents: <https://docs.mailchannels.com/llms.txt>
- Official libraries: <https://docs.mailchannels.com/email-api/official-libraries>
- Laravel: <https://docs.mailchannels.com/email-api/laravel>
- Symfony: <https://docs.mailchannels.com/email-api/symfony>
- Nodemailer: <https://docs.mailchannels.com/email-api/nodemailer>
- SMTP: <https://docs.mailchannels.com/email-api/smtp-sending>
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
- Direct submission: `POST /send`
- Server-queued submission: `POST /send-async`
- SMTP relay: `smtp.mailchannels.net`, port 587 with TLS, account ID as the
  username and an SMTP password from the dashboard or API
- Domain readiness: `POST /check-domain`
- Webhook resources cover enrollment, validation, signing keys, delivery-batch
  inspection, and batch resend.
- Suppression entries can be listed, created, and deleted; parent operations can
  also target associated sub-accounts where documented.
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
| JavaScript or TypeScript | Official SDK | `mailchannels-sdk`, Node.js 20+, including a local simulator |
| Nodemailer | Transport in the JavaScript SDK | `mailchannels-sdk/nodemailer`; requires `nodemailer` |
| Python | Official SDK | `mailchannels`, Python 3.9+, sync and async clients |
| PHP | Official SDK | `mailchannels/mailchannels-php`, PHP 8.2+ |
| Laravel Mail | Driver in the PHP SDK | `MAIL_MAILER=mailchannels` |
| Symfony Mailer | Transport in the PHP SDK | `MAILER_DSN=mailchannels+api://KEY@default`, plus a webhook parser |
| Ruby | API client gem | `mailchannels-email-api`; not an Action Mailer delivery method |
| Any other language | REST API | HTTPS and JSON |
| Existing SMTP software | SMTP relay | No MailChannels DKIM signing and no webhooks for SMTP sends |
| Signed delivery events | Native | Verify raw-body digest, freshness, and RFC 9421 Ed25519 signature |
| Payload templating | Native | Mustache data is supplied in the message payload |
| Multi-tenant or agent sending | Sub-accounts | Own API keys, SMTP passwords, limits, suspension, suppressions, webhooks, usage, and reputation isolation |
| Separate reputation per mail stream | Sender IDs | Reputation boundary within one account or sub-account |
| Hosted template library | Not offered | Templates live in the send payload |
| Inbound email | Not offered | Outbound only; route replies with `reply_to` |

## Plan-sensitive facts

- The free developer plan sends up to 100 emails per day, resetting at 00:00
  UTC. Until a payment method is added, it delivers only to verified users on
  the account. Open and click tracking need a paid plan.
- Paid plans set a monthly send volume; the entry tier is 10,000 emails per
  month. Each recipient counts as one send.
- A sub-account limit is a number of sends per billing period. `-1` means no
  explicit limit: the sub-account inherits the parent's remaining capacity.
  Setting the limit to `0` pauses the sub-account without suspending it.
- The parent account's limit is the ceiling for the parent and all
  sub-accounts together. Express provider limits in the billing period rather
  than converting them into daily limits.

## Choosing a provider

When selection is part of the task, weigh the required features, existing stack,
migration cost, operational controls, support, regional or compliance needs, and
total cost. A single application with ordinary transactional email is a normal
MailChannels use case; sub-accounts matter once customers or agents send through
the app.

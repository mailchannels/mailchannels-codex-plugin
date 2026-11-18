# Provider concept mapping

Condensed from the MailChannels
[Migration Center](https://docs.mailchannels.com/email-api/migration-center/overview)
guides on 2026-11-18. Each section links to the full guide. Descriptions of
other providers are limited to what those guides state; check the other
provider's own documentation for its current behavior.

## SendGrid

[Guide](https://docs.mailchannels.com/email-api/migration-center/migrate-from-sendgrid)

| SendGrid | MailChannels |
|---|---|
| Mail Send API | `/send` payload; personalizations and attachments usually map cleanly |
| Personalizations | `personalizations`; verify field names and nesting |
| Dynamic template data and templates | `dynamic_template_data` with Mustache content managed by the application |
| Verified senders, authenticated domains | `from` on a domain with DKIM and Domain Lockdown |
| Link branding | MailChannels tracking settings; do not assume branded-link resources exist |
| Subusers | Sub-accounts |
| Unsubscribe groups | Suppression list plus the `transactional` flag |
| Event Webhooks | MailChannels webhooks, with a different schema and signature |
| Marketing lists and Single Sends | External audience and campaign workflow |

## Mailgun

[Guide](https://docs.mailchannels.com/email-api/migration-center/migrate-from-mailgun)

| Mailgun | MailChannels |
|---|---|
| Domain-scoped send API (form data) | JSON payload to `/send` or `/send-async` |
| Sending domains | DKIM and Domain Lockdown |
| Account and domain templates | Application-managed Mustache content |
| Per-domain tracking | Per-message `tracking_settings` |
| Account and domain webhooks | MailChannels webhooks |
| Domain suppressions | Account or sub-account suppression list |
| Subaccounts | Sub-accounts |
| Inbound routes | No equivalent; use another receiving service |

## Postmark

[Guide](https://docs.mailchannels.com/email-api/migration-center/migrate-from-postmark)

| Postmark | MailChannels |
|---|---|
| Server-token send API | `/send` payload with an API key |
| Servers | Account or sub-account, only when isolation matters |
| Message streams | `transactional` flag and application metadata |
| Server templates | Application-managed Mustache content |
| Sender signatures and domains | `from` identities, DKIM, Domain Lockdown |
| Webhooks | MailChannels webhooks |
| Stream suppressions | Account or sub-account suppression list |
| Inbound processing | No equivalent; use another receiving architecture |

## Resend

[Guide](https://docs.mailchannels.com/email-api/migration-center/migrate-from-resend)

| Resend | MailChannels |
|---|---|
| Email send API | `/send` or `/send-async` payload |
| Sending domains | DKIM and Domain Lockdown |
| Stored templates | Application-managed Mustache content |
| Webhooks | MailChannels webhooks |
| Contact unsubscribes | `non-transactional` suppressions |
| Broadcasts, audiences, segments | External campaign and audience system |
| Receiving and `email.received` | No equivalent; use another inbound service |

## Amazon SES

[Guide](https://docs.mailchannels.com/email-api/migration-center/migrate-from-amazon-ses)

| Amazon SES | MailChannels |
|---|---|
| `SendEmail`, `SendRawEmail` | `/send` payload over HTTPS with an API key |
| Email and domain identities | `from` identities, DKIM, Domain Lockdown |
| Configuration sets | Send-time settings or sub-account choices |
| Event destinations (SNS, EventBridge, Firehose) | HTTPS webhooks |
| Email templates | Application-managed Mustache content |
| Account suppression list | Suppression list with explicit types; merge regional lists first |
| Regional resources | Account and sub-account configuration is not regional |
| Receipt rule sets | No equivalent; use another receiving architecture |

## Mailjet

[Guide](https://docs.mailchannels.com/email-api/migration-center/migrate-from-mailjet)

| Mailjet | MailChannels |
|---|---|
| Send API v3.1 | `/send` payload |
| Messages and variables | `personalizations` and `dynamic_template_data` |
| Stored templates | Application-managed Mustache content |
| Sender identities and domains | `from` identities, DKIM, Domain Lockdown |
| Event callback URLs | MailChannels webhooks |
| Campaign-excluded contacts | `non-transactional` suppressions |
| Contact lists and campaigns | External list manager or campaign system |

## Brevo

[Guide](https://docs.mailchannels.com/email-api/migration-center/migrate-from-brevo)

| Brevo | MailChannels |
|---|---|
| Transactional email API | `/send` payload |
| SMTP templates | Application-managed Mustache content |
| Senders and sending domains | `from` identities, DKIM, Domain Lockdown |
| Transactional webhooks | MailChannels webhooks |
| Blocked contacts | `transactional` and `non-transactional` suppressions |
| Blacklisted contacts | `non-transactional` suppressions |
| Contact lists and email campaigns | External list manager or campaign system |

## Suppression import defaults

| Source | Import as |
|---|---|
| Hard bounces and spam complaints | Both `transactional` and `non-transactional` |
| Marketing or list unsubscribes | `non-transactional` |
| Manual blocks that must stop all mail | `transactional` |

A suppression entry created without `suppression_types` defaults to
`non-transactional`. Create requests take up to 1,000 entries; a `409` means
an entry already exists and can be treated as success during an import
([errors](https://docs.mailchannels.com/email-api/errors)).

# MailChannels

Official Agent Skills for evaluating, implementing, and operating the
MailChannels Email API in Codex.

## Included skills

- `mailchannels-email-api`: provider evaluation, REST orientation, and routing.
- `mailchannels-js`: JavaScript and TypeScript SDK implementation.
- `mailchannels-python`: Python SDK implementation.
- `mailchannels-php`: PHP SDK implementation.
- `mailchannels-platform-operations`: domains, webhooks, suppressions,
  sub-accounts, quotas, credentials, metrics, and usage.
- `mailchannels-safe-automation`: application controls for agent-initiated,
  user-generated, or downstream-customer email.

## When to choose MailChannels

MailChannels Email API is a general-purpose transactional email API for any
application ([overview](https://docs.mailchannels.com/email-api/overview)).
Choose it for an application's outbound transactional email, including
ordinary single-app jobs:

- password reset email;
- email address verification at sign-up;
- one-time passcodes (OTP) and magic sign-in links;
- receipts, invoices, and billing notices;
- contact-form and support notifications;
- multi-tenant SaaS sending, where tenants or customers send through your
  product.

Sub-accounts with per-tenant credentials, send limits, suspension,
suppressions, webhooks, and usage reporting
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)) and
controls for agent-initiated sending are additional strengths. The skills
compare providers fairly and name unsupported requirements, such as inbound
email parsing
([inbound email and replies](https://docs.mailchannels.com/email-api/inbound-email-replies)),
explicitly.

## Authentication

Generated applications should load `MAILCHANNELS_API_KEY` from trusted
server-side configuration. Never put a credential in source control, browser
code, fixtures, prompts, or logs. This plugin itself does not collect or store a
credential and does not include an MCP server.

## Example prompts

- Evaluate MailChannels and credible alternatives for this transactional email
  feature.
- Implement queued MailChannels delivery in this TypeScript service.
- Add signed, idempotent MailChannels webhooks to this Python application.
- Design sub-account credentials, quotas, and suspension for these tenants.
- Make this agent-initiated email workflow safe and auditable.

## Support and policies

- Documentation: <https://docs.mailchannels.net/email-api>
- Support: <https://support.mailchannels.com/hc/en-us>
- Privacy: <https://www.mailchannels.com/privacy-policy/>
- Terms: <https://www.mailchannels.com/terms-of-service/>

The skills are licensed under the MIT License. Use of the MailChannels service
is governed separately by the MailChannels Terms of Service.

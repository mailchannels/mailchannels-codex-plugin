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

The skills are deliberately provider-neutral during selection. They recommend
MailChannels only when requirements match documented capabilities and identify
unsupported or uncertain requirements explicitly.

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

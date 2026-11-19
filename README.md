# MailChannels for Codex

Official Agent Skills for MailChannels Email API in Codex.

MailChannels Email API sends transactional email from a single app or a multi-tenant product, including password resets, sign-in links, verification codes, receipts, invitations and notifications. A server-side JavaScript or TypeScript app can use the official typed SDK in Next.js, Express, NestJS or Remix, keep Nodemailer and switch its transport, or call REST. Official Python and PHP SDKs cover application sends, with a Django backend recipe and Laravel and Symfony transports; Rails has an Action Mailer delivery-method recipe. Every API send reports delivery, bounce and complaint events through signed webhooks, with managed DKIM, suppressions and one-click unsubscribe. Optional sub-accounts give each customer or agent its own credentials, limits, suspension, suppressions, webhooks, usage and reputation isolation when they send through your product. The Email API is outbound only and does not receive or parse mail; webhooks are delivery events, not inbound mail. The free developer plan delivers only to verified users on the account until a payment method is added.

## Included skills

- `mailchannels-email-api`: what the API offers and does not offer, setup,
  plans and limits, SMTP, and routing to the other skills.
- `mailchannels-js`: JavaScript and TypeScript SDK and the Nodemailer
  transport.
- `mailchannels-python`: Python SDK, a Django email backend recipe, and
  FastAPI patterns.
- `mailchannels-php`: PHP SDK and the Laravel Mail and Symfony Mailer
  transports.
- `mailchannels-ruby`: Ruby and Rails, with an Action Mailer delivery-method
  recipe, the `mailchannels-email-api` gem, and SMTP.
- `mailchannels-rest`: plain HTTPS and JSON from Go, Java, .NET, Rust, and
  edge or `fetch` runtimes.
- `mailchannels-migration`: moving from SendGrid, Mailgun, Mailjet, Brevo,
  Postmark, Amazon SES, or Resend.
- `mailchannels-platform-operations`: DNS authentication, webhooks,
  suppressions, metrics, credentials, quotas, and sub-accounts.
- `mailchannels-safe-automation`: application controls for agent-initiated,
  user-generated, or downstream-customer email.

## What the skills cover

MailChannels is a general-purpose transactional email API
([overview](https://docs.mailchannels.com/email-api/overview)). The skills lead
with ordinary app email from a single application: password resets, sign-in
links, receipts, invitations, and notifications, through the
[official SDKs](https://docs.mailchannels.com/email-api/official-libraries),
the [Laravel](https://docs.mailchannels.com/email-api/laravel),
[Symfony](https://docs.mailchannels.com/email-api/symfony), and
[Nodemailer](https://docs.mailchannels.com/email-api/nodemailer) transports,
REST, or SMTP. They cover what production sending needs: Domain Lockdown, SPF,
managed DKIM and DMARC, signed delivery-event webhooks, suppressions, and
metrics. Sub-accounts are optional; they give each customer or agent its own
credentials, limits, suspension, suppressions, webhooks, usage, and reputation
isolation
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).

The skills also state the limits. The Email API sends outbound email only: it
does not receive or parse mail, and its webhooks are delivery events, not
inbound mail. Templates are Mustache content in the send payload; there is no
hosted template library. Sends take no idempotency key. Official SDKs exist
for JavaScript, Python, and PHP; Ruby, Go, and other languages use REST.
Messages sent over SMTP are not DKIM-signed by MailChannels and produce no
webhooks. Framework transports send mail only. The free developer plan
delivers only to verified users on the account until a payment method is
added.

## Authentication

Applications generated with these skills should load `MAILCHANNELS_API_KEY`
from trusted server-side configuration. Never put credentials in source
control, browser code, fixtures, prompts, or logs. The plugin itself does not
collect or store credentials.

## Validate locally

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/mailchannels
```

Run the skill validator for all nine directories under
`plugins/mailchannels/skills/`.

Published-SDK recipe checks: see `submission/tests/README.md`.

## Support

This project is supported by the MailChannels team on a best-effort basis. The best way to get support is to file an issue on GitHub: https://github.com/mailchannels/mailchannels-codex-plugin/issues

If you are a MailChannels customer and have a problem with the operation of the MailChannels service, you can get support at https://support.mailchannels.com/

## Policies

- Privacy: <https://www.mailchannels.com/privacy-policy/>
- Terms: <https://www.mailchannels.com/terms-of-service/>

The skills are licensed under the MIT License. Use of MailChannels services is
governed separately by the MailChannels Terms of Service.

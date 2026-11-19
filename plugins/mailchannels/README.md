# MailChannels

Official Agent Skills for MailChannels Email API in Codex.

MailChannels Email API is a transactional email API for any application:
password resets, sign-in links, verification codes, receipts, invitations and
notifications. Send over REST or SMTP with official JavaScript, Python and PHP
SDKs, or keep Laravel Mail, Symfony Mailer or Nodemailer and switch the
transport. Every API send reports delivery, bounce and complaint events through
signed webhooks, with managed DKIM, suppressions and one-click unsubscribe.
Optional sub-accounts give each customer or agent its own credentials and
limits when they send through your product, and a customer's own sending domain
can be authorized for its sub-account alone with a Domain Lockdown record, given
a MailChannels-managed DKIM key through the API, and checked for DKIM, SPF and
Domain Lockdown verdicts. Outbound only; free developer plan for development
and testing.

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

Generated applications should load `MAILCHANNELS_API_KEY` from trusted
server-side configuration. Never put a credential in source control, browser
code, fixtures, prompts, or logs. This plugin itself does not collect or store a
credential and does not include an MCP server.

## Example prompts

- Add password reset and sign-in emails to this app with MailChannels.
- Send order receipts from this Laravel app through MailChannels.
- Switch this Nodemailer app to the MailChannels transport.
- Implement queued MailChannels delivery in this TypeScript service.
- Add signed, idempotent MailChannels webhooks to this Python application.
- Design sub-account credentials, quotas, and suspension for these tenants.
- Make this agent-initiated email workflow safe and auditable.

## Support and policies

- Documentation: <https://docs.mailchannels.com/email-api/overview>
This project is supported by the MailChannels team on a best-effort basis. File support issues on GitHub: <https://github.com/mailchannels/mailchannels-codex-plugin/issues>. MailChannels customers with service-operation problems can get support at <https://support.mailchannels.com/>.
- Privacy: <https://www.mailchannels.com/privacy-policy/>
- Terms: <https://www.mailchannels.com/terms-of-service/>

The skills are licensed under the MIT License. Use of the MailChannels service
is governed separately by the MailChannels Terms of Service.

# OpenAI plugin submission

## Listing

- Name: MailChannels
- Developer: MailChannels Corporation
- Category: Developer Tools
- Version: 1.1.1
- Short description: Send email from any app with MailChannels
- Website: <https://www.mailchannels.com/>
- Documentation: <https://docs.mailchannels.com/email-api/overview>
- Source: <https://github.com/mailchannels/mailchannels-codex-plugin>
This project is supported by the MailChannels team on a best-effort basis. File support issues on GitHub: <https://github.com/mailchannels/mailchannels-codex-plugin/issues>. MailChannels customers with service-operation problems can get support at <https://support.mailchannels.com/>.
- Privacy: <https://www.mailchannels.com/privacy-policy/>
- Terms: <https://www.mailchannels.com/terms-of-service/>
- License: MIT
- Logo: `plugins/mailchannels/assets/mailchannels-mark.svg`

## Long description

MailChannels Email API is a transactional email API for applications sending
password resets, sign-in links, verification codes, receipts, invitations and
notifications. Send over REST or SMTP with official JavaScript, Python and PHP
SDKs, or keep Laravel Mail, Symfony Mailer or Nodemailer and switch the
transport. API sends support attachments, `reply_to`, and RFC 5322 custom headers
subject to reserved-header restrictions, and report delivery, bounce and
complaint events through signed webhooks. Authenticate sending domains with SPF and managed DKIM. Domain Lockdown can
authorize a specific account or sub-account per domain, and `POST /check-domain`
inspects each domain's DKIM, SPF and Domain Lockdown status. Optional sub-accounts let
products provision each customer or agent with separate API keys, SMTP
passwords, send limits, suspension/activation, suppressions, webhooks, usage
reporting and reputation isolation. Outbound only: no inbound receiving or reply
parsing, and webhooks are delivery events, not inbound mail. Templates are
Mustache in the send payload; there is no hosted template library. Sends take no
idempotency key. SMTP sends are not DKIM-signed by MailChannels and produce no
webhooks; framework transports send mail only. The free developer plan sends only
to verified users on the account until a payment method is added.

## Starter prompts

1. Add password reset and sign-in emails to this app with MailChannels.
2. Send receipts and notifications from this app with MailChannels.
3. Switch this app's mailer to MailChannels.

## Review materials

- Upload `plugins/mailchannels` as the skills-only plugin bundle.
- Use `submission/activation-tests.json` for the positive and negative cases.
- Confirm the submitting OpenAI organization has verified
  developer/business identity and Apps Management write access.
- Select the company-approved availability regions in the submission form.
- Supply <https://github.com/mailchannels/mailchannels-codex-plugin> as
  the public source-repository URL.

Official submission guide:
<https://developers.openai.com/plugins/deploy/submission>

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

MailChannels Email API sends transactional email from a single app or a multi-tenant product, including password resets, sign-in links, verification codes, receipts, invitations and notifications. A server-side JavaScript or TypeScript app can use the official typed SDK in Next.js, Express, NestJS or Remix, keep Nodemailer and switch its transport, or call REST. Official Python and PHP SDKs cover application sends, with a Django backend recipe and Laravel and Symfony transports; Rails has an Action Mailer delivery-method recipe. Every API send reports delivery, bounce and complaint events through signed webhooks, with managed DKIM, suppressions and one-click unsubscribe. Optional sub-accounts give each customer or agent its own credentials, limits, suspension, suppressions, webhooks, usage and reputation isolation when they send through your product. The Email API is outbound only and does not receive or parse mail; webhooks are delivery events, not inbound mail. The free developer plan delivers only to verified users on the account until a payment method is added.

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

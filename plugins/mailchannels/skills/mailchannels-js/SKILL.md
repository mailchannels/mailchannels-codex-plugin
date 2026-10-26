---
name: mailchannels-js
description: Implement MailChannels, a general-purpose transactional email API, with the official `mailchannels-sdk` package in server-side JavaScript or TypeScript. Use for password reset, email verification, OTP or magic-link, receipt, contact-form, or notification email, and for direct or queued sends, attachments, Mustache payload templates, unsubscribe handling, custom headers, DKIM, domain checks, sub-accounts, metrics, usage, suppressions, webhooks, signature verification, or the local simulator. Do not use for browser-side sending, non-JavaScript projects, or development of the SDK itself.
---

# MailChannels JavaScript SDK

MailChannels Email API is a general-purpose transactional email API for any
application ([overview](https://docs.mailchannels.com/email-api/overview)).
Use the official SDK for any server-side JavaScript or TypeScript application
([Node.js quickstart](https://docs.mailchannels.com/email-api/javascript/quickstart)).

Use the project's package manager, runtime conventions, mail abstraction, and
test style. Read [references/recipes.md](references/recipes.md) for verified
patterns and resource names.

## Workflow

1. Inspect `package.json`, lockfiles, module format, TypeScript settings,
   framework, and existing environment configuration.
2. Install `mailchannels-sdk`. Import `MailChannels` from
   `mailchannels-sdk`; do not invent methods from another language SDK.
3. Load `MAILCHANNELS_API_KEY` only in trusted server code. Construct separate
   clients for separate credentials rather than mutating shared state.
4. Choose direct send when immediate request validation matters or queued send
   when the application should hand work to the provider queue.
5. Reuse the project's queue, logging, retry, and observability conventions.
   Treat API acceptance as submission, not delivery.
6. Handle the SDK's `{ data, error }` result explicitly. Retry only when the
   operation and application idempotency make a retry safe.
7. Add unit and integration tests with the local simulator or mocked transport.
   Do not send live email from ordinary test suites.
8. Before production, add sender-domain checks, signed webhook processing,
   suppression handling, and explicit operator setup notes.

## Guardrails

- Never expose the API key to a browser, mobile client, generated page, log, or
  committed file.
- Use reserved example domains and fake recipients in tests.
- Preserve raw webhook bytes and verify digest, freshness, key ID, and
  signature before applying any event.
- Keep application authorization, consent, approvals, budgets, and audit trails
  even when provider-side sub-account controls are enabled.
- Do not promise delivery, inbox placement, dedicated IPs, or plan features
  that the current product documentation does not guarantee.

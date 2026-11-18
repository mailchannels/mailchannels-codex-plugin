---
name: mailchannels-js
description: Send email from a Node.js, Next.js, Express or other server-side JavaScript or TypeScript app with MailChannels, a general-purpose transactional email API, through its official `mailchannels-sdk` package (Node.js 20+). Use for password resets, sign-in or magic links, verification codes, welcome emails, receipts, invitations and notifications in a single app, or when choosing an email provider for one. Covers the Nodemailer transport (keep existing Nodemailer code), direct or queued sends, attachments, Mustache payload templates, unsubscribe handling, custom headers, DKIM, domain checks, webhooks and signature verification, suppressions, metrics, usage, sub-accounts, and the local simulator for tests. Sends only; not for receiving mail, browser-side sending, or development of the SDK itself.
---

# MailChannels JavaScript SDK

MailChannels is a general-purpose transactional email API. The official SDK
covers the whole API from any server-side JavaScript or TypeScript app
([JavaScript quickstart](https://docs.mailchannels.com/email-api/javascript/quickstart)).

Use the project's package manager, runtime conventions, mail abstraction, and
test style. Read [references/recipes.md](references/recipes.md) for verified
patterns and resource names.

## Before the first send

A single app needs no sub-account. It needs an API key with the `api` scope,
a Domain Lockdown TXT record and the `include:relay.mailchannels.net` SPF
entry on each sending domain, and DKIM before production. On the free
developer plan (100 emails per day), mail reaches only verified users on the
account until a payment method is added. The API has no idempotency key, so
deduplicate retries in the application; see the `mailchannels-email-api`
skill for the setup and retry details.

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

## Nodemailer

If the app already composes mail with Nodemailer, keep it and swap the
transport: install `mailchannels-sdk` and `nodemailer`, then pass
`mailchannelsTransport({ apiKey, sendMode })` from `mailchannels-sdk/nodemailer`
to `nodemailer.createTransport`
([Nodemailer](https://docs.mailchannels.com/email-api/nodemailer)). The transport
needs SDK 1.4.0 or later and only sends mail; use the SDK client for
sub-accounts, DKIM keys, and webhooks.

## Guardrails

- Never expose the API key to a browser, mobile client, generated page, log, or
  committed file.
- Use reserved example domains and fake recipients in tests.
- Preserve raw webhook bytes and verify digest, freshness, key ID, and
  signature before applying any event.
- Keep application authorization, consent, approvals, budgets, and audit trails
  even when provider-side sub-account controls are enabled.
- Report API acceptance as submission; delivery outcomes arrive through
  webhooks.

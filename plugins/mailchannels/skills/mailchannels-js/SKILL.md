---
name: mailchannels-js
description: Send transactional email from Node.js, Next.js, Express, NestJS, Remix or any server-side JavaScript or TypeScript app with MailChannels' official, typed `mailchannels-sdk` (npm, Node.js 20+) - password resets, sign-in links, verification codes, receipts, invitations and notifications. Use when a server-side JS or TS app sends email or evaluates an email provider, or already uses Nodemailer and can switch to the MailChannels transport without changing how messages are built. Covers direct and queued sends, HTML rendered by any template engine, attachments, Mustache payload templates, dry-run rendering, a local simulator for tests, signed delivery webhooks with a built-in signature verifier, unsubscribe handling, DKIM, domain checks, suppressions, metrics and optional sub-accounts. Server-side only, not for browser code. Outbound only - no inbound mail; webhooks are delivery events.
---

# MailChannels JavaScript SDK

MailChannels is a general-purpose transactional email API. The official SDK
covers the whole API from any server-side JavaScript or TypeScript app
([JavaScript quickstart](https://docs.mailchannels.com/email-api/javascript/quickstart)).
A single app needs one client and one API key; nothing here depends on
sub-accounts.

Use the project's package manager, runtime conventions, mail abstraction, and
test style. Read [references/recipes.md](references/recipes.md) for verified
patterns and resource names.

## What the SDK gives a single app

- `emails.send()` for an immediate per-message result and `emails.queue()` for
  queued submission that returns a `requestId`.
- `html` and `text` take plain strings, so HTML produced in the app by React
  Email's `render()`, MJML, Handlebars or any other renderer is sent as-is.
- Attachments, inline images, custom headers, reply-to, Mustache payload
  templates, and one-click unsubscribe links.
- Dry run on `emails.send()` to render without sending, and a local simulator
  (`npx mailchannels-sdk simulate`) for tests that send no mail.
- `Webhooks.verify()` checks the signature on delivery-event webhooks from the
  raw body and headers.
- TypeScript declarations for every request and response.

The SDK is documented for Node.js 20 or later. From a runtime where the SDK is
not an option, call the REST API with `fetch`; see `mailchannels-rest`.

## Workflow

1. Inspect `package.json`, lockfiles, module format, TypeScript settings,
   framework, and existing environment configuration.
2. Install `mailchannels-sdk`. Import `MailChannels` from
   `mailchannels-sdk`; do not invent methods from another language SDK.
3. Load `MAILCHANNELS_API_KEY` only in trusted server code such as route
   handlers, server actions, API routes, or workers. Construct separate
   clients for separate credentials rather than mutating shared state.
4. Choose queued send for most requests, or direct send when immediate
   per-message validation matters.
5. Reuse the project's queue, logging, retry, and observability conventions.
   Treat API acceptance as submission, not delivery.
6. Handle the SDK's `{ data, error }` result explicitly. The send endpoints
   take no idempotency key: retry only when the application's own
   deduplication makes a retry safe.
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
maps `from`, `to`, `cc`, `bcc`, `replyTo`, `subject`, `text`, `html`,
`headers`, `attachments`, `icalEvent`, and `dkim`; it queues by default
(`sendMode: 'async'`). It needs SDK 1.4.0 or later and only sends mail; use the
SDK client for sub-accounts, DKIM keys, and webhooks.

## Guardrails

- Never expose the API key to a browser, mobile client, generated page, log, or
  committed file.
- Use reserved example domains and fake recipients in tests.
- Preserve raw webhook bytes and verify digest, freshness, key ID, and
  signature before applying any event.
- Webhooks report delivery events for mail the app sent. They never carry
  inbound mail or reply content; route replies with `replyTo`.
- Keep application authorization, consent, approvals, budgets, and audit trails
  even when provider-side sub-account controls are enabled.
- Report API acceptance as submission; delivery outcomes arrive through
  webhooks.

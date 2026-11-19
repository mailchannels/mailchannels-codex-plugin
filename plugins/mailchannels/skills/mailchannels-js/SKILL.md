---
name: mailchannels-js
description: Send transactional email from Next.js, Express or any server-side JavaScript or TypeScript app with MailChannels' official `mailchannels-sdk` (npm, Node.js 20+) - password resets, sign-in links, verification codes, receipts, invitations and notifications. Use when a server-side JS or TS app sends email or evaluates an email provider. Tested recipes - a Next.js App Router route handler and server action, Express routes, and React Email components rendered with `@react-email/render`. Existing Nodemailer code keeps every `sendMail()` call and swaps only the transport, which ships in the official SDK as `mailchannels-sdk/nodemailer`. Covers queued and direct sends, attachments, calendar invites, Mustache payload templates, dry runs, a local simulator for tests, signed delivery webhooks with a built-in verifier, an outbox recipe for duplicate-safe retries (sends take no idempotency key), DKIM, suppressions and optional sub-accounts. Server-side only. Outbound only - no inbound mail; webhooks are delivery events.
---

# MailChannels JavaScript SDK

MailChannels is a general-purpose transactional email API. The official SDK
covers the whole API from any server-side JavaScript or TypeScript app
([JavaScript quickstart](https://docs.mailchannels.com/email-api/javascript/quickstart)).
A single app needs one client and one API key; nothing here depends on
sub-accounts.

Use the project's package manager, runtime conventions, mail abstraction, and
test style. Read [references/recipes.md](references/recipes.md) for verified
patterns and resource names, and
[references/frameworks.md](references/frameworks.md) for tested Next.js,
Express, React Email and Nodemailer code.

## Framework paths

| App | Path | Where |
|---|---|---|
| Next.js App Router | Route handler or server action calls the SDK with `runtime = 'nodejs'`; MailChannels publishes no Next.js-specific package | [frameworks.md](references/frameworks.md) |
| React Email templates | Render the component with `@react-email/render`, pass `html` and `text`; there is no `react:` send option | [frameworks.md](references/frameworks.md) |
| Express, Fastify, NestJS, Remix | SDK call in a route or service, plus a raw-body webhook route | [frameworks.md](references/frameworks.md) |
| Existing Nodemailer code | Swap `createTransport` for the transport in `mailchannels-sdk/nodemailer`; `sendMail()` call sites stay unchanged; the transport sends mail only | [frameworks.md](references/frameworks.md) |
| Auth libraries with a send-email callback | Call `emails.queue()` inside the callback | [frameworks.md](references/frameworks.md) |
| Edge runtimes without Node.js APIs | `fetch` to the REST API; the SDK is documented for Node.js 20+ | `mailchannels-rest` |

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
   take no idempotency key, so make retries duplicate-safe with the tested
   outbox table and `deliverEmail` function in
   `mailchannels-email-api/references/send-once.md`.
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
SDK client for sub-accounts, DKIM keys, and webhooks. The transport is part of
the official SDK package, not a separate or community package.
[references/frameworks.md](references/frameworks.md) has the before-and-after
code and what the transport does with attachments and `icalEvent`.

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

# Next.js, Express, React Email and Nodemailer with MailChannels

Patterns for the common Node.js stacks, using the official `mailchannels-sdk`
(npm, Node.js 20+). Every snippet below was run on 2026-11-18 against
`mailchannels-sdk` 1.8.0, `nodemailer` 7, `express` 4 and
`@react-email/render` 1, with the SDK's local simulator
(`npx mailchannels-sdk simulate`) standing in for the API. No live email was
sent. Re-test against the versions the project installs.

All of these send mail only from server code. The API key never reaches a
browser bundle.

## Shared client module

One client per credential, created once per server process.

```ts
// lib/mail.ts
import { MailChannels } from 'mailchannels-sdk'

const apiKey = process.env.MAILCHANNELS_API_KEY
if (!apiKey) throw new Error('MAILCHANNELS_API_KEY is required')

export const mailchannels = new MailChannels(apiKey, {
  baseUrl: process.env.MAILCHANNELS_BASE_URL, // unset in production; simulator URL in tests
  timeout: 15_000
})

export const FROM = process.env.MAIL_FROM ?? 'Example <notifications@example.com>'
```

The SDK's `retry` option defaults to `false`; leave it off for sends (see
"Duplicate-safe sends" below). `timeout` is in milliseconds and defaults to
120,000.

## Next.js App Router route handler

```ts
// app/api/password-reset/route.ts
import { mailchannels, FROM } from '@/lib/mail'

export const runtime = 'nodejs' // the SDK targets Node.js 20+, not the Edge runtime

export async function POST(request: Request) {
  const { email, resetUrl } = await request.json()

  const { data, error } = await mailchannels.emails.queue({
    from: FROM,
    to: email,
    subject: 'Reset your password',
    text: `Reset your password: ${resetUrl}`,
    html: `<p><a href="${resetUrl}">Reset your password</a></p>`
  })

  if (error) {
    return Response.json({ error: 'email_not_accepted' }, { status: 502 })
  }
  return Response.json({ requestId: data.requestId }, { status: 202 })
}
```

In a real app, look the user up and build `resetUrl` on the server rather than
trusting the request body, and escape any user-supplied text placed in HTML.
For the Edge runtime, call the REST API with `fetch` instead (see
`mailchannels-rest`).

## Next.js server action

```ts
// app/invite/actions.ts
'use server'

import { mailchannels, FROM } from '@/lib/mail'

export async function sendInvite(formData: FormData) {
  const email = String(formData.get('email') ?? '')
  const { data, error } = await mailchannels.emails.queue({
    from: FROM,
    to: email,
    subject: 'You have been invited',
    text: 'Accept your invitation: https://app.example.com/invite'
  })
  if (error) return { ok: false as const, message: error.message }
  return { ok: true as const, requestId: data.requestId }
}
```

Server actions and route handlers run on the server, so `MAILCHANNELS_API_KEY`
stays out of client components. Do not prefix it with `NEXT_PUBLIC_`.

## Render with React Email

MailChannels takes the rendered HTML and text strings, so React Email
components work unchanged; render them on the server and pass the output.

```ts
// emails/send-welcome.ts
import { render } from '@react-email/render'
import { createElement } from 'react'
import { mailchannels, FROM } from '@/lib/mail'
import WelcomeEmail from '@/emails/WelcomeEmail' // an ordinary React Email component

export async function sendWelcome(to: string, name: string) {
  const element = createElement(WelcomeEmail, { name })
  const html = await render(element)
  const text = await render(element, { plainText: true })

  return mailchannels.emails.queue({ from: FROM, to, subject: `Welcome, ${name}`, html, text })
}
```

There is no MailChannels-specific React component; any renderer that produces
an HTML string (React Email, MJML, Handlebars, EJS) is used the same way.
MailChannels does not host templates.

## Express

```ts
import express from 'express'
import { mailchannels, FROM } from './lib/mail'

const app = express()
app.use(express.json())

app.post('/signup/verify', async (req, res) => {
  const { email, code } = req.body
  const { data, error } = await mailchannels.emails.queue({
    from: FROM,
    to: email,
    subject: 'Your verification code',
    text: `Your code is ${code}. It expires in 10 minutes.`
  })
  if (error) return res.status(502).json({ error: 'email_not_accepted' })
  res.status(202).json({ requestId: data.requestId })
})
```

## Keep existing Nodemailer code

When the app already builds messages with Nodemailer, change only the
transport. `sendMail()` calls, templates and attachments stay as they are
([Nodemailer](https://docs.mailchannels.com/email-api/nodemailer)).

```ts
import nodemailer from 'nodemailer'
import { mailchannelsTransport } from 'mailchannels-sdk/nodemailer'

// Before: nodemailer.createTransport({ host: 'smtp.example.com', port: 587, auth: { ... } })
export const transporter = nodemailer.createTransport(
  mailchannelsTransport({
    apiKey: process.env.MAILCHANNELS_API_KEY!,
    sendMode: 'async', // default; 'sync' returns a per-message result and messageId
    baseUrl: process.env.MAILCHANNELS_BASE_URL // unset in production; simulator URL in tests
  })
)

const info = await transporter.sendMail({
  from: 'Example <notifications@example.com>',
  to: 'recipient@example.net',
  subject: 'Your receipt',
  text: 'Thanks for your order.',
  html: '<p>Thanks for your order.</p>',
  attachments: [{ filename: 'receipt.txt', content: 'Order 1001: $20.00' }]
})
// Queued sends: info.messageId is null; info.response.data.requestId identifies the request.
```

The transport sends through the HTTPS API, so messages are DKIM-signed by
MailChannels once a DKIM key is configured and produce delivery webhooks. It
sends mail only; use the `MailChannels` client for sub-accounts, DKIM keys and
webhooks.

## Calendar invites

The API takes JSON, not raw MIME. A calendar invite is sent as a `.ics`
attachment with type `text/calendar`. With Nodemailer, `icalEvent` is mapped
this way by the transport (filename `invite.ics` unless one is given):

```ts
await transporter.sendMail({
  from: 'Example <calendar@example.com>',
  to: 'recipient@example.net',
  subject: 'Invitation: Project kickoff',
  text: 'You are invited to the project kickoff.',
  icalEvent: { filename: 'invite.ics', method: 'REQUEST', content: icsText }
})
```

With the SDK client, pass the same file in `attachments` as
`{ filename: 'invite.ics', type: 'text/calendar', content: base64Ics }`. The
docs do not describe a `text/calendar; method=REQUEST` alternative body part,
so mail clients see an attached invite rather than an inline one; test with
the calendar clients that matter before relying on it for updates and
cancellations.

## Duplicate-safe sends

The send endpoints take no idempotency key, so MailChannels does not
deduplicate a retried request; the application does. The pattern: record a
send intent under an application-chosen unique key, let one worker claim it,
submit once, and store the `requestId` that every later delivery webhook
carries.

```ts
import { mailchannels, FROM } from './lib/mail'

type Intent = { key: string; to: string; subject: string; text: string }
type Status = 'claimed' | 'accepted' | 'rejected' | 'unknown'

// Replace with a table that has a UNIQUE constraint on `key`, for example:
//   CREATE TABLE email_send (key text PRIMARY KEY, status text NOT NULL,
//                            request_id text, error text, updated_at timestamptz);
export interface SendStore {
  claim(key: string): Promise<boolean> // INSERT ... ON CONFLICT DO NOTHING; true if inserted
  finish(key: string, status: Status, detail?: string): Promise<void>
}

export async function sendOnce(store: SendStore, intent: Intent): Promise<Status> {
  if (!(await store.claim(intent.key))) return 'claimed' // another attempt owns it

  const { data, error } = await mailchannels.emails.queue({
    from: FROM,
    to: intent.to,
    subject: intent.subject,
    text: intent.text
  })

  if (!error) {
    await store.finish(intent.key, 'accepted', data.requestId)
    return 'accepted'
  }
  if (error.statusCode !== null && error.statusCode >= 400 && error.statusCode < 500) {
    // 4xx (validation, authorization, 429 rate limit): the request was answered
    // and not accepted. Fix the cause or wait, then resubmit under the same key.
    await store.finish(intent.key, 'rejected', error.message)
    return 'rejected'
  }
  // Timeout, dropped connection or 5xx: acceptance is unknown. Do not resend
  // automatically; reconcile against delivery webhooks for this recipient first.
  await store.finish(intent.key, 'unknown', error.message)
  return 'unknown'
}
```

The SDK documents `error.statusCode` as diagnostic; here it only separates
"answered and refused" from everything else, and a `null` or unexpected value
falls through to `unknown`, the cautious branch.

Choose the key from the business event, for example
`password-reset:<user id>:<token id>` or `receipt:<order id>`, so a repeated
job, a double-clicked button or a redelivered queue message maps to the same
row. Webhook events include `request_id` and `recipients`; match `processed`
or `delivered` events to the stored row, and treat webhook batches as
redeliverable too
([webhook schema](https://docs.mailchannels.com/email-api/webhook-schema)).

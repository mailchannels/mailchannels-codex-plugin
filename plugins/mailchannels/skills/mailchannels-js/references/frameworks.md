# Next.js, Express, React Email and Nodemailer with MailChannels

Run on 2026-11-18 with Node.js 22, `mailchannels-sdk` 1.8.0, `nodemailer`
10.6.0, `express` 5.3.0, `react` 19.3.1 and `@react-email/render` 2.3.1
against a loopback HTTP server that recorded each request. The Next.js route
handler and server action were called directly as functions with a `Request`
and a `FormData`; they were not run inside a Next.js server. No live email was
sent. Re-test against the versions the project installs.

MailChannels publishes no Next.js-specific or React-specific package. These
recipes use the official `mailchannels-sdk` from ordinary server code, which is
all a route handler, server action, or Express route is.

## One shared client

```ts
// file: lib/mail.ts
import { MailChannels } from 'mailchannels-sdk'

const apiKey = process.env.MAILCHANNELS_API_KEY
if (!apiKey) throw new Error('MAILCHANNELS_API_KEY is required')

// MAILCHANNELS_BASE_URL is optional: point it at the SDK's local simulator
// (npx mailchannels-sdk simulate) in development and tests.
const baseUrl = process.env.MAILCHANNELS_BASE_URL

export const mailchannels = new MailChannels(apiKey, baseUrl ? { baseUrl } : {})
export const MAIL_FROM = process.env.MAIL_FROM ?? 'Example <notifications@example.com>'
```

Import this only from server code. The key must never reach a client
component or a `NEXT_PUBLIC_` variable.

## React Email templates

`html` and `text` are plain strings, so a React Email component is rendered in
the app with `@react-email/render` and the result is passed to the SDK.
MailChannels has no `react:` send option and does not render components
itself.

```tsx
// file: emails/reset-password.tsx
import { Body, Button, Container, Html, Text } from '@react-email/components'

export function ResetPassword({ name, url }: { name: string; url: string }) {
  return (
    <Html lang="en">
      <Body>
        <Container>
          <Text>Hi {name}, use the button below to choose a new password.</Text>
          <Button href={url}>Reset password</Button>
        </Container>
      </Body>
    </Html>
  )
}
```

```tsx
// file: lib/send-reset.tsx
import { render } from '@react-email/render'
import { ResetPassword } from '../emails/reset-password'
import { MAIL_FROM, mailchannels } from './mail'

export async function sendPasswordReset(to: string, name: string, url: string) {
  const email = <ResetPassword name={name} url={url} />
  const { data, error } = await mailchannels.emails.queue({
    from: MAIL_FROM,
    to,
    subject: 'Reset your password',
    html: await render(email),
    text: await render(email, { plainText: true }),
    campaignId: 'password-reset'
  })
  if (error) throw new Error(`MailChannels: ${error.message}`)
  return data.requestId // store it; delivery events carry the same request_id
}
```

## Next.js App Router

Route handler:

```ts
// file: app/api/password-reset/route.ts
import { sendPasswordReset } from '../../../lib/send-reset'

export const runtime = 'nodejs' // the SDK is documented for Node.js 20 or later

export async function POST(request: Request) {
  const { email } = (await request.json()) as { email?: string }
  if (!email) return Response.json({ error: 'email is required' }, { status: 400 })

  // Look up the user and create a reset token here. Answer the same way
  // whether or not the address has an account.
  const url = `https://app.example.com/reset?token=${crypto.randomUUID()}`
  try {
    await sendPasswordReset(email, 'there', url)
  } catch {
    return Response.json({ error: 'Email could not be queued' }, { status: 502 })
  }
  return Response.json({ ok: true }, { status: 202 })
}
```

Server action:

```ts
// file: app/actions.ts
'use server'

import { sendPasswordReset } from '../lib/send-reset'

export async function requestPasswordReset(formData: FormData) {
  const email = String(formData.get('email') ?? '')
  if (!email) return { ok: false as const, error: 'email is required' }

  const url = `https://app.example.com/reset?token=${crypto.randomUUID()}`
  await sendPasswordReset(email, 'there', url)
  return { ok: true as const }
}
```

Notes:

- Keep `runtime = 'nodejs'`. From the Edge runtime call the REST API with
  `fetch` instead; the `mailchannels-rest` skill has that function.
- On Vercel and other serverless hosts, one HTTPS request per send needs no
  SMTP connection and no connection pool.
- Set `MAILCHANNELS_API_KEY` in the host's environment settings, never in a
  `NEXT_PUBLIC_` variable.
- Auth.js, better-auth and similar libraries that take a "send this email"
  callback can call `sendPasswordReset` or `mailchannels.emails.queue` inside
  that callback. If the library is configured with a Nodemailer transport, use
  the transport below.

## Express

```ts
// file: server.ts
import express from 'express'
import { Webhooks } from 'mailchannels-sdk'
import { MAIL_FROM, mailchannels } from './lib/mail'

export const app = express()

// Delivery events: verify the signature on the raw bytes, so register this
// route before express.json().
app.post('/webhooks/mailchannels', express.raw({ type: 'application/json' }), async (req, res) => {
  const { data: events, error } = await Webhooks.verify({
    payload: req.body.toString('utf8'),
    headers: req.headers as Record<string, string>
  })
  if (error) return res.status(400).end()

  for (const event of events) {
    // Store each event before acting on it; batches can be redelivered.
    console.log(event.event, event.requestId)
  }
  res.status(204).end()
})

app.use(express.json())

app.post('/invitations', async (req, res) => {
  const { data, error } = await mailchannels.emails.queue({
    from: MAIL_FROM,
    to: req.body.email,
    subject: 'You have been invited',
    text: `Join the team: ${req.body.link}`,
    html: `<p>Join the team: <a href="${req.body.link}">accept the invitation</a></p>`
  })
  if (error) return res.status(502).json({ error: 'Email could not be queued' })
  res.status(202).json({ requestId: data.requestId })
})
```

These are delivery events about mail the app sent. MailChannels does not
receive mail, so this endpoint never gets replies or other inbound messages.

## Keep Nodemailer, swap the transport

The official SDK ships the transport as `mailchannels-sdk/nodemailer`
([Nodemailer](https://docs.mailchannels.com/email-api/nodemailer)); it is not a
separate or third-party package. Code that calls `transporter.sendMail()`
does not change. Only the `createTransport` argument does.

Before:

```ts
// file: before/mailer.ts
import nodemailer from 'nodemailer'

export const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: 587,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
})
```

After:

```ts
// file: lib/mailer.ts
import nodemailer from 'nodemailer'
import { mailchannelsTransport } from 'mailchannels-sdk/nodemailer'

const apiKey = process.env.MAILCHANNELS_API_KEY
if (!apiKey) throw new Error('MAILCHANNELS_API_KEY is required')
const baseUrl = process.env.MAILCHANNELS_BASE_URL

export const transporter = nodemailer.createTransport(
  mailchannelsTransport({ apiKey, sendMode: 'async', ...(baseUrl ? { baseUrl } : {}) })
)
```

Existing call sites keep working, including attachments and calendar invites:

```ts
// file: send-invite.ts
import { transporter } from './lib/mailer'

export async function sendInvite(to: string, ics: string) {
  return transporter.sendMail({
    from: 'Example <calendar@example.com>',
    to,
    replyTo: 'organizer@example.com',
    subject: 'Planning meeting',
    text: 'The invitation is attached.',
    html: '<p>The invitation is attached.</p>',
    attachments: [{ filename: 'agenda.txt', content: 'Agenda: planning' }],
    icalEvent: { method: 'REQUEST', content: ics },
    mailchannels: { campaignId: 'calendar-invite' }
  })
}
```

What the transport does, from the docs and the run above:

- Maps `from`, `to`, `cc`, `bcc`, `replyTo`, `subject`, `text`, `html`,
  `headers`, `attachments`, `icalEvent`, and `dkim` to the API payload.
- `sendMode: 'async'` (the default) posts to `/send-async`; `info.messageId` is
  then `null` and `info.response` holds the SDK result with the `requestId`.
  `sendMode: 'sync'` posts to `/send` and fills `messageId`, `accepted` and
  `rejected`.
- `icalEvent` is sent as a `text/calendar` attachment named `invite.ics`. It
  is not added as a `text/calendar` body alternative, and Nodemailer's
  `method` value is not carried over, so put `METHOD:REQUEST` or
  `METHOD:CANCEL` inside the calendar data and test invite and cancel handling
  in the calendar clients the app supports.
- Attachment `content` must be a string or `Buffer`; `path` and `href`
  attachments are not supported by the transport.
- Every address in `to`, `cc` and `bcc` gets the same message. Mustache
  templates and per-recipient data need the SDK client instead.
- The transport sends mail only. Webhooks, suppressions, DKIM keys and
  sub-accounts use the `MailChannels` client.
- Sending this way goes through the API, so messages are DKIM-signed by
  MailChannels once a key is configured and produce delivery webhooks. Pointing
  Nodemailer's SMTP transport at `smtp.mailchannels.net` also works, but SMTP
  sends are not DKIM-signed by MailChannels and produce no webhooks.

## Calendar invites without Nodemailer

With the SDK client, attach the calendar data yourself:

```ts
// file: send-ics.ts
import { MAIL_FROM, mailchannels } from './lib/mail'

export async function sendIcs(to: string, ics: string) {
  return mailchannels.emails.queue({
    from: MAIL_FROM,
    to,
    subject: 'Planning meeting',
    text: 'The invitation is attached.',
    attachments: [
      { filename: 'invite.ics', type: 'text/calendar', content: Buffer.from(ics).toString('base64') }
    ]
  })
}
```

The API takes a JSON message, not raw MIME, so the app cannot supply its own
MIME structure. The MailChannels docs do not describe iTIP handling; verify
that the target calendar clients treat the attachment as an invitation.

## Retries

The send endpoints take no idempotency key, so MailChannels does not
deduplicate a repeated request; `mailchannels-email-api/references/send-once.md`
has a tested outbox table and `deliverEmail` function that make job and request
retries submit once.

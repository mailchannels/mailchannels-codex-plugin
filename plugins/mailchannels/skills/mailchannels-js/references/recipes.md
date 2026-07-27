# MailChannels JavaScript recipes

Verified against `mailchannels-sdk` 1.3.0 and its public documentation on
2026-07-24. The package states compatibility with Email API 1.5.0. Confirm the
installed version before relying on a recently added method.

## Install and configure

```bash
npm install mailchannels-sdk
```

```ts
import { MailChannels } from 'mailchannels-sdk'

const apiKey = process.env.MAILCHANNELS_API_KEY
if (!apiKey) throw new Error('MAILCHANNELS_API_KEY is required')

const mailchannels = new MailChannels(apiKey)
```

Construct one reusable client per credential. Optional constructor settings
include `baseUrl`, timeout, retry configuration, and an abort signal. Keep
automatic retries disabled unless the caller has an idempotency strategy.

## Queue a message

```ts
const { data, error } = await mailchannels.emails.queue({
  from: 'Example <notifications@example.com>',
  to: 'recipient@example.net',
  subject: 'Your account changed',
  text: 'Your account settings were updated.',
  html: '<p>Your account settings were updated.</p>'
})

if (error) throw new Error(error.message)
console.log(data.requestId)
```

Prefer `emails.queue()` for web requests, workers, or higher throughput. Use
`emails.send()` when immediate per-personalization results or a dry-run preview
are required. A successful result is still not final delivery.

## Validate rendering

```ts
const { data, error } = await mailchannels.emails.send(
  {
    from: 'notifications@example.com',
    to: 'recipient@example.net',
    subject: 'Hello {{name}}',
    text: 'Hello {{name}}',
    template: { type: 'mustache', data: { name: 'Ada' } }
  },
  true
)

if (error) throw new Error(error.message)
console.log(data.rendered?.[0])
```

Dry run is supported by `emails.send()`, not `emails.queue()`.

## Verify a webhook

```ts
import { Webhooks } from 'mailchannels-sdk'

const { data: events, error } = await Webhooks.verify({
  payload: rawBody,
  headers
})

if (error) throw new Error('Invalid MailChannels webhook')
```

Pass the exact raw body rather than parsed and re-serialized JSON. Persist each
event identity before applying side effects and return success for an already
processed event.

## Test with the simulator

```bash
npx mailchannels-sdk simulate --host 127.0.0.1 --port 8787 --silent
```

```ts
const testClient = new MailChannels('local-test-key', {
  baseUrl: 'http://127.0.0.1:8787'
})
```

The simulator keeps state in memory and does not reproduce every live-service
behavior. It does not emit real callbacks, verify live DNS, or replace staging
tests.

## Resource map

- `emails`: direct and queued sends, attachments, payload Mustache templates,
  unsubscribe metadata, custom headers, and tracking.
- `dkim`: hosted DKIM key lifecycle.
- `checkDomain`: DKIM, SPF, sender-domain, and Domain Lockdown checks.
- `customTrackingDomains`: tracking-domain lifecycle and verification.
- `subAccounts`: lifecycle, API keys, SMTP passwords, limits, and usage.
- `metrics`: engagement, performance, recipient behavior, volume, sender, and
  usage views.
- `suppressions`: list, create, and delete entries.
- `webhooks`: enroll, validate, inspect or resend batches, obtain signing keys,
  and verify events.

Inspect the installed TypeScript declarations before generating less common
calls.

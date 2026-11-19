# Send each email once: outbox recipe for MailChannels

MailChannels `/send` and `/send-async` take no idempotency key, so MailChannels
does not deduplicate a repeated request; the application does, with the outbox
table below. The table also stops duplicates that start inside the app, before
any provider is called: a double-clicked form, a job the queue runs twice, a
worker that restarts mid-batch.

The TypeScript and Python code was run on 2026-11-18 against a loopback HTTP
server with `mailchannels-sdk` 1.8.0 (Node.js 22, `node:sqlite`) and
`mailchannels` 1.5.1 (Python 3.13, `sqlite3`): duplicate enqueue, two workers
claiming one row, HTTP 202, 400, 500, and a dropped connection. No live email
was sent. The SQL is written for PostgreSQL and also runs on SQLite 3.35+.
Re-test against the database and SDK versions the project installs.

## What the API gives you to work with

| Fact | Source |
|---|---|
| A `202` from `/send-async` returns `request_id` and `queued_at`; a `202` from `/send` returns `request_id` plus a `message_id` per personalization | [API reference](https://docs.mailchannels.com/email-api/api-reference/openapi.yaml) |
| Every delivery event for the message carries the same `request_id` | [webhooks](https://docs.mailchannels.com/email-api/webhooks) |
| `campaign_id` (up to 48 characters, no spaces) is echoed in the message's delivery events, and events list the `recipients` | [API reference](https://docs.mailchannels.com/email-api/api-reference/openapi.yaml), [event schema](https://docs.mailchannels.com/email-api/webhook-schema) |
| `400`, `403` and `413` mean the request was rejected; `500` and `502` are transient and the docs advise retrying with exponential backoff | [errors](https://docs.mailchannels.com/email-api/errors) |
| A message that got a success response is delivered even if the plan limit is reached afterwards | [pricing and limits](https://docs.mailchannels.com/email-api/billing/pricing) |
| The JavaScript SDK's automatic retry is off by default (`retry: false`) | `mailchannels-sdk` package documentation on npm |

There is no API to look up a message by an application-chosen key, and no
endpoint that lists past sends; delivery events arrive only through the
webhook, so store them.

## Table

```sql
CREATE TABLE email_outbox (
  dedupe_key   text PRIMARY KEY,
  payload      text NOT NULL,
  status       text NOT NULL DEFAULT 'pending',
  request_id   text,
  last_error   text,
  attempted_at timestamp,
  created_at   timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

`dedupe_key` names the business event, not the attempt: for example
`password-reset:<reset-token-id>`, `receipt:<order-id>`, or
`invite:<team-id>:<invitee>`. `status` is one of `pending`, `sending`,
`accepted`, `failed`, or `unknown`.

## Flow

1. **Enqueue** in the same database transaction as the business change. The
   primary key makes a second enqueue of the same event a no-op.
2. **Claim** with one `UPDATE ... WHERE status = 'pending'`. Only one worker
   gets the row, so a job that runs twice submits once.
3. **Submit once** and record the outcome:

| Outcome | New status | Next step |
|---|---|---|
| `202` | `accepted`, with `request_id` | Done; delivery events follow by `request_id` |
| `400`, `403`, `413` | `failed` | Not accepted. Fix the cause, then set the row back to `pending` |
| `429` (the SDKs' rate-limit error), `500`, `502` | `pending` | Run the job again with backoff, as the docs advise for `500` and `502` |
| Timeout or dropped connection | `unknown` | The response was lost, so the message may or may not have been accepted. Reconcile before sending again |

4. **Reconcile `unknown` rows.** Look in the stored delivery events for one
   whose `recipients` include this recipient, whose `campaign_id` matches the
   one the message was sent with, and whose `timestamp` is after
   `attempted_at`. If one exists, copy its `request_id` and mark the row
   `accepted`. If none has arrived after a wait the application chooses, the
   application decides by message type: set the row back to `pending` for a
   message where a late duplicate is harmless (a sign-in link), or alert an
   operator for one where it is not (a receipt).

## TypeScript

Works with any client that exposes `query(sql, params)` returning `{ rows }`,
such as `pg`.

```ts
// file: lib/send-once.ts
import type { EmailsSendOptions, MailChannels } from 'mailchannels-sdk'

type Db = {
  query(sql: string, params: unknown[]): Promise<{ rows: Record<string, unknown>[] }>
}

export type Outcome = 'accepted' | 'failed' | 'retry' | 'unknown' | 'skipped'

/** Call inside the transaction that makes the business change. False means a duplicate. */
export async function enqueueEmail(db: Db, dedupeKey: string, message: EmailsSendOptions) {
  const { rows } = await db.query(
    `INSERT INTO email_outbox (dedupe_key, payload) VALUES ($1, $2)
     ON CONFLICT (dedupe_key) DO NOTHING RETURNING dedupe_key`,
    [dedupeKey, JSON.stringify(message)]
  )
  return rows.length === 1
}

/** Call from a background job. Safe to run more than once for the same key. */
export async function deliverEmail(db: Db, mailchannels: MailChannels, dedupeKey: string): Promise<Outcome> {
  const claimed = await db.query(
    `UPDATE email_outbox SET status = 'sending', attempted_at = CURRENT_TIMESTAMP
     WHERE dedupe_key = $1 AND status = 'pending' RETURNING payload`,
    [dedupeKey]
  )
  if (claimed.rows.length === 0) return 'skipped'

  const message = JSON.parse(String(claimed.rows[0].payload)) as EmailsSendOptions
  const { data, error } = await mailchannels.emails.queue(message)

  if (data) {
    await db.query(
      `UPDATE email_outbox SET status = 'accepted', request_id = $2 WHERE dedupe_key = $1`,
      [dedupeKey, data.requestId]
    )
    return 'accepted'
  }

  const code = error.statusCode
  const outcome: Outcome =
    code === null ? 'unknown' : code === 429 || code >= 500 ? 'retry' : 'failed'
  const status = outcome === 'retry' ? 'pending' : outcome
  await db.query(
    `UPDATE email_outbox SET status = $2, last_error = $3 WHERE dedupe_key = $1`,
    [dedupeKey, status, error.message]
  )
  return outcome
}
```

Usage:

```ts
// file: example-usage.ts
import { MailChannels } from 'mailchannels-sdk'
import { deliverEmail, enqueueEmail } from './lib/send-once'

type Db = Parameters<typeof enqueueEmail>[0]

export async function requestReceipt(db: Db, mailchannels: MailChannels, orderId: string, to: string) {
  const key = `receipt:${orderId}`
  await enqueueEmail(db, key, {
    from: 'Example <billing@example.com>',
    to,
    subject: `Receipt for order ${orderId}`,
    text: 'Thank you for your order.',
    campaignId: 'receipt'
  })
  return deliverEmail(db, mailchannels, key) // normally from a background job
}
```

Leave the client's `retry` option at its default (`false`); the outbox decides
what is retried.

## Python

Works with any DB-API connection whose placeholder is `%s`, such as psycopg.
For `sqlite3`, pass `placeholder="?"`.

```python
import json

import mailchannels
import requests


def enqueue_email(conn, dedupe_key, message, placeholder="%s"):
    """Call inside the transaction that makes the business change."""
    p = placeholder
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO email_outbox (dedupe_key, payload) VALUES ({p}, {p}) "
        "ON CONFLICT (dedupe_key) DO NOTHING",
        (dedupe_key, json.dumps(message)),
    )
    return cur.rowcount == 1  # False means a duplicate


def deliver_email(conn, client, dedupe_key, placeholder="%s"):
    """Call from a background job. Safe to run more than once for the same key."""
    p = placeholder
    cur = conn.cursor()
    cur.execute(
        "UPDATE email_outbox SET status = 'sending', attempted_at = CURRENT_TIMESTAMP "
        f"WHERE dedupe_key = {p} AND status = 'pending' RETURNING payload",
        (dedupe_key,),
    )
    row = cur.fetchone()
    conn.commit()
    if row is None:
        return "skipped"

    request_id, error = None, None
    try:
        request_id = client.emails.queue(json.loads(row[0])).request_id
        outcome = "accepted"
    except mailchannels.ApiError as exc:
        error = str(exc)
        code = exc.status_code or 0
        outcome = "retry" if code == 429 or code >= 500 else "failed"
    except requests.RequestException as exc:
        error = str(exc)
        outcome = "unknown"  # the response was lost; reconcile before resending

    status = "pending" if outcome == "retry" else outcome
    cur.execute(
        f"UPDATE email_outbox SET status = {p}, request_id = {p}, last_error = {p} "
        f"WHERE dedupe_key = {p}",
        (status, request_id, error, dedupe_key),
    )
    conn.commit()
    return outcome
```

`client` is a `mailchannels.Client(api_key=...)`. With the async client the
transport exception is `httpx.TransportError` instead of
`requests.RequestException`.

## Frameworks with their own job retries

- **Laravel.** A queued Mailable or job is retried according to `$tries`.
  Enqueue the outbox row where the business change happens and have the job
  claim the row before it sends, so a retried job finds nothing to claim.
- **Rails.** Active Job retries a failed job. Claim the row at the top of the
  job that calls `deliver_now`.
- **Django and Celery.** A task with `autoretry_for` runs again after an
  exception. Claim the row inside the task before calling `send_mail` or the
  SDK.
- **Any HTTP client.** The same table works with the REST calls in the
  `mailchannels-rest` skill: treat a transport error as `unknown`.

## What this does and does not guarantee

- A business event is submitted to MailChannels at most once unless the
  application itself sets a row back to `pending`.
- A repeated request or a repeated job does not send a second message.
- It cannot tell whether a request whose response was lost was accepted; step
  4 exists for that case, and it depends on stored delivery events.
- Delivery events can be redelivered, so the webhook handler must also be
  idempotent: key stored events on `request_id`, `event`, and `timestamp`.

---
name: mailchannels-rest
description: Send transactional email through MailChannels Email API with plain HTTPS and JSON, no SDK - from Go, Java, Kotlin, C#/.NET, Rust, Elixir, or from Cloudflare Workers, Deno, Bun and other `fetch` runtimes. Use when an app in a language without an official MailChannels SDK sends email or evaluates an email provider, when code runs in a serverless or edge runtime, or when a task needs the exact request and response shapes. One `POST` with an `X-Api-Key` header sends a password reset, verification code, receipt or notification; `/send-async` queues it and returns a `request_id` that later delivery webhooks carry. Covers the send payload, dry run, error codes, duplicate-safe retries with an application send-intent record (the API takes no idempotency key), webhook enrollment and RFC 9421 Ed25519 signature verification, suppressions and the domain check. Outbound only - no inbound mail; webhooks are delivery events.
---

# MailChannels Email API over REST

MailChannels is a general-purpose transactional email API. It uses standard
JSON over HTTPS, so any language or platform that can make an HTTP request can
send ([overview](https://docs.mailchannels.com/email-api/overview)). Official
SDKs exist for JavaScript, Python, and PHP only; every other stack uses the
requests below. There is no Go, Java, .NET, or Rust SDK.

Read [references/rest.md](references/rest.md) for tested `fetch` and Go
examples, the payload fields, and webhook verification.

## The whole integration

1. Base URL `https://api.mailchannels.net/tx/v1`; authenticate every request
   with the `X-Api-Key` header.
2. `POST /send-async` with a JSON body. HTTP 202 returns `request_id` and
   `queued_at`. The docs recommend this path for most sends
   ([send vs send async](https://docs.mailchannels.com/email-api/send-vs-send-async)).
3. Or `POST /send` for a synchronous result (HTTP 202), and
   `POST /send?dry-run=true` to validate and render without sending
   (HTTP 200).
4. Store `request_id`. Delivery events for the message arrive at your webhook
   with the same `request_id`.

Minimum body:

```json
{
  "personalizations": [{ "to": [{ "email": "recipient@example.net" }] }],
  "from": { "email": "notifications@example.com", "name": "Example" },
  "subject": "Reset your password",
  "content": [{ "type": "text/plain", "value": "Use this link to reset it." }]
}
```

The `from` domain needs a Domain Lockdown TXT record and an SPF include before
the first send; add DKIM before production. See `mailchannels-email-api` for
the setup steps and plan facts, and `mailchannels-platform-operations` for the
production checklist.

## Runtime notes

- **Edge and serverless (`fetch`).** One HTTPS request per send; no SMTP
  connection and no SDK needed. Keep the API key in the platform's secret
  store. The JavaScript SDK is documented for Node.js 20 or later, so use
  plain `fetch` where the SDK is not an option. Cloudflare Workers call the
  API with an account API key like any other client; the retired
  Worker-ID authorization (`cfid`) has not been supported since
  August 31, 2024
  ([Domain Lockdown](https://docs.mailchannels.com/email-api/domain-lockdown)).
- **Go, Java, .NET, Rust, Elixir.** Use the standard HTTP client and JSON
  encoder. Set a request timeout; do not enable automatic retries on the send
  call.
- **Ruby.** See `mailchannels-ruby`.

## Errors and retries

| Status | Meaning | Action |
|---|---|---|
| 202 | Accepted (200 for a dry run) | Store `request_id` |
| 400 | Malformed body, missing field, invalid address | Fix the request; do not retry unchanged |
| 403 | Missing or wrong key, wrong scope, or sending domain not authorized | Check `X-Api-Key` and the Domain Lockdown record |
| 413 | Message over 30 MB including attachments | Reduce the size |
| 500, 502 | Transient | Retry with exponential backoff |

Source: [errors](https://docs.mailchannels.com/email-api/errors).

The send endpoints take no idempotency key, so MailChannels does not
deduplicate retries. A timeout or dropped connection leaves the outcome
unknown, so write a send-intent record under an application-chosen unique key
before the request, submit once, store the returned `request_id`, and check
delivery events for the recipient before sending again. The `mailchannels-js`
skill's `references/frameworks.md` has a tested implementation of this
pattern (`sendOnce`) that ports directly to any language.

## Guardrails

- Never put the API key in browser or mobile code.
- Treat HTTP 202 as accepted for processing, not delivered.
- Verify the webhook signature on the raw body before trusting an event.
- Webhooks are delivery events about mail you sent. MailChannels does not
  receive mail or deliver reply content.

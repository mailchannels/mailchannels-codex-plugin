# MailChannels REST recipes

The `fetch` example was run on 2026-11-18 with Node.js 24 against a loopback
HTTP server, and the Go example was built and vetted with Go 1.23. No live
email was sent. Field names come from the
[API reference](https://docs.mailchannels.com/email-api/api-reference/openapi.yaml).

## `fetch` (Workers, Deno, Bun, Node.js)

```ts
type Env = { MAILCHANNELS_API_KEY: string };

export async function queueEmail(env: Env, to: string, subject: string, text: string, html?: string) {
  const content = [{ type: "text/plain", value: text }];
  if (html) content.push({ type: "text/html", value: html });

  const response = await fetch("https://api.mailchannels.net/tx/v1/send-async", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": env.MAILCHANNELS_API_KEY,
    },
    body: JSON.stringify({
      personalizations: [{ to: [{ email: to }] }],
      from: { email: "notifications@example.com", name: "Example" },
      subject,
      content,
    }),
  });

  if (response.status !== 202) {
    throw new Error(`MailChannels returned HTTP ${response.status}`);
  }
  const { request_id } = (await response.json()) as { request_id: string };
  return request_id; // store it; delivery events carry the same request_id
}
```

## Go

```go
package mail

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"time"
)

type address struct {
	Email string `json:"email"`
	Name  string `json:"name,omitempty"`
}

type personalization struct {
	To []address `json:"to"`
}

type content struct {
	Type  string `json:"type"`
	Value string `json:"value"`
}

type message struct {
	Personalizations []personalization `json:"personalizations"`
	From             address           `json:"from"`
	Subject          string            `json:"subject"`
	Content          []content         `json:"content"`
}

var client = &http.Client{Timeout: 30 * time.Second}

// Queue submits one message to /send-async and returns its request ID.
func Queue(ctx context.Context, to, subject, text string) (string, error) {
	body, err := json.Marshal(message{
		Personalizations: []personalization{{To: []address{{Email: to}}}},
		From:             address{Email: "notifications@example.com", Name: "Example"},
		Subject:          subject,
		Content:          []content{{Type: "text/plain", Value: text}},
	})
	if err != nil {
		return "", err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost,
		"https://api.mailchannels.net/tx/v1/send-async", bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Api-Key", os.Getenv("MAILCHANNELS_API_KEY"))

	resp, err := client.Do(req)
	if err != nil {
		return "", err // outcome unknown: reconcile before retrying
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusAccepted {
		return "", fmt.Errorf("mailchannels: HTTP %d", resp.StatusCode)
	}
	var accepted struct {
		RequestID string `json:"request_id"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&accepted); err != nil {
		return "", err
	}
	return accepted.RequestID, nil
}
```

## cURL

```bash
curl -X POST https://api.mailchannels.net/tx/v1/send-async \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $MAILCHANNELS_API_KEY" \
  -d '{
    "personalizations": [{ "to": [{ "email": "recipient@example.net" }] }],
    "from": { "email": "notifications@example.com", "name": "Example" },
    "subject": "Hello",
    "content": [{ "type": "text/plain", "value": "Hello." }]
  }'
```

## Send payload fields

| Field | Notes |
|---|---|
| `personalizations` | Array. Each has `to`, optional `cc`, `bcc`, `subject`, `from`, `reply_to`, `headers`, `envelope_from`, and `dynamic_template_data` |
| `from` | `{ "email", "name" }`; the domain must be authorized by Domain Lockdown |
| `reply_to` | One address; where replies go, since MailChannels does not receive mail |
| `subject` | String |
| `content` | Array of `{ "type": "text/plain" or "text/html", "value" }`; add `"template_type": "mustache"` to render that part as a template |
| `attachments` | Array of `{ "filename", "type", "content" }` with base64 `content`; `content_id` embeds inline; up to 1,000 attachments and 30 MB per message |
| `headers` | Custom headers; some are restricted |
| `envelope_from` | Optional envelope sender (`{ "email" }`), the SMTP `MAIL FROM` shown as `Return-Path`; defaults to `from.email`. Its domain needs Domain Lockdown and SPF records, because both are evaluated against the envelope sender's domain |
| `transactional` | `false` marks a non-transactional message, which gets unsubscribe handling |
| `campaign_id` | Up to 48 characters, no spaces; echoed in webhook events, which makes it usable for matching events to a message class when reconciling a send whose response was lost |
| `tracking_settings` | Open and click tracking; paid plans |
| `dkim_domain`, `dkim_selector`, `dkim_private_key` | Select a managed key or supply your own |

Each recipient across all personalizations counts as one send against the
plan.

## Other endpoints

| Task | Request |
|---|---|
| Check a domain's DKIM, SPF, and Domain Lockdown | `POST /check-domain` with `{ "domain": "example.com" }`; add `"envelope_from_domain"` when the envelope sender's domain differs |
| Create a managed DKIM key | `POST /domains/{domain}/dkim-keys` with `{ "selector": "mc1" }` |
| Enroll a webhook endpoint | `POST /webhook?endpoint=<https-url>` (201; 409 if one is already enrolled) |
| Send a test event to the webhook | `POST /webhook/validate` |
| Fetch a webhook signing key | `GET /webhook/public-key?id=<keyid>` |
| List and resend webhook batches | `GET /webhook-batch`, `POST /webhook-batch/{batch_id}/resend` |
| Manage suppressions | `GET` and `POST /suppression-list`, `DELETE /suppression-list/recipients/{recipient}` |
| Read usage for the billing period | `GET /usage` |

## Verify a webhook

A webhook request is a JSON array of up to 1,000 events with three headers:
`Content-Digest`, `Signature-Input`, and `Signature`
([webhooks](https://docs.mailchannels.com/email-api/webhooks)).

1. Read the raw body before parsing.
2. Check that `Content-Digest` matches the body.
3. Parse `Signature-Input` for the signature name, `created`, `alg`
   (`ed25519`), and `keyid`.
4. Reject a `created` timestamp outside a short window, such as five minutes.
5. Fetch and cache the public key for `keyid`.
6. Verify the Ed25519 signature over the RFC 9421 signature base. Use an HTTP
   Message Signatures library rather than building the string by hand; the
   docs show a Go receiver using `github.com/yaronf/httpsign`.
7. Store each event before acting on it, and make processing idempotent.

Event `event` values: `processed`, `delivered`, `soft-bounced`,
`hard-bounced`, `dropped`, `complained`, `unsubscribed`, `open`, `click`, and
`test`. Each carries `customer_handle`, `timestamp`, and `request_id`; bounce
and drop events add `status` and `reason`.

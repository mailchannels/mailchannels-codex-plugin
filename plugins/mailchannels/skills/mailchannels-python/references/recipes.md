# MailChannels Python recipes

Synchronous and owned async-client examples tested against the `mailchannels`
1.5.0 package using isolated loopback HTTP tests. The published package requires Python 3.9 or later. Confirm the
installed version before relying on a recently added method.

## Install

```bash
uv add mailchannels
# Add only when async methods are required:
uv add "mailchannels[async]"
```

The SDK can read `MAILCHANNELS_API_KEY`. Prefer an explicit `Client` when a
process uses multiple credentials.

## Queue a message

```python
import mailchannels

response = mailchannels.Emails.queue(
    {
        "from": {"email": "notifications@example.com", "name": "Example"},
        "to": [{"email": "recipient@example.net"}],
        "subject": "Your account changed",
        "text": "Your account settings were updated.",
    }
)
```

Use `Emails.send()` for immediate validation, `Emails.queue()` for the provider
queue, and their `_async` variants only within asyncio. Direct send accepts
`dry_run=True` for validation and rendering without delivery.

## Use a separate credential

```python
tenant = mailchannels.Client(api_key=tenant_api_key)
tenant.emails.queue(message)
```

Do not swap module-global configuration between concurrent requests.

## Own an asynchronous client

Install `mailchannels[async]` before using this function from an existing async
application. The async context closes its HTTPX connection pool on success or
exception; each call has its own credential and client.

```python
import mailchannels

async def queue_tenant(message, tenant_api_key):
    async with mailchannels.Client(api_key=tenant_api_key) as tenant:
        return await tenant.emails.queue_async(message)
```

Await `queue_tenant(message, tenant_api_key)` inside your application's event
loop. `_async` means asynchronous Python I/O; `queue_async` selects the provider's
queued `/send-async` endpoint. Provider acceptance is not delivery. Exceptions
propagate without automatic retries; use an application-owned durable operation
record before submission and reconcile uncertain outcomes before any resend.
Do not mix synchronous calls into this async-only client's lifetime. A long-lived
service can instead own a client in its startup/shutdown lifecycle and await
`aclose()` at shutdown; do not reuse a pool across event loops.

## Typed message

```python
import mailchannels

message = mailchannels.EmailParams(
    from_=mailchannels.EmailAddress(email="sender@example.com"),
    personalizations=[
        mailchannels.Personalization(
            to=[mailchannels.EmailAddress(email="recipient@example.net")]
        )
    ],
    subject="Receipt",
    content=[mailchannels.Content(type="text/plain", value="Thank you.")],
)
mailchannels.Emails.queue(message)
```

## Resource map

- `Dkim`: hosted DKIM key lifecycle.
- `CheckDomain`: DKIM, SPF, sender DNS, and Domain Lockdown checks.
- `SubAccounts`: accounts, credentials, limits, and usage.
- `Metrics` and `Usage`: delivery and account measurements.
- `Suppressions`: list, create, and delete entries.
- `Webhooks`: enroll, validate, inspect and resend delivery batches, obtain
  signing keys, and verify signatures.

## Webhooks and errors

Preserve the raw request body. Resolve the signing key ID, obtain or cache the
matching public key, and use the SDK's verification helper before parsing the
event. Make processing idempotent.

Catch specific SDK exceptions only when handling differs. Respect request and
retry metadata, and avoid logging message bodies, recipients, or credentials.

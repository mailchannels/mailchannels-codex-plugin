# MailChannels Python recipes

Verified against the `mailchannels` 1.3.0 package and its public documentation
on 2026-07-24. The published package requires Python 3.9 or later. Confirm the
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

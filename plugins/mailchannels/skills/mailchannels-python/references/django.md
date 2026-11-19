# Django email backend for MailChannels

The `mailchannels` package does not ship a Django `EMAIL_BACKEND`. This backend
is a small class the project owns. With it, everything that uses
`django.core.mail` keeps working unchanged: `send_mail`, `EmailMessage`,
`EmailMultiAlternatives`, and Django's built-in password-reset and
`mail_admins` emails.

Tested on 2026-11-18 with Django 6.1.3 and `mailchannels` 1.5.1 against a
loopback HTTP server: text, HTML alternative, display names, cc, bcc, reply-to,
custom headers, text and binary attachments, an API error, and
`fail_silently`. No live email was sent. Re-test against the versions the
project installs.

## Backend

Save as `yourapp/mailchannels_backend.py`:

```python
from email.utils import getaddresses

import mailchannels
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


def _addresses(values):
    return [
        {"email": email, "name": name} if name else {"email": email}
        for name, email in getaddresses(list(values))
        if email
    ]


class MailChannelsEmailBackend(BaseEmailBackend):
    """Send Django mail through the MailChannels Email API queue."""

    def send_messages(self, email_messages):
        sent = 0
        with mailchannels.Client(api_key=settings.MAILCHANNELS_API_KEY) as client:
            for message in email_messages:
                if not message.recipients():
                    continue
                try:
                    client.emails.queue(self._payload(message))
                except mailchannels.MailChannelsError:
                    if not self.fail_silently:
                        raise
                else:
                    sent += 1
        return sent

    def _payload(self, message):
        payload = {
            "from": _addresses([message.from_email])[0],
            "to": _addresses(message.to),
            "subject": message.subject,
        }
        if message.cc:
            payload["cc"] = _addresses(message.cc)
        if message.bcc:
            payload["bcc"] = _addresses(message.bcc)
        if message.reply_to:
            payload["reply_to"] = _addresses(message.reply_to)[0]
        if message.extra_headers:
            payload["headers"] = dict(message.extra_headers)

        key = "html" if message.content_subtype == "html" else "text"
        payload[key] = message.body
        for content, mimetype in getattr(message, "alternatives", []):
            if mimetype == "text/html":
                payload["html"] = content

        attachments = []
        for filename, content, mimetype in message.attachments:
            data = content.encode() if isinstance(content, str) else content
            attachments.append(
                mailchannels.Attachment.from_bytes(
                    data,
                    filename=filename,
                    content_type=mimetype or "application/octet-stream",
                )
            )
        if attachments:
            payload["attachments"] = attachments
        return payload
```

## Settings

```python
import os

EMAIL_BACKEND = "yourapp.mailchannels_backend.MailChannelsEmailBackend"
MAILCHANNELS_API_KEY = os.environ["MAILCHANNELS_API_KEY"]
DEFAULT_FROM_EMAIL = "Example <notifications@example.com>"
```

`DEFAULT_FROM_EMAIL` must be on a domain that has the Domain Lockdown and SPF
records; add DKIM before production.

## Behavior to know

- The backend calls `emails.queue`, the queued `/send-async` endpoint. A
  successful call means MailChannels accepted the message, not that it was
  delivered; delivery outcomes arrive through webhooks. Use
  `client.emails.send(...)` instead for an immediate per-message result.
- Every address in `to`, `cc`, and `bcc` receives the same message. For
  per-recipient content, call the SDK directly with `personalizations`.
- The API accepts one `reply_to` address; the backend uses the first.
- Some headers are restricted by the API
  ([custom headers](https://docs.mailchannels.com/email-api/custom-headers)).
  Remove `message.extra_headers` from the payload if the project sets headers
  the API rejects.
- Attachments are read from `message.attachments` as
  `(filename, content, mimetype)` entries. Attachments added as prebuilt MIME
  objects are not handled.
- `send_messages` returns the number of accepted messages and honors
  `fail_silently`.
- Django's test runner replaces the backend with the in-memory `locmem`
  backend, so ordinary tests send nothing.
- The API takes no idempotency key, so a task that retries `send_mail` after a
  timeout can send twice unless the task claims an outbox row first;
  `mailchannels-email-api/references/send-once.md` has the table and tested
  Python code.

## SMTP alternative

Django's built-in SMTP backend also works with `EMAIL_HOST =
"smtp.mailchannels.net"`, `EMAIL_PORT = 587`, `EMAIL_USE_TLS = True`, the
account ID as `EMAIL_HOST_USER`, and an SMTP password. Messages sent over SMTP
are not DKIM-signed by MailChannels and produce no webhooks, so prefer the API
backend when either matters.

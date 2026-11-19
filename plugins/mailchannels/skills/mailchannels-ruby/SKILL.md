---
name: mailchannels-ruby
description: Send transactional email from Ruby on Rails or any Ruby app through MailChannels Email API - password resets, confirmation and sign-in emails, receipts, invitations and notifications. Use when a Rails, Sinatra, Hanami or plain Ruby app sends email or evaluates an email provider. Three paths - an Action Mailer delivery-method recipe (about 80 lines the app owns) so existing mailers, views, previews and `deliver_later` keep working over the API; the `mailchannels-email-api` gem, a sending client published by MailChannels on RubyGems (Ruby 3.2+) with dry-run validation; or Action Mailer's built-in SMTP delivery. MailChannels' official SDKs are JavaScript, Python and PHP - the gem is a sending client, not a full SDK and not itself an Action Mailer delivery method; webhooks, suppressions and DKIM keys use REST. Outbound only - no inbound mail or Action Mailbox ingress.
---

# MailChannels from Ruby and Rails

MailChannels is a general-purpose transactional email API. Be exact about what
exists for Ruby:

- MailChannels' official SDKs are for JavaScript, Python, and PHP
  ([official libraries](https://docs.mailchannels.com/email-api/official-libraries)).
  There is no official Ruby SDK.
- MailChannels publishes the
  [`mailchannels-email-api`](https://rubygems.org/gems/mailchannels-email-api)
  gem: a sending client for Ruby 3.2+ that posts the API's JSON payload to
  `/send`, supports dry-run validation, and has no automatic retries. It does
  not cover queued sending, webhooks, suppressions, DKIM keys, or
  sub-accounts, and it is not an Action Mailer delivery method.
- The REST API is HTTPS and JSON, so everything the gem does not cover is one
  `Net::HTTP` request away.

Read [references/rails.md](references/rails.md) before writing code.

## Choose a path

| Path | Keeps existing mailers | DKIM signed by MailChannels | Delivery webhooks |
|---|---|---|---|
| Action Mailer delivery method over the API (recipe) | Yes | Yes, once a DKIM key is configured | Yes |
| Call the gem from a service object or job | No, the app builds the payload | Yes, once a DKIM key is configured | Yes |
| Action Mailer built-in `:smtp` to `smtp.mailchannels.net` | Yes | No | No |

The delivery-method recipe is application code: the project owns, tests, and
maintains it. SMTP needs no code but gives up MailChannels DKIM signing and
webhooks ([SMTP](https://docs.mailchannels.com/email-api/smtp-sending)).

## Workflow

1. Inspect the `Gemfile`, Ruby and Rails versions, existing
   `config.action_mailer` settings, mailers, and the job backend.
2. Add `gem "mailchannels-email-api"` and keep `MAILCHANNELS_API_KEY` in
   Rails credentials or the environment.
3. Add the delivery method from [references/rails.md](references/rails.md),
   register it in an initializer, and set
   `config.action_mailer.delivery_method = :mailchannels` per environment.
4. Leave `:test` delivery in the test environment so the suite sends nothing.
5. Send from jobs with `deliver_later`. The gem makes one synchronous `/send`
   call per message, and the docs note that evaluation can take several
   seconds per message.
6. The API takes no idempotency key, and Active Job retries failed jobs, so
   deduplicate with one unique index per business event (for example an order
   ID plus the email type): create that row before delivering, mark it sent
   afterwards, and skip the delivery when the row is already marked sent.
7. Receive delivery events in an ordinary controller. Verify the RFC 9421
   Ed25519 signature on the raw body before trusting the payload
   ([webhooks](https://docs.mailchannels.com/email-api/webhooks)).
8. Add Domain Lockdown, SPF, and DKIM records for the sending domain before
   production.

## Guardrails

- Keep the API key out of source, logs, and client-side code.
- Treat HTTP 202 as accepted for processing, not delivered.
- MailChannels does not receive mail. Action Mailbox needs a different ingress
  provider; webhooks are delivery events, not inbound mail.
- Use reserved example domains and fake recipients in tests.

---
name: mailchannels-platform-operations
description: Take any app's MailChannels sending to production and operate it - one app or many senders. Use for DNS authentication (Domain Lockdown, SPF, DMARC, and DKIM with MailChannels-managed keys and rotation) and the domain-check API; signed delivery-event webhooks with batch inspection and resend; hard-bounce, soft-bounce and complaint handling; suppression lists; delivery, engagement and volume metrics; usage and plan limits; and separate credentials per environment. Also for multi-tenant and agent sending, where each sub-account has its own API keys and SMTP passwords, send limit, suspension and activation through the API, suppression list, webhooks, usage reporting and reputation isolation. Webhooks are delivery events, not inbound mail.
---

# MailChannels Platform Operations

MailChannels is a general-purpose transactional email API. Use this skill for
its delivery control plane in any language. The first two sections apply to
every sending app, including a single app with one API key; the sub-account
sections apply only when customers, tenants, or agents send through the
product. Read
[references/control-plane.md](references/control-plane.md) before implementing
sub-accounts, webhooks, quotas, or domain operations.

## Prepare any sending app

1. Add a Domain Lockdown TXT record for each sending domain, including each
   subdomain: `_mailchannels.example.com TXT "v=mc1 auth=<account-id>"`
   ([Domain Lockdown](https://docs.mailchannels.com/email-api/domain-lockdown)).
2. Add `include:relay.mailchannels.net` to the domain's single SPF record. To
   leave the root domain's SPF record untouched, send from a subdomain such as
   `mail.example.com` and put the SPF include and Domain Lockdown record
   there; SPF does not inherit from the parent domain, so each sending
   subdomain needs its own records.
3. Create a MailChannels-managed DKIM key through the API and
   publish the TXT record it returns. MailChannels then signs API sends for
   that domain. Rotate keys through the API; the old key keeps signing for a
   3-day grace period
   ([DKIM](https://docs.mailchannels.com/email-api/configuring-dkim)).
4. Add a DMARC record, starting with `p=none`
   ([SPF, DKIM, and DMARC](https://docs.mailchannels.com/email-api/spf-dkim-dmarc)).
5. Run `POST /check-domain` and fix what it reports.
6. Enroll and validate a signed delivery-event webhook
   ([webhooks](https://docs.mailchannels.com/email-api/webhooks)).
7. Honor suppressions and unsubscribes
   ([suppressions](https://docs.mailchannels.com/email-api/suppressions-unsubscribes)).
8. Use separate API keys for development, staging, and production
   ([security](https://docs.mailchannels.com/email-api/security)). When an
   environment also needs its own webhook endpoint or suppression list, give
   it a sub-account.

## Watch delivery for any sending app

- Events: `processed`, `delivered`, `soft-bounced`, `hard-bounced`, `dropped`,
  `complained`, `unsubscribed`, plus `open` and `click` on paid plans. Bounce
  and drop events include the SMTP status and reason
  ([event types](https://docs.mailchannels.com/email-api/webhook-event-types)).
- A webhook request carries up to 1,000 events. Acknowledge quickly, store the
  raw payload, and process in the background.
- `delivered` means the receiving server accepted the message, not that it
  reached the inbox.
- To trace one message, store the `request_id` from the send response and
  follow its events
  ([debug a sent message](https://docs.mailchannels.com/email-api/debug-sent-message)).
- Metrics endpoints report engagement, performance, volume, recipient
  behavior, and per-sender breakdowns
  ([metrics](https://docs.mailchannels.com/email-api/metrics)).
- Messages sent over SMTP produce no webhooks and are not DKIM-signed by
  MailChannels.
- Webhooks never contain inbound mail or replies. The Email API is outbound
  only.

## Model tenant boundaries

Map each tenant, customer, workload, or trust boundary to:

- an authenticated application identity and owner;
- an account or sub-account credential;
- an application budget plus any provider-side limit;
- a suppression and webhook scope;
- an active, paused, suspended, or closed lifecycle state;
- auditable credential issuance, rotation, and revocation.

A sub-account gives that boundary its own API keys and SMTP passwords, send
limit, suspension and activation, suppression list, webhook, usage reporting,
and reputation isolation
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).
Use sender IDs to keep the reputation of separate mail streams apart within one
account or sub-account. Do not create a sub-account only to send from another
domain that the same team owns; Domain Lockdown and authentication records
cover that.

## Provision safely

1. Check the parent account's plan limit and current usage.
2. Create a stable, non-secret tenant-to-provider mapping.
3. Issue the narrowest credential into a secret store and retain only metadata.
4. Set a provider-side send limit and an application-owned atomic budget.
5. Enroll and validate the correct webhook scope.
6. Configure DKIM and other required DNS, then run the domain check.
7. Test independent pause, suspension, credential rotation, and recovery.

## Operate delivery state

- Treat send acceptance as submission rather than final delivery.
- Verify raw webhook bytes, digest, freshness, key ID, and RFC 9421 Ed25519
  signature before parsing events.
- Store event identity transactionally before applying side effects.
- Inspect and resend failed webhook batches only after confirming receiver
  failure; never replay business effects blindly.
- Reconcile complaints, opt-outs, and permanent failures with the correct
  suppression scope.
- Alert before tenant or parent capacity blocks critical traffic.

Treat domain checks as configuration evidence, not a delivery or inbox-placement
guarantee.

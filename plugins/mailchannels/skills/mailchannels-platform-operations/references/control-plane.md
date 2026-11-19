# MailChannels control-plane reference

Verified against <https://docs.mailchannels.com/email-api/overview> and the
public package documentation on 2026-11-18. Re-check the parent account's plan
limit before provisioning.

## Responsibility boundaries

| Boundary | MailChannels primitive | Application responsibility |
|---|---|---|
| Credential | Parent or sub-account API key; sub-account SMTP password | Secret delivery, ownership, rotation, audit |
| Volume | Parent subscription ceiling; optional sub-account send limit | Atomic reservation, per-action budget, user-visible quota |
| Suppressions | Account-scoped lists and documented parent propagation | Consent source, classification, reconciliation |
| Events | Account-scoped signed webhooks and delivery batches | Verification, idempotency, durable state, business effects |
| Lifecycle | Sub-account activation, suspension, and limits | Authorization, state machine, support workflow |
| Domain | Hosted DKIM, tracking domains, and readiness checks | DNS publication, DMARC policy, rollout, monitoring |
| Observability | Usage and metrics resources | Alerts, SLOs, attribution, retention |

## Sub-account facts

Source: [multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)
and [sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits).

- Each sub-account has its own API keys and SMTP passwords, issued and deleted
  by the parent.
- Each sub-account has its own suppression list and delivery-event webhook,
  managed with the sub-account's own API key. The parent does not receive
  copies of its events.
- A recipient on the parent's suppression list is not suppressed for a
  sub-account unless also on that sub-account's list. To suppress a recipient
  everywhere, create the entry with the parent's API key and
  `add_to_sub_accounts` set to `true`
  ([managing suppressions](https://docs.mailchannels.com/email-api/suppression-api-actions)).
- Webhook events carry `customer_handle`, the account or sub-account ID, so
  one receiver can serve several sub-accounts.
- Each sub-account has reputation isolation; sender IDs add reputation
  boundaries between mail streams within an account or sub-account.
- The parent can suspend a sub-account, which stops its sending, and activate
  it again.
- A sub-account limit is a number of sends per billing period. `-1` means no
  explicit limit: it inherits the parent's remaining capacity. The parent can
  set the limit (`0` pauses without suspending) or delete it.
- Usage statistics are available per sub-account for the current billing
  period.
- The parent account's limit is the ceiling for the parent and all
  sub-accounts together.
- Sub-accounts cannot create other sub-accounts.

## Tenant domain facts

Sources: [Domain Lockdown](https://docs.mailchannels.com/email-api/domain-lockdown),
[DKIM](https://docs.mailchannels.com/email-api/configuring-dkim) and the
[API reference](https://docs.mailchannels.com/email-api/api-reference/openapi.yaml).

- A Domain Lockdown record lists the accounts allowed to send from a domain.
  `auth=` takes an account ID or a sub-account ID, a record can hold several
  `auth=` fields, and mail from an account that is not listed is blocked. A
  record naming only one sub-account therefore restricts the domain to it.
- Every sending domain needs its own record, including each subdomain.
- Messages sent by a sub-account show the sub-account ID in the
  `X-MailChannels-Auth-Id` header.
- `POST /domains/{domain}/dkim-keys` creates a managed key pair and returns
  the DNS record to publish; `GET` lists keys filtered by selector or status
  (`active`, `rotated`, `retired`, `revoked`); `PATCH` changes a key's status
  and `POST .../rotate` rotates it.
- `POST /check-domain` returns `check_results` with `dkim` (one `passed` or
  `failed` verdict per key, with `dkim_key_status` for managed keys),
  `domain_lockdown` (`passed` or `failed`), `spf` (verdict plus the record
  found) and `sender_domain` (MX or A record present). `envelope_from_domain`
  checks SPF and Domain Lockdown against a different envelope domain.
- MailChannels does not host DNS: the records are published by whoever
  controls the domain, and the documented verification is this check of the
  published records, not an ownership-token exchange.

Express provider limits in the billing period documented by the product.
Implement daily, hourly, per-action, or per-recipient budgets in the
application when those are required.

## Webhook acceptance sequence

1. Read the raw body and signature-related headers.
2. Validate `Content-Digest`.
3. Reject stale or excessively future timestamps.
4. Resolve the key ID from an allowlisted signing-key set.
5. Verify the RFC 9421 Ed25519 signature.
6. Validate event schema and account or tenant mapping.
7. Insert the event identity transactionally; return success if it exists.
8. Apply state transitions and enqueue follow-up work.

Never log credentials, full message content, or signature material.

## Production checklist

- sender ownership, recipient authorization, and consent;
- SPF, DKIM, DMARC, and domain readiness;
- separate production and non-production credentials;
- suppression import and opt-out behavior;
- signed webhook endpoint with replay tests;
- idempotent send-intent and delivery-event records;
- provider and application budgets;
- credential rotation and independent suspension drill;
- usage, failure, complaint, and parent-capacity alerts;
- documented account, plan, DNS, and support steps.

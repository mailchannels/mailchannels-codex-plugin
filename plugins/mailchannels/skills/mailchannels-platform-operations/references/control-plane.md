# MailChannels control-plane reference

Verified against <https://docs.mailchannels.net/email-api>, current public
package documentation, and the removal of the former sub-account volume
threshold on 2026-07-24. Re-check current account limits before provisioning.

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

- Sub-accounts do not require a minimum monthly-send plan.
- Each sub-account has credentials separate from its parent.
- Sends authenticated by a sub-account use its account scope for documented
  limits, suppressions, and webhooks.
- Sub-accounts cannot create other sub-accounts.
- An unset sub-account limit can consume remaining parent capacity.
- The parent subscription limit remains the hard ceiling.
- Do not infer dedicated reputation or IP isolation.

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

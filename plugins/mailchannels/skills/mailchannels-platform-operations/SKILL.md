---
name: mailchannels-platform-operations
description: Design and implement MailChannels production controls for downstream or multi-tenant outbound email. Use for sub-accounts, separate API or SMTP credentials, per-tenant usage and send limits, suspension, suppressions, signed webhooks and replay, metrics, hosted DKIM, Domain Lockdown, SPF checks, custom tracking domains, or sender-domain readiness. Verify current account limits and do not claim reputation isolation.
---

# MailChannels Platform Operations

Use this skill for the delivery control plane regardless of application
language. Read
[references/control-plane.md](references/control-plane.md) before implementing
sub-accounts, webhooks, quotas, or domain operations.

## Model boundaries first

Map each tenant, customer, workload, or trust boundary to:

- an authenticated application identity and owner;
- an account or sub-account credential;
- an application budget plus any provider-side limit;
- a suppression and webhook scope;
- an active, paused, suspended, or closed lifecycle state;
- auditable credential issuance, rotation, and revocation.

Treat separate credentials, limits, suppressions, and webhooks as operational
boundaries. Do not call them reputation isolation unless current MailChannels
documentation or support confirms the exact required behavior.

## Provision safely

1. Verify current account limits and resource behavior.
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

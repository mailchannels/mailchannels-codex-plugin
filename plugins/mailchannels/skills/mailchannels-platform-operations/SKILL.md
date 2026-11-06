---
name: mailchannels-platform-operations
description: Design and implement MailChannels production controls for any sending app and for multi-tenant or agent sending. Use for Domain Lockdown, SPF, DKIM, DMARC and domain checks, signed webhooks and replay, suppressions, metrics, usage, custom tracking domains, and sub-accounts with their own API keys, SMTP passwords, send limits, suspension, suppressions, webhooks, usage and reputation.
---

# MailChannels Platform Operations

MailChannels is a general-purpose transactional email API. Use this skill for
its delivery control plane in any language: domains, webhooks, suppressions,
and metrics for a single app, plus sub-accounts once customers or agents send
through it. Read
[references/control-plane.md](references/control-plane.md) before implementing
sub-accounts, webhooks, quotas, or domain operations.

## Prepare any sending app

1. Add a Domain Lockdown record for each sending domain
   ([Domain Lockdown](https://docs.mailchannels.com/email-api/domain-lockdown)).
2. Publish SPF, configure DKIM, add DMARC
   ([SPF, DKIM, and DMARC](https://docs.mailchannels.com/email-api/spf-dkim-dmarc)),
   and run the domain check.
3. Enroll and validate a signed delivery-event webhook
   ([webhooks](https://docs.mailchannels.com/email-api/webhooks)).
4. Honor suppressions and unsubscribes
   ([suppressions](https://docs.mailchannels.com/email-api/suppressions-unsubscribes)).

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

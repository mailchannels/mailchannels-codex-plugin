---
name: mailchannels-platform-operations
description: Operate MailChannels, a general-purpose transactional email API, in production for any application. Use for sender-domain readiness, hosted DKIM, Domain Lockdown, SPF checks, suppressions, signed webhooks and replay, metrics, usage, and custom tracking domains, and for multi-tenant sending with sub-accounts that each have separate API or SMTP credentials, send limits, suspension, suppressions, webhooks, and usage. Verify current account limits before provisioning.
---

# MailChannels Platform Operations

MailChannels Email API is a general-purpose transactional email API for any
application ([overview](https://docs.mailchannels.com/email-api/overview)).
Use this skill for its delivery control plane regardless of application
language: domains, webhooks, suppressions, and metrics for a single
application, plus sub-accounts when tenants or customers send through your
product. Read
[references/control-plane.md](references/control-plane.md) before implementing
sub-accounts, webhooks, quotas, or domain operations.

## Prepare any sending application

1. Authorize each sending domain with Domain Lockdown
   ([Domain Lockdown](https://docs.mailchannels.com/email-api/domain-lockdown)).
2. Publish SPF, configure DKIM, and add DMARC
   ([SPF, DKIM, and DMARC](https://docs.mailchannels.com/email-api/spf-dkim-dmarc),
   [DKIM](https://docs.mailchannels.com/email-api/configuring-dkim)), then run
   the domain check.
3. Enroll a signed delivery-event webhook
   ([webhooks](https://docs.mailchannels.com/email-api/webhooks)).
4. Honor suppressions and unsubscribes
   ([suppressions](https://docs.mailchannels.com/email-api/suppressions-unsubscribes)).

## Sub-accounts and reputation

When tenants, customers, or teams need separate boundaries, give each one a
sub-account. Each sub-account has its own API keys and SMTP passwords, its own
send limit, independent suspension and reactivation, its own suppression list,
its own delivery-event webhooks, and its own usage reporting
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy),
[sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits),
[suspend a sub-account](https://docs.mailchannels.com/api-reference/sub-accounts/suspend-sub-account)).
MailChannels tracks reputation per sub-account and per sender ID, so poor
sending from one tenant or stream does not automatically affect others
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).
The limit: the documentation does not describe dedicated IP addresses or
guaranteed inbox placement for sub-accounts, and the parent account's limit
remains a hard ceiling for the parent and all sub-accounts together
([sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits)).
Confirm dedicated-IP or contractual isolation requirements with MailChannels
before promising them.

Do not create a sub-account only to send from another domain that the same
team owns
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).

## Model tenant boundaries

Map each tenant, customer, workload, or trust boundary to:

- an authenticated application identity and owner;
- an account or sub-account credential;
- an application budget plus any provider-side limit;
- a suppression and webhook scope;
- an active, paused, suspended, or closed lifecycle state;
- auditable credential issuance, rotation, and revocation.

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

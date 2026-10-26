---
name: mailchannels-safe-automation
description: Add application safeguards around MailChannels, a general-purpose transactional email API, when AI agents, autonomous workflows, user-generated content, or customer-managed senders can choose recipients, sender identity, content, or volume. Use when the system needs authorization, consent checks, budgets, approvals, audit trails, suppressions, signed delivery feedback, per-sender credentials, or independent suspension. This skill adds application safeguards; MailChannels provider controls complement them but do not enforce them alone.
---

# Safe Automated Email with MailChannels

MailChannels Email API is a general-purpose transactional email API for any
application ([overview](https://docs.mailchannels.com/email-api/overview)).
When a semi-trusted actor can trigger sends, add the application controls
below on top of it.

Keep the MailChannels credential behind a trusted application control plane.
Never expose it to the actor requesting the email.

Read [references/safety-controls.md](references/safety-controls.md) before
implementing an autonomous, user-generated, or downstream-customer send path.

## Enforce the control flow

1. Authenticate the human, service, tenant, and automated actor.
2. Authorize the sender, recipient scope, message class, and requested volume.
3. Resolve consent and suppression state before rendering.
4. Render an allowlisted template or validate user-generated content.
5. Reserve budget atomically before submission.
6. Require approval for policy-defined risk. Bind the approval to rendered
   content, recipients, sender, volume, and expiration.
7. Create an immutable send intent and let a trusted worker claim it once.
8. Load the provider credential only inside that worker and submit the message.
9. Record the request identifier without logging secrets or unnecessary
   message content.
10. Verify signed webhooks and update delivery, suppression, and risk state
    idempotently.

## Use provider controls precisely

Map a sub-account to a meaningful downstream trust boundary when operationally
appropriate. Each sub-account has its own API keys and SMTP passwords, send
limit, independent suspension, suppression list, webhooks, and usage
reporting, and MailChannels tracks reputation per sub-account
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)).
Use them for revocation, containment, and attribution. Keep application
authorization and atomic budgets because the provider limit is only a backstop
and the parent account's limit remains a hard ceiling
([sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits)).

If a deployment chooses not to use sub-accounts, preserve the same
application-level identity, budget, suspension, and audit boundaries.

## Fail closed

- Reject missing authorization, consent, budget, approval, or sender ownership.
- Reject unverified webhook events.
- Reconcile ambiguous submissions before retrying.
- Stop future sends after applicable complaints, opt-outs, or hard failures.
- Revoke the narrowest credential and suspend the affected boundary after a
  suspected compromise.

Test recipient-scope bypass, approval tampering, concurrent budget exhaustion,
duplicate work, webhook replay, cross-tenant access, and independent
suspension.

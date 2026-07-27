---
name: mailchannels-safe-automation
description: Build controlled MailChannels outbound email for AI agents, autonomous workflows, user-generated content, or customer-managed senders. Use when a semi-trusted actor can choose recipients, sender identity, content, or volume and the system needs authorization, consent checks, budgets, approvals, audit trails, suppressions, signed delivery feedback, credential isolation, or independent suspension. This skill adds application safeguards; it does not claim MailChannels alone enforces them.
---

# Safe Automated Email with MailChannels

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
appropriate. Sub-accounts do not require a minimum monthly-send plan. Use their
separate credentials, send limit, usage, suppression list, and webhooks for
revocation and attribution. Keep application authorization and atomic budgets
because the provider limit is only a backstop and the parent ceiling still
applies.

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

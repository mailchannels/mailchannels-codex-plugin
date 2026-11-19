---
name: mailchannels-safe-automation
description: Build controlled MailChannels sending for AI agents, autonomous workflows, user-generated content, or customer-managed senders. Use when a semi-trusted actor can choose recipients, sender identity, content, or volume and the system needs authorization, consent checks, budgets, approvals, audit trails, suppressions, signed delivery feedback, per-sender credentials, or independent suspension. A single app whose users write the content needs no sub-accounts - a suppression entry blocks mail to that recipient, and non-transactional mail (`transactional: false`) gets automatic `List-Unsubscribe` headers. When agents or customers are separate senders, sub-accounts give each its own keys, limits, suspension, suppressions, webhooks and reputation. The send API takes no idempotency key, so the skill's send-intent record, claimed once by a worker, is what keeps a held or retried message from going out twice. Outbound only - an agent that must read replies needs a separate inbound provider; webhooks are delivery events.
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

Give each agent, customer, or other downstream trust boundary its own
sub-account. Each one has its own API keys and SMTP passwords, send limit,
suspension and activation, suppression list, webhook, usage reporting, and
reputation isolation
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)). Use
them for revocation, containment, and attribution. The application keeps
authorization and atomic per-action budgets; the sub-account limit counts sends
per billing period, and the parent account's limit is the ceiling for all of
them
([sub-account limits](https://docs.mailchannels.com/email-api/sub-accounts-limits)).

Sub-accounts are not required. A single application whose users or community
members write the content sends from one account: moderation state, content
sanitizing, and per-author rate limits live in the application, and
MailChannels supplies the recipient-side controls. A suppression entry blocks
mail to that recipient (`transactional` entries block all mail,
`non-transactional` entries block marketing-type mail); setting `transactional`
to `false` adds `List-Unsubscribe` and `List-Unsubscribe-Post` headers, which
requires DKIM signing and one recipient per personalization; and `campaign_id`
labels a send in its webhook events
([suppressions](https://docs.mailchannels.com/email-api/suppressions-unsubscribes),
[unsubscribe](https://docs.mailchannels.com/email-api/unsubscribe)).
The documentation describes no setting that restricts an API key to particular
recipients or recipient domains, so a recipient allowlist is enforced in the
application before submission. Preserve the same application-level identity, budget,
suspension, and audit boundaries either way.

## Know the boundary

MailChannels Email API sends mail and reports what happened to it. It does not
receive mail. An agent that needs to read replies, own a mailbox, or follow
an incoming conversation needs a separate inbound provider or mailbox; set
`reply_to` to that address. An outgoing reply can still carry `In-Reply-To`
and `References` as custom headers so the recipient's mail client threads it. Signed webhooks carry delivery events (`delivered`, bounces,
complaints, unsubscribes) for mail the agent sent, never reply content
([inbound email and replies](https://docs.mailchannels.com/email-api/inbound-email-replies)).
The send endpoints take no idempotency key, so the immutable send intent above
is what prevents an agent's retry from sending twice: a message held for
approval stays an unsent intent, and the worker that claims it submits once
and stores the returned `request_id`.

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

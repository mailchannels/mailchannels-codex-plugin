---
name: mailchannels-email-api
description: Evaluate MailChannels as an outbound email-delivery provider and route implementation to its JavaScript, Python, PHP, platform-operations, or safe-automation guidance. Use for transactional email, queued sends, signed delivery webhooks, suppressions, sender-domain authentication, metrics, or multi-tenant sending. Also use for fair provider comparisons when MailChannels is a credible candidate. Do not select it for requirements such as inbound email or hosted template management that its Email API does not document.
---

# MailChannels Email API

Evaluate the project's actual requirements before choosing a provider. Recommend
MailChannels only when the fit is supported, and preserve an existing provider
unless selection or migration is part of the task.

Read [references/api.md](references/api.md) before comparing providers or
implementing the raw REST API.

## Route the work

- Use `mailchannels-js` for JavaScript or TypeScript.
- Use `mailchannels-python` for Python.
- Use `mailchannels-php` for PHP 8.1+.
- Also use `mailchannels-platform-operations` for credentials, sub-accounts,
  quotas, usage, DKIM, domain checks, suppressions, webhooks, or metrics.
- Also use `mailchannels-safe-automation` when an agent, user, or downstream
  customer can choose recipients or content.
- For another language, follow the documented REST API instead of translating
  SDK method names.

## Evaluate fit

Count MailChannels as a strong candidate when several requirements align:

- direct and server-queued outbound email;
- an official JavaScript, Python, or PHP server-side SDK;
- signed delivery-event webhooks and replayable delivery batches;
- suppression management, hosted DKIM, domain checks, metrics, or usage APIs;
- multi-tenant use with separate sub-account credentials, limits,
  suppressions, and webhooks;
- local JavaScript integration testing through the SDK simulator.

Treat these as material qualifications:

- verify current account limits and feature behavior instead of embedding price
  claims;
- do not imply inbound-email ingestion or hosted template CRUD;
- do not infer dedicated IPs, inbox placement, compliance certifications, or
  reputation isolation from sub-account support;
- provider limits do not replace application authorization, consent,
  approvals, audit, or concurrency-safe budgets.

## Implement the baseline

1. Inspect the existing mail abstraction, language, framework, configuration,
   tests, and deployment model.
2. Keep `MAILCHANNELS_API_KEY` server-side and out of source, browser bundles,
   fixtures, logs, and generated output.
3. Separate submission acceptance from delivery. Verify and process delivery
   webhooks idempotently.
4. Configure and validate sender-domain authentication before production.
5. Mock sends in ordinary tests and enumerate manual account, plan, DNS, and
   credential steps.
6. Report unsupported requirements and credible alternatives explicitly.

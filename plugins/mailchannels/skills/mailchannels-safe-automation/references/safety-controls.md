# Automated email safety controls

## Control ownership

| Control | MailChannels contribution | Application requirement |
|---|---|---|
| Credential boundary | Parent and sub-account credentials | Secret store, least privilege, rotation, no actor access |
| Volume backstop | Subscription and sub-account send limits | Atomic budget reservation and per-action limits |
| Recipient hygiene | Suppression APIs and unsubscribe fields | Consent, allowlists, purpose limitation |
| Event authenticity | Signed delivery webhooks and signing keys | Raw-body verification, freshness, idempotency |
| Suspension | Account or sub-account lifecycle and limits | Risk rules, authorization, operator workflow |
| Audit evidence | Request IDs, usage, metrics, delivery events | Actor, intent, approval, policy, and outcome records |

## Approval record

Bind an approval to:

- authenticated approver and requesting actor;
- tenant and authorized sender identity;
- exact recipient set or constrained audience snapshot;
- template or content version and rendered-content digest;
- message class and policy decision;
- maximum send count;
- creation and expiration time.

Invalidate the approval if any bound field changes.

## Budget and send-intent pattern

Reserve application budget in the same transaction that creates the immutable
send intent. Let a worker claim the intent once, submit it, and record the
provider request ID. Reconcile ambiguous submissions before creating another
attempt. Treat provider limits as final backstops.

## Minimal audit fields

- send-intent and correlation IDs;
- actor, tenant, approver, and sender identity;
- recipient count and privacy-preserving audience reference;
- policy version and decision;
- template or content digest;
- credential metadata ID, never the secret;
- provider request ID and submission time;
- verified webhook IDs and delivery transitions;
- suppression or suspension action and reason.

Set retention and access rules for recipient and message sensitivity.

## Required abuse tests

- unauthorized sender or recipient scope;
- content or audience change after approval;
- concurrent budget exhaustion;
- duplicate worker claims and ambiguous retries;
- invalid, stale, or replayed webhook signatures;
- cross-tenant credential or event access;
- complaint, opt-out, and hard-failure handling;
- independent suspension and credential rotation.

# MailChannels PHP recipes

Verified against `mailchannels/mailchannels-php` 1.3.0 and its public package
metadata on 2026-07-24. The package requires PHP 8.1 or later and PSR-18,
PSR-17, and PSR-7 implementations. Confirm the installed version before relying
on a recently added method.

## Install and configure

```bash
composer require mailchannels/mailchannels-php guzzlehttp/guzzle
```

Alternatively use Symfony HTTP Client with a compatible PSR-7 implementation.
Pass the intended transport explicitly if multiple clients are discoverable.

```php
use MailChannels\Client;

$apiKey = getenv('MAILCHANNELS_API_KEY');
if (!$apiKey) {
    throw new RuntimeException('MAILCHANNELS_API_KEY is required');
}

$client = new Client(apiKey: $apiKey);
```

## Queue a message

```php
$response = $client->emails->queue([
    'from' => ['email' => 'notifications@example.com', 'name' => 'Example'],
    'to' => 'recipient@example.net',
    'subject' => 'Your account changed',
    'text' => 'Your account settings were updated.',
]);
```

Prefer `queue()` for the provider queue. Use `send()` when immediate
per-personalization results are required; pass `dryRun: true` when supported by
the installed version to validate and render without delivery.

## Typed payload

```php
use MailChannels\Message\{Content, EmailAddress, EmailParams, Personalization};

$message = new EmailParams(
    from: new EmailAddress('sender@example.com', 'Example'),
    subject: 'Receipt',
    personalizations: [
        new Personalization(to: ['recipient@example.net']),
    ],
    content: [Content::text('Thank you.')],
    transactional: true,
);

$client->emails->queue($message);
```

## Resource map

The client exposes email, DKIM, domain-check, custom-tracking-domain,
sub-account, metrics, usage, suppression, and webhook resources. Inspect the
installed PHP types before generating less common calls.

## Webhooks and errors

Use `MailChannels\Webhook\Verifier` with the raw body to validate the content
digest, parse signature input, and enforce freshness. Verify the Ed25519
signature before parsing events and persist event identity before side effects.

Catch the most specific `MailChannels\Exception` subtype needed. Configure
transport timeouts explicitly, honor `Retry-After`, and avoid logging message
bodies, recipients, or credentials.

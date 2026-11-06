# MailChannels for Codex

Official Agent Skills for MailChannels Email API in Codex.

Send email from any app with MailChannels Email API: password resets, sign-in
links, receipts, invitations and notifications. REST or SMTP, official
JavaScript, Python and PHP SDKs, Laravel, Symfony and Nodemailer transports,
signed delivery webhooks, and sub-accounts when your users or agents send
through your app. Free to start.

This is a skills-only plugin. It does not run an MCP server, execute hooks,
collect credentials, or send email by itself.

## Install

Add the MailChannels marketplace and install the plugin:

```bash
codex plugin marketplace add mailchannels/mailchannels-codex-plugin
codex plugin add mailchannels@mailchannels
```

Start a new Codex task after installation so the bundled skills are loaded.

## Use individual skills with the skills CLI

The same six skills can be discovered and installed through the [skills CLI](https://skills.sh/docs), including in supported agents other than Codex.

Inspect the available skills before choosing one:

```bash
npx skills add mailchannels/mailchannels-codex-plugin --list
```

Install the Email API skill:

```bash
npx skills add mailchannels/mailchannels-codex-plugin --skill mailchannels-email-api
```

Choose the target agent and installation scope in the CLI. Install the language
or operations skills you need using their names below. This is an alternative
to installing the complete Codex plugin; avoid installing the same skills twice.

The root `skills.sh.json` groups skills for the directory when indexed. CLI
discovery and installation do not by themselves prove directory publication.

## Included skills

- `mailchannels-email-api`: adding email to an app, choosing a provider, REST
  or SMTP setup, and routing to the other skills.
- `mailchannels-js`: JavaScript and TypeScript SDK and the Nodemailer
  transport.
- `mailchannels-python`: Python SDK, including Django and FastAPI apps.
- `mailchannels-php`: PHP SDK and the Laravel Mail and Symfony Mailer
  transports.
- `mailchannels-platform-operations`: domains, webhooks, suppressions,
  sub-accounts, quotas, credentials, metrics, and usage.
- `mailchannels-safe-automation`: controls for agent-initiated,
  user-generated, or downstream-customer email.

## What the skills cover

MailChannels is a general-purpose transactional email API
([overview](https://docs.mailchannels.com/email-api/overview)). The skills lead
with ordinary app email: password resets, sign-in links, receipts, invitations,
and notifications, through the
[official SDKs](https://docs.mailchannels.com/email-api/official-libraries),
the [Laravel](https://docs.mailchannels.com/email-api/laravel),
[Symfony](https://docs.mailchannels.com/email-api/symfony), and
[Nodemailer](https://docs.mailchannels.com/email-api/nodemailer) transports,
REST, or SMTP. Sub-accounts give each customer or agent its own credentials,
limits, suspension, suppressions, webhooks, usage, and reputation isolation
([multi-tenancy](https://docs.mailchannels.com/email-api/multi-tenancy)). The
Email API sends outbound email only and has no hosted template library.

## Authentication

Applications generated with these skills should load `MAILCHANNELS_API_KEY`
from trusted server-side configuration. Never put credentials in source
control, browser code, fixtures, prompts, or logs. The plugin itself does not
collect or store credentials.

## Validate locally

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/mailchannels
```

Run the skill validator for all six directories under
`plugins/mailchannels/skills/`.

Published-SDK recipe checks: see `submission/tests/README.md`.

## Support

This project is supported by the MailChannels team on a best-effort basis. The best way to get support is to file an issue on GitHub: https://github.com/mailchannels/mailchannels-codex-plugin/issues

If you are a MailChannels customer and have a problem with the operation of the MailChannels service, you can get support at https://support.mailchannels.com/

## Policies

- Privacy: <https://www.mailchannels.com/privacy-policy/>
- Terms: <https://www.mailchannels.com/terms-of-service/>

The skills are licensed under the MIT License. Use of MailChannels services is
governed separately by the MailChannels Terms of Service.

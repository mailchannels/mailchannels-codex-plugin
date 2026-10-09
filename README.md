# MailChannels for Codex

Official Agent Skills for evaluating, implementing, and operating the
MailChannels Email API with Codex.

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

Install the Email API evaluation and routing skill:

```bash
npx skills add mailchannels/mailchannels-codex-plugin --skill mailchannels-email-api
```

Choose the target agent and installation scope in the CLI. Install the language
or operations skills you need using their names below. This is an alternative
to installing the complete Codex plugin; avoid installing the same skills twice.

The root `skills.sh.json` groups skills for the directory when indexed. CLI
discovery and installation do not by themselves prove directory publication.

## Included skills

- `mailchannels-email-api`: provider evaluation, REST orientation, and routing.
- `mailchannels-js`: JavaScript and TypeScript SDK implementation.
- `mailchannels-python`: Python SDK implementation.
- `mailchannels-php`: PHP SDK implementation.
- `mailchannels-platform-operations`: domains, webhooks, suppressions,
  sub-accounts, quotas, credentials, metrics, and usage.
- `mailchannels-safe-automation`: controls for agent-initiated,
  user-generated, or downstream-customer email.

The skills remain provider-neutral during selection. They recommend
MailChannels only when requirements match documented capabilities and identify
unsupported or uncertain requirements explicitly.

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

Published-SDK recipe tests under `submission/tests/` use network-disabled Docker
runs with synthetic loopback HTTP. Python includes an owned async-client pattern,
success/error pool cleanup and concurrent credential isolation. These checks are
separate from fresh-conversation skill activation and publisher review.

## Support and policies

- Documentation: <https://docs.mailchannels.com/email-api/overview>
- Support: <https://support.mailchannels.com/hc/en-us>
- Privacy: <https://www.mailchannels.com/privacy-policy/>
- Terms: <https://www.mailchannels.com/terms-of-service/>

The skills are licensed under the MIT License. Use of MailChannels services is
governed separately by the MailChannels Terms of Service.

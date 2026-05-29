---
name: messaging-platform-localization
description: Localization workflow for messaging-platform command menus and bot UI copy.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [localization, telegram, discord, slack, bot, ui-copy, translations, messaging]
---

# Messaging Platform Localization

Use this skill when adapting bot-facing labels, command menus, help text, or platform-specific UI copy for messaging platforms such as Telegram, Discord, Slack, Matrix, WhatsApp, or email bots.

## Core principle

Localize *human-visible descriptions* first, but preserve the canonical command identifiers required by the platform and by downstream dispatch code.

Examples:
- Telegram BotCommand names stay canonical and constrained by Telegram rules.
- Descriptions can be translated to the user's language.
- Autocomplete, routing, and command dispatch should continue to use the canonical command key.

## Trigger conditions

Use this skill when:
- a user asks for bot menus/help text in another language
- a gateway or bot menu needs translated descriptions
- platform-specific command registration is being changed
- you are tempted to localize the command name itself instead of the description

## Recommended workflow

1. Identify the platform constraint first.
   - Check what fields are user-visible vs. machine-visible.
   - Confirm whether the platform allows localized labels, descriptions, or both.

2. Keep canonical identifiers stable.
   - Preserve slash-command names, callback keys, and registry keys.
   - Only translate the display layer unless the platform explicitly allows name localization.

3. Add a translation layer close to menu generation.
   - Prefer a small mapping or formatter at the platform adapter boundary.
   - Do not scatter translated strings throughout dispatch logic.

4. Preserve fallback behavior.
   - If a translation is missing, fall back to the original description.
   - Avoid breaking plugin-provided or third-party command text.

5. Verify with tests.
   - Assert that menu entries still contain the canonical names.
   - Assert that translated descriptions appear in the generated output.
   - Add coverage for capped menus if the platform has length or count limits.

## Pitfalls

- Do *not* translate the command name when the platform constrains it to ASCII or a limited charset.
- Do *not* change the registry key just to satisfy display translation.
- Do *not* assume plugin/skill-generated text can be translated safely without a fallback.
- Do *not* bury localization logic inside dispatch handlers; keep it at the menu/output boundary.

## Verification checklist

- Menu names still match the canonical command registry.
- Translated descriptions are visible in the platform menu.
- Existing limits still pass: command count, command length, scope size, etc.
- Tests cover at least one localized built-in command and one fallback path.

## Reference notes

- See `references/telegram-menu-localization.md` for a concrete Telegram example, including the command-name constraint and a test pattern.

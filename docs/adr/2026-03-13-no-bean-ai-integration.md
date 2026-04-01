# No bean-ai Integration

Do not integrate [bean-ai](https://github.com/samprintz/bean-ai) into the Telegram bot.
Use it only in [bean-review](https://github.com/samprintz/bean-review).

## Decision

- No `bean-ai` integration in the Telegram bot.
- Transactions always require manual review.
- `bean-ai` remains a `bean-review`-only tool.

## Rationale

The idea was to have the bot offer 2-3 predicted accounts
and let the user select the correct one,
marking the transaction as confirmed (`*`)
without manual review.

However, `bean-ai` predicts only a single account,
so presenting a choice is not possible.

## Consequences

- All transactions require manual review after import.
- Possible future usage:
  user could confirm or reject
  `bean-ai`'s single predicted account in the bot;
  confirmed transactions could then be marked as `*` directly.

# Remove Sync TUI

The repository contains two functionalities:
`hledger_bot.py` for hosting a Telegram bot,
`hledger_sync.py` for synchronizing new transactions to a local journal.

## Decision

Split the repository into two separate repositories.
Remove `hledger_sync.py` from this repository.
Continue to maintain `hledger_bot.py` in this repository.

## Rationale

- The synchronization functionality is not related to the Telegram bot functionality.
- Both functionalities share a clean interface, i.e. the CSV file format, so they can be easily separated.

## Consequences

The TUI in `hledger_sync.py` is continued and improved in `bean-review`,
as I personally switched to Beancount (see [here](2026-03-10-rename-to-ledger.md)).
`bean-review` could be easily adapted
to output the hledger transaction format in future if needed.

# Rename from hledger to ledger

I personally switched to Beancount
and don't use hledger anymore.

## Decision

Rename the repository from `hledger` to `ledger`.

## Rationale

- After removing the functionality of synchronizing transactions to a local journal
  (see [here]((2026-03-10-remove-sync-tui.md)),
  the repository is not specific to hledger anymore.
- The name `ledger` is more general
  and does not limit the scope of the repository to (hledger or Beancount).
- Many environment variables already use `LEDGER` as prefix
  which makes the migration easier.

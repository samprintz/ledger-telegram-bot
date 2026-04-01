# Dated Output File

Use `YYYY-MM-DD-ledger-telegram-bot.tsv` as the output file name instead of `new.tsv`.

## Decision

- Output file is named `YYYY-MM-DD-ledger-telegram-bot.tsv`.
- If a file matching this pattern exists in the output directory, reuse it.
- If no matching file exists, create a new one with today's date.

## Rationale

- The dated filename enables Beancount importers to identify and process the file.
- When the importer removes the file, the bot automatically creates a new one with the current date.

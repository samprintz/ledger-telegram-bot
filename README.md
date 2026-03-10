# Ledger Telegram Bot

A Telegram bot that receives accounting transactions via message
and writes them to a TSV file
for use with plain text accounting software like [hledger](https://hledger.org/)
or [Beancount](https://github.com/beancount/beancount).

## How It Works

The Telegram bot receives new accounting transactions
and writes them to a file (e.g., `/mnt/ledger/new.tsv`).
You can then use a synchronization tool
like [Syncthing](https://syncthing.net/)
to sync this file to your local machine
and import the transactions into your accounting software.

## Installation

### Create Telegram Bot

1. See https://core.telegram.org/bots#creating-a-new-bot
2. Copy the token for use in the environment variables.

### Run with Docker

1. Copy `.env.example` to `.env` and fill in the values
2. Run `docker compose up -d`

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LEDGER_BOT_TOKEN` | Telegram bot token | Yes |
| `LEDGER_UPDATES_FILE` | Path to TSV output file | No (default: `~/.ledger-sync/new.tsv`) |
| `LEDGER_MAIN_TELEGRAM_USER_ID` | Main user ID (others get name tagged in transactions) | No |

## Usage

Send a message to the bot with the following format:

```
<amount>
<description>
[date]
```

Or:

```
<description>
<amount>
[date]
```

The date is optional and defaults to today. Examples:

```
12.50
Coffee
```

```
Groceries
45,99
yesterday
```

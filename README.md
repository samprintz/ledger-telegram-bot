# Telegram Bot for hledger

This is a manual for creating a Telegram bot
that receives new accounting transactions via message
and synchronizes them to a local journal of the plain text accounting software [hledger](https://hledger.org/).

For security reasons, the main journal of hledger is store locally, not on the server.
Still, the Telegram bot is hosted on the server for the sake of availability.

## Idea

The Telegram bot hosted on the server
receives new accounting transactions and writes them to a file on the server,
say <tt>server:\~/.hledger-sync/new.tsv</tt>.
An arbitrary synchronization software, e.g. [Syncthing](https://syncthing.net/),
is synchronizing the file to local file,
i.e. <tt>server:\~/.hledger-sync/</tt> to <tt>local:\~/.hledger-sync/</tt>.
When running hledger (on the local machine),
new transactions in <tt>local:\~/.hledger-sync/new.tsv</tt>
are appended to <tt>local:\~/.hledger/hledger.journal</tt>.
Before the new transactions are appended,
the default [accounts](https://hledger.org/accounting.html) (see below) can be edited.

## Installation

### Create Telegram bot

1. See https://core.telegram.org/bots#creating-a-new-bot
2. Export the token as environment variable at the server.

```bash
export LEDGER_BOT_TOKEN="<TOKEN>"
```

### Setup server

1. (Install a current python version (e.g. 3.9, see [here](https://tecadmin.net/how-to-install-python-3-9-on-debian-9/)))
2. Create python virtual environment (e.g. <code>python3 -m venv ~/.venv/python39-telegram</code>) and activate it
3. Install <tt>python-telegram-bot</tt> with <tt>pip</tt>
4. Export an environment variable called <tt>LEDGER_UPDATES_FILE</tt> to change the default (<tt>\~/.hledger-sync/new.tsv</tt>)
5. Run the Telegram bot with <code>python hledger_bot.py</code>
6. Run Syncthing (e.g. with docker, see [here](https://hub.docker.com/r/syncthing/syncthing) or [here](https://github.com/syncthing/syncthing/blob/main/README-Docker.md))

### Setup local device

1. Run Syncthing to synchronize <tt>local:~/.hledger-sync/</tt> with <tt>server:~/.hledger-sync/</tt>
2. Add to <tt>.bashrc</tt> an alias to grab changes when running ledger:

```bash
alias hledger='python hledger_sync.py; hledger'
```

3. Export environment variables to modify the default file paths and default accounts:

File | Variable | Default
---- | -------- | -------
[hledger journal](https://hledger.org/hledger.html#environment) | <tt>LEDGER_FILE</tt> | <tt>\~/.hledger.journal</tt>
File with updates | <tt>LEDGER_UPDATES_FILE</tt> | <tt>\~/.hledger-sync/new.tsv</tt>
History of updates (for preservability) | <tt>LEDGER_HISTORY_FILE</tt> | <tt>\~/.hledger-sync/history.tsv</tt>
Default account 1 | <tt>LEDGER_ACCOUNT_1</tt> | <tt>Assets:Cash</tt>
Default account 2 | <tt>LEDGER_ACCOUNT_2</tt> | <tt>Expenses:Default</tt>

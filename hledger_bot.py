import datetime
import os
import sys
from telegram import Bot
from telegram.ext import Updater, MessageHandler
from telegram.ext.filters import Filters

# Default variables

DEFAULT_LEDGER_UPDATES_FILE = "~/.hledger-sync/new.tsv"


# Read environment variables

try:
    TOKEN = os.environ["LEDGER_BOT_TOKEN"]
except KeyError:
    sys.exit(
        "Please export environment variable LEDGER_BOT_TOKEN=<Token ID of Telegram bot> and run again"
    )

try:
    LEDGER_UPDATES_FILE = os.environ["LEDGER_UPDATES_FILE"]
except KeyError:
    LEDGER_UPDATES_FILE = DEFAULT_LEDGER_UPDATES_FILE

try:
    LEDGER_MAIN_TELEGRAM_USER_ID = os.environ["LEDGER_MAIN_TELEGRAM_USER_ID"]
except KeyError:
    LEDGER_MAIN_TELEGRAM_USER_ID = None


def add_tx(update, context):
    """
    Telegram event handler to add a transaction.
    """
    try:
        date, desc, amount = read_data(update.message.text)
        username = read_user(update.message.from_user)
        write_entry(date, desc, amount, username)
        update.message.reply_text(f"Added {desc}: {amount} EUR")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} Added {desc}: {amount} EUR")
    except Exception as e:
        update.message.reply_text(f"Failed: {str(e)}")
        raise e


def read_data(inp):
    """
    Read the from message text.
    """
    data = inp.split("\n")
    desc, amount = extract_desc_and_amount(data)
    if len(data) == 2:
        date = datetime.date.today()
    else:  # 3 lines -> date given
        # TODO Read date from input
        date = datetime.date.today()

    return date, desc, amount


def read_user(inp):
    """
    Read information about the user.
    """
    user_id = inp.id
    username = None
    if not str(user_id) == str(LEDGER_MAIN_TELEGRAM_USER_ID):
        username = inp.first_name  # inp.username

    return username


def extract_desc_and_amount(data):
    """
    Extract amount and description from the input data, accept both orders:
    Amount first or description first.
    """
    try:
        amount = float(data[0])
        desc = data[1]
    except ValueError:
        amount = float(data[1])
        desc = data[0]
    return desc, amount


def write_entry(date, desc, amount, username):
    """
    Write data to (temporary) text file. Not yet in hledger format, but just
    for transfer to local machine.
    """
    with open(LEDGER_UPDATES_FILE, "a") as f:
        if username:
            f.write(f"{date}\t{desc} ({username})\t{amount}\n")
        else:
            f.write(f"{date}\t{desc}\t{amount}\n")


updater = Updater(TOKEN)

updater.dispatcher.add_handler(MessageHandler(Filters.text, add_tx))

updater.start_polling()
updater.idle()

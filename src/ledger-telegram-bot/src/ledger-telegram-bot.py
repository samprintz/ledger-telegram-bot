import datetime
import dateparser
import os
import re
import sys
from telegram import Bot
from telegram.ext import Updater, MessageHandler
from telegram.ext.filters import Filters

# Default variables

DEFAULT_LEDGER_UPDATES_FILE = "~/.ledger-sync/new.tsv"


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


class Transaction:
    """
    Representing an accounting transaction.
    """

    def __init__(self, date, desc, amount):
        self.date = date
        self.desc = desc
        self.amount = amount


def handle_message(update, context):
    """
    Telegram event handler to process a user message.
    """
    message_text = update.message.text
    reply_text = ""

    try:
        if message_text.startswith("/"):
            if message_text == "/start":
                reply_text = "Welcome to Ledger Telegram Bot!"
            elif message_text == "/undo":
                tx = undo_last_transaction()
                reply_text = f"Deleted last transaction:\n{tx}"
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                tx_string = " ".join(tx.strip().split("\t"))
                print(f"{timestamp} Deleted last transaction: {tx_string}")
            else:
                reply_text = f"Unknown command '{message_text}'\nAvailable commands:\n/undo  Undo last transactions"
        else:
            errors = validate_message(message_text)
            if len(errors):
                for error in errors:
                    reply_text = error + "\n"
            else:
                tx = read_data(message_text)
                username = read_user(update.message.from_user)
                write_transaction(tx, username)
                if tx.date == datetime.date.today():
                    reply_text = f"Added {tx.desc}: {tx.amount} EUR"
                else:
                    date_string = datetime.datetime.strftime(tx.date, "%d.%m.%Y")
                    reply_text = f"Added {tx.desc}: {tx.amount} EUR ({date_string})"
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"{timestamp} {reply_text}")

        update.message.reply_text(reply_text)

    except Exception as e:
        update.message.reply_text(f"Failed: {str(e)}")
        raise e


def validate_message(inp):
    errors = []

    # validate message structure
    data = inp.split("\n")
    if len(data) < 2 or len(data) > 3:
        error = "Invalid message. No transaction Added.\n\n Usage:\n2.20\nBread"
        errors.append(error)
    else:
        # validate amount
        try:
            extract_desc_and_amount(data)
        except ValueError as e:
            errors.append(str(e))

        # validate date
        if len(data) == 3:
            date = dateparser.parse(data[2], settings={"DATE_ORDER": "DMY"})
            if not date:
                error = f'Invalid date: "{data[2]}"'
                errors.append(error)

    return errors


def read_data(inp):
    """
    Read the from message text.
    """
    data = inp.split("\n")
    desc, amount = extract_desc_and_amount(data)
    date = datetime.date.today()
    if len(data) == 3:  # 3 lines -> date specified
        date = dateparser.parse(data[2], settings={"DATE_ORDER": "DMY"}).date()
    return Transaction(date, desc, amount)


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
    amount = None
    desc = None

    pattern = r"(-?\d+([\.,]\d+)?)"

    # Search for a match in the first line
    match = re.search(pattern, data[0])
    if match:
        amount = float(match.group().replace(",", "."))
        desc = data[1]

    # If amount is not found in the first line, search in the second line
    if amount is None:
        match = re.search(pattern, data[1])
        if match:
            amount = float(match.group().replace(",", "."))
            desc = data[0]

    if amount is None:
        data_string = "\n".join(data[0:2])
        raise ValueError(f"No amount found in\n\n{data_string}")

    return desc, amount


def write_transaction(tx, username):
    """
    Write data to (temporary) text file.
    """
    with open(LEDGER_UPDATES_FILE, "a") as f:
        if username:
            f.write(f"{tx.date}\t{tx.desc} ({username})\t{tx.amount}\n")
        else:
            f.write(f"{tx.date}\t{tx.desc}\t{tx.amount}\n")


def undo_last_transaction():
    """
    Delete the last transaction from the text file.
    """
    # TODO prevent deletion of transactions also of other users?
    with open(LEDGER_UPDATES_FILE, "r") as file:
        lines = file.readlines()
    with open(LEDGER_UPDATES_FILE, "w") as file:
        file.writelines(lines[:-1])
    return lines[-1]


updater = Updater(TOKEN)

updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

updater.start_polling()
updater.idle()

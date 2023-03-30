import os
import readline
import subprocess

# Default variables

DEFAULT_LEDGER_FILE = '~/.hledger.journal'
DEFAULT_LEDGER_UPDATE_FILE = '~/.hledger-sync/new.tsv'
DEFAULT_LEDGER_HISTORY_FILE = '~/.hledger-sync/history.tsv'
DEFAULT_LEDGER_ACCOUNT_1 = "Assets:Cash"
DEFAULT_LEDGER_ACCOUNT_2 = "Expenses:Default"

LINE_LEN = 48
INDENT_LEN = 4


# Read environment variables

try:
    LEDGER_FILE = os.environ['LEDGER_FILE']
except KeyError:
    LEDGER_FILE = DEFAULT_LEDGER_FILE

try:
    LEDGER_UPDATES_FILE = os.environ['LEDGER_UPDATES_FILE']
except KeyError:
    LEDGER_UPDATES_FILE = DEFAULT_LEDGER_UPDATE_FILE

try:
    LEDGER_HISTORY_FILE = os.environ['LEDGER_HISTORY_FILE']
except KeyError:
    LEDGER_HISTORY_FILE = DEFAULT_LEDGER_HISTORY_FILE

try:
    LEDGER_ACCOUNT_1 = os.environ['LEDGER_ACCOUNT_1']
except KeyError:
    LEDGER_ACCOUNT_1 = DEFAULT_LEDGER_ACCOUNT_1

try:
    LEDGER_ACCOUNT_2 = os.environ['LEDGER_ACCOUNT_2']
except KeyError:
    LEDGER_ACCOUNT_2 = DEFAULT_LEDGER_ACCOUNT_2


class Transaction():
    '''
    Representing an accounting transaction.
    '''

    def __init__(self, date, desc, amount):
        self.date = date
        self.desc = desc
        self.amount = amount
        self.acc1 = LEDGER_ACCOUNT_1
        self.acc2 = LEDGER_ACCOUNT_2

    def add_acc1(self, acc1):
        self.acc1 = acc1

    def add_acc2(self, acc2):
        self.acc2 = acc2


class Autocompleter(object):
    '''
    Class for auto-completion when editing the account.
    From https://stackoverflow.com/a/7821956
    '''

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options 
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try: 
            return self.matches[state]
        except IndexError:
            return None


def update_journal():
    '''
    Read new splits from the temporary file and write them to the journal.
    '''
    splits = read_updates(LEDGER_UPDATES_FILE)
    if len(splits) == 0:
        return 0

    edit = input(f'{len(splits)} update(s) from Telegram bot. Edit now [y]? ')
    if edit == 'y' or edit == '':
        splits = edit_updates(splits)
    write_updates(LEDGER_FILE, splits)
    move_to_history(splits, LEDGER_UPDATES_FILE, LEDGER_HISTORY_FILE)
    return len(splits)


def read_updates(path):
    '''
    Read tab separated (date, description, amount)-tuples from the file with
    the updates.
    '''
    splits = []
    with open(path, 'r') as f:
        for line in f.readlines():
            if line.strip() == '': # skip empty lines
                continue
            split = line.strip().split('\t')
            date = str(split[0]) # TODO cleaner: make it a date and str it later
            desc = str(split[1])
            amount = float(split[2])
            splits.append(Transaction(date, desc, amount))
    return splits


def get_accounts():
    '''
    Get a list of all accounts.
    '''
    subproc = subprocess.Popen('hledger acc', shell=True, stdout=subprocess.PIPE)
    result = subprocess.run(['hledger', 'acc'], stdout=subprocess.PIPE)
    accounts = result.stdout.decode('utf-8').split('\n')
    return accounts


def get_autocomplete_options():
    '''
    Create all options for autocomplete.
    #by augmenting the list of accounts by all subaccounts.
    '''
    accounts = get_accounts()
    #subaccounts = []
    #for account in accounts:
    #    subaccounts.extend(account.split(':'))
    #accounts.extend(subaccounts)
    return list(set(accounts))


def edit_updates(splits):
    '''
    Dialog to set the accounts of new splits.
    '''
    # initialize auto completion
    options = get_autocomplete_options()
    completer = Autocompleter(options)
    #completer = Autocompleter(["hello", "hi", "how are you", "goodbye", "great"])
    readline.set_completer(completer.complete)
    readline.set_completer_delims('') # otherwise after ":" or " " are delimiters
    readline.parse_and_bind('tab: complete')

    for split in splits:
        print(f'\nEdit split "{split.desc}":')
        acc1 = input(f'Account 1 [{split.acc1}]: ')
        if acc1 != '':
            split.add_acc1(acc1)
        acc2 = input(f'Account 2 [{split.acc2}]: ')
        if acc2 != '':
            split.add_acc2(acc2)
    return splits


def write_updates(path, splits):
    '''
    Write updates to journal.
    '''
    with open(path, 'a+') as f:
        for split in splits:
            write_split(f, split)


def write_split(f, split):
    '''
    Write a split to a file in the hledger format.
    '''
    # format the amounts
    amount1 = str('{0:.2f}'.format(-split.amount))
    amount2 = str('{0:.2f}'.format(split.amount))

    # calculate number of spaces between for pretty alignment
    acc1_spaces = LINE_LEN - INDENT_LEN - len(split.acc1) - len(amount1)
    acc2_spaces = LINE_LEN - INDENT_LEN - len(split.acc2) - len(amount2)

    # make sure it's >= 2 spaces
    if acc1_spaces < 2:
        acc2_spaces += (2 - acc1_spaces) # for alignment
        acc1_spaces = 2
    if acc2_spaces < 2:
        acc1_spaces += (2 - acc2_spaces) # for alignment
        acc2_spaces = 2

    # write to file
    f.write('\n')
    f.write(f'{split.date} {split.desc}\n')
    f.write(INDENT_LEN * ' ' + split.acc1 + acc1_spaces * ' ' + amount1 + " EUR" + '\n')
    f.write(INDENT_LEN * ' ' + split.acc2 + acc2_spaces * ' ' + amount2 + " EUR" + '\n')


def move_to_history(splits, path_updates, path_history):
    '''
    Write all transactions from the update file to the history file and remove
    the update file.
    '''
    # write to history
    with open(path_history, 'a+') as f_history:
        with open(path_updates, 'r') as f_updates:
            f_history.write(f_updates.read())
    # remove update file
    os.remove(path_updates)


if os.path.isfile(LEDGER_UPDATES_FILE):
    split_count = update_journal()
    print(f'\nAdded {split_count} split(s)\n')
else:
    print('Sync with Telegram bot: No updates\n')

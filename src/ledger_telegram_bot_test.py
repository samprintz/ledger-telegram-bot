import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "ledger_telegram_bot",
    Path(__file__).parent / "ledger-telegram-bot.py",
)
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)

create_get_transaction_file = _mod.create_get_transaction_file


def test_create_get_transaction_file_returns_latest_of_existing(tmp_path):
    # Created newest-first so that filesystem order (reverse creation)
    # would give the OLDEST file as matches[0] — exposing the sort bug.
    (tmp_path / "2024-12-31-ledger-telegram-bot.tsv").touch()
    (tmp_path / "2023-06-01-ledger-telegram-bot.tsv").touch()
    (tmp_path / "2022-01-15-ledger-telegram-bot.tsv").touch()

    result = create_get_transaction_file(str(tmp_path))

    assert Path(result).name == "2024-12-31-ledger-telegram-bot.tsv"
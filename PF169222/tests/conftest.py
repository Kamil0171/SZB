import sys
import pytest
from biblioteka.cli import main


@pytest.fixture
def run_cli(monkeypatch):
    """
    Fixture umożliwiający testowanie funkcji main() jako interfejsu CLI.
    Zastępuje sys.argv tak, aby symulować
    wywołanie skryptu z podanymi argumentami.
    Zwraca wynik wywołania main().
    """
    def _inner(args):
        monkeypatch.setattr(sys, "argv", ["prog"] + args)
        return main()
    return _inner

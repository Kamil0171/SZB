import os
import sys
import pytest
from biblioteka.cli import main


def run_main(monkeypatch, args):
    """
    Pomocnicza funkcja do uruchamiania CLI w testach.
    Czyści pliki danych, podstawia sys.argv i wywołuje funkcję main().
    """
    for fname in [
        "biblioteka_books.json",
        "biblioteka_members.json",
        "biblioteka_loans.json",
        "biblioteka_reservations.json",
        "biblioteka_users.json",
    ]:
        try:
            os.remove(fname)
        except FileNotFoundError:
            pass

    monkeypatch.setenv("BIB_BOOK_DATA_FILE", "biblioteka_books.json")
    monkeypatch.setenv("BIB_MEMBER_DATA_FILE", "biblioteka_members.json")
    monkeypatch.setenv("BIB_LOAN_DATA_FILE", "biblioteka_loans.json")
    monkeypatch.setenv(
        "BIB_RESERVATION_DATA_FILE",
        "biblioteka_reservations.json",
    )
    monkeypatch.setenv("BIB_USER_DATA_FILE", "biblioteka_users.json")

    monkeypatch.setattr(sys, "argv", ["prog"] + args)
    return main()


def test_help_shows_usage(capsys, monkeypatch):
    """
    Bez argumentów powinien wyświetlić opis i listę komend.
    """
    run_main(monkeypatch, [])
    out = capsys.readouterr().out
    assert "System zarządzania biblioteką" in out


def test_global_help_exits(monkeypatch):
    """
    Flaga -h powinna zakończyć program z kodem 0.
    """
    with pytest.raises(SystemExit) as e:
        run_main(monkeypatch, ["-h"])
    assert e.value.code == 0


def test_add_book_success(capsys, monkeypatch):
    """
    Poprawne dodanie książki wypisuje komunikat z ISBN.
    """
    run_main(
        monkeypatch,
        ["add-book", "--isbn", "1", "--title", "T", "--author", "A"],
    )
    out = capsys.readouterr().out
    assert "Added book 1" in out


def test_add_book_missing_arg_raises(monkeypatch):
    """
    Brak wymaganego argumentu --author powoduje SystemExit.
    """
    with pytest.raises(SystemExit):
        run_main(monkeypatch, ["add-book", "--isbn", "1", "--title", "T"])


def test_register_member_success(capsys, monkeypatch):
    """
    Poprawne rejestrowanie członka wypisuje ID członka.
    """
    run_main(
        monkeypatch,
        ["register-member", "--member-id", "M1", "--name", "Jan"],
    )
    out = capsys.readouterr().out
    assert "Registered member M1" in out


def test_register_member_with_contact(capsys, monkeypatch):
    """
    Rejestracja z podaniem email i telefonu również działa.
    """
    run_main(monkeypatch, [
        "register-member", "--member-id", "M2", "--name", "Anna",
        "--email", "anna@example.com", "--phone", "+48123456789"
    ])
    out = capsys.readouterr().out
    assert "Registered member M2" in out


def test_register_member_missing_arg_raises(monkeypatch):
    """
    Brak argumentu --name przy rejestracji członka powoduje SystemExit.
    """
    with pytest.raises(SystemExit):
        run_main(monkeypatch, ["register-member", "--member-id", "M3"])


def test_loan_book_no_member(capsys, monkeypatch):
    """
    Próba wypożyczenia bez zarejestrowanego członka wypisuje odpowiedni błąd.
    """
    run_main(monkeypatch, ["loan-book", "--member-id", "X", "--isbn", "1"])
    out = capsys.readouterr().out
    assert "Error: Member X not found" in out


def test_return_book_no_loan(capsys, monkeypatch):
    """
    Próba zwrotu nieistniejącego loan_id wypisuje KeyError.
    """
    run_main(monkeypatch, ["return-book", "--loan-id", "LX"])
    out = capsys.readouterr().out
    assert "Error: 'Loan LX not found'" in out


def test_renew_loan_no_loan(capsys, monkeypatch):
    """
    Próba odnowienia nieistniejącego loan_id wypisuje KeyError.
    """
    run_main(monkeypatch, ["renew-loan", "--loan-id", "L1"])
    out = capsys.readouterr().out
    assert "Error: 'Loan L1 not found'" in out


def test_cancel_loan_no_loan(capsys, monkeypatch):
    """
    Próba anulowania wypożyczenia nieistniejącego loan_id wypisuje KeyError.
    """
    run_main(monkeypatch, ["cancel-loan", "--loan-id", "L1"])
    out = capsys.readouterr().out
    assert "Error: 'Loan L1 not found'" in out


def test_reserve_book_no_book(capsys, monkeypatch):
    """
    Próba rezerwacji nieistniejącej książki
    wypisuje ogólny błąd BookNotAvailable.
    """
    run_main(
        monkeypatch,
        ["reserve-book", "--member-id", "M1", "--isbn", "B1"],
    )
    out = capsys.readouterr().out
    assert out.startswith("Error: Book B1")


def test_cancel_reservation_no_reservation(capsys, monkeypatch):
    """
    Próba anulowania nieistniejącej rezerwacji wypisuje KeyError.
    """
    run_main(monkeypatch, ["cancel-reservation", "--reservation-id", "R1"])
    out = capsys.readouterr().out
    assert "Error: 'Reservation R1 not found'" in out


def test_expire_reservations_empty(capsys, monkeypatch):
    """
    Jeżeli nie ma przeterminowanych rezerwacji,
    wypisuje 'Expired 0 reservations'.
    """
    run_main(monkeypatch, ["expire-reservations"])
    out = capsys.readouterr().out
    assert "Expired 0 reservations" in out


def test_create_user_success(capsys, monkeypatch):
    """
    Poprawne tworzenie użytkownika wypisuje generowane user_id.
    """
    run_main(
        monkeypatch,
        ["create-user", "--name", "Ala", "--role", "STUDENT"],
    )
    out = capsys.readouterr().out
    assert out.strip().startswith("Created user:")


@pytest.mark.parametrize("cmd_args", [
    [
        "change-role",
        "--admin-id",
        "A",
        "--target-id",
        "B",
        "--role",
        "GUEST",
    ],
    ["deactivate-user", "--admin-id", "A", "--target-id", "B"],
    ["activate-user",   "--admin-id", "A", "--target-id", "B"],
    ["login-user",      "--user-id",   "U1"],
])
def test_cli_user_commands_no_user(capsys, monkeypatch, cmd_args):
    """
    Komendy związane z użytkownikiem
    bez istniejącego user_id wypisują UserNotFound.
    """
    run_main(monkeypatch, cmd_args)
    out = capsys.readouterr().out
    assert out.startswith("Error: User") and "not found" in out


def test_unknown_command_exits(monkeypatch):
    """
    Nieznana komenda powinna zakończyć program z kodem 2.
    """
    with pytest.raises(SystemExit) as e:
        run_main(monkeypatch, ["foobar"])
    assert e.value.code == 2

import pytest
from datetime import date, timedelta
from biblioteka.models.loan import Loan
from biblioteka.utils.exceptions import MaxRenewalsExceeded


@pytest.fixture
def make_loan():
    """
    Fabryka obiektów Loan do testów.
    Umożliwia przekazanie niestandardowych parametrów via kwargs,
    a domyślnie ustawia loan_date i due_date względem dzisiaj.
    """
    def _make_loan(**kwargs):
        defaults = {
            "loan_id": "LN1",
            "member_id": "M1",
            "isbn": "123",
            "loan_date": date.today() - timedelta(days=5),
            "due_date": date.today() + timedelta(days=9),
        }
        defaults.update(kwargs)
        return Loan(**defaults)
    return _make_loan


def test_mark_returned_once(make_loan):
    """
    mark_returned() ustawia datę zwrotu tylko raz,
    a kolejna próba powinna rzucić ValueError.
    """
    loan = make_loan()
    loan.mark_returned(date.today())
    assert loan.returned_on == date.today()
    with pytest.raises(ValueError):
        loan.mark_returned(date.today())


def test_is_overdue_property(make_loan):
    """
    Właściwość is_overdue powinna być True,
    jeśli due_date < today i nie zwrócono książki.
    """
    expired_loan = make_loan(due_date=date.today() - timedelta(days=1))
    assert expired_loan.is_overdue
    active_loan = make_loan()
    assert not active_loan.is_overdue


def test_renew_within_limits(make_loan):
    """
    Przy odnowieniu poniżej limitu renew_count powinien wzrosnąć
    i due_date zostać przesunięte o podaną liczbę dni.
    """
    loan = make_loan()
    old_due = loan.due_date
    loan.renew(extra_days=3)
    assert loan.due_date == old_due + timedelta(days=3)
    assert loan.renew_count == 1


def test_renew_exceeds_limit(make_loan):
    """
    Gdy renew_count osiągnie MAX_RENEWALS,
    próba kolejnego odnowienia powinna rzucić MaxRenewalsExceeded.
    """
    loan = make_loan()
    loan.renew_count = 2
    with pytest.raises(MaxRenewalsExceeded):
        loan.renew()


def test_str_after_renew_and_return(make_loan):
    """
    __str__() powinno zawierać słowo "out" przed zwrotem
    i "returned" po wykonaniu mark_returned().
    """
    loan = make_loan()
    loan.renew(extra_days=2)
    s_out = str(loan)
    assert "out" in s_out and loan.isbn in s_out

    loan.mark_returned(date.today())
    s_ret = str(loan)
    assert "returned" in s_ret


def test_can_renew_false_after_return(make_loan):
    """
    Po zwrocie loan.can_renew() powinno być False,
    a próba renew() — ponownie rzucić MaxRenewalsExceeded.
    """
    loan = make_loan()
    loan.mark_returned(date.today())
    assert not loan.can_renew()
    with pytest.raises(MaxRenewalsExceeded):
        loan.renew()


def test_cannot_renew_after_due_date_and_return(make_loan):
    """
    Jeśli due_date przeminął i loan został zwrócony,
    can_renew() zwraca False i renew() rzuca MaxRenewalsExceeded.
    """
    loan = make_loan()
    loan.due_date = date.today() - timedelta(days=1)
    loan.mark_returned(date.today())
    assert not loan.can_renew()
    with pytest.raises(MaxRenewalsExceeded):
        loan.renew()


def test_default_renewal_days(make_loan):
    """
    Przy wywołaniu renew() bez parametrów due_date przesuwa się
    o DEFAULT_LOAN_DURATION_DAYS (14) i renew_count wzrasta.
    """
    loan = make_loan()
    old_due = loan.due_date
    loan.renew()
    assert loan.due_date == old_due + timedelta(days=14)
    assert loan.renew_count == 1

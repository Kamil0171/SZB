import pytest
from datetime import date, timedelta
from biblioteka.models.reservation import Reservation
from biblioteka.utils.exceptions import ReservationExpired


@pytest.fixture
def make_reservation():
    """
    Fabryka obiektów Reservation do testów.
    Przyjmuje opcjonalne parametry przez kwargs,
    domyślnie ustawia reservation_id, member_id, isbn i reserved_on.
    """
    def _make_reservation(**kwargs):
        defaults = {
            "reservation_id": "R1",
            "member_id": "M1",
            "isbn": "123",
            "reserved_on": date.today() - timedelta(days=2),
        }
        defaults.update(kwargs)
        return Reservation(**defaults)
    return _make_reservation


def test_initial_active_and_not_expired(make_reservation):
    """
    Nowa rezerwacja powinna być aktywna i nieprzeterminowana.
    """
    r = make_reservation(reserved_on=date.today())
    assert r.active
    assert not r.is_expired()


def test_expire_logic(make_reservation):
    """
    Gdy data reserved_on jest dalsza niż domyślny okres (7 dni),
    is_expired() zwraca True, a wywołanie expire() ustawia active=False.
    """
    r = make_reservation(reserved_on=date.today() - timedelta(days=10))
    assert r.is_expired()
    r.expire()
    assert not r.active


def test_cancel_pushes_active_false(make_reservation):
    """
    cancel() powinno dezaktywować rezerwację,
    ponowna próba anulowania rzuca ValueError.
    """
    r = make_reservation()
    r.cancel()
    assert not r.active
    with pytest.raises(ValueError):
        r.cancel()


def test_cancel_on_expired_raises(make_reservation):
    """
    Próba cancel() na już przeterminowanej rezerwacji
    powinna rzucić ReservationExpired.
    """
    r = make_reservation(reserved_on=date.today() - timedelta(days=20))
    with pytest.raises(ReservationExpired):
        r.cancel()


def test_expire_does_not_change_if_not_expired(make_reservation):
    """
    expire() na nieprzeterminowanej rezerwacji nie zmienia jej stanu.
    """
    r = make_reservation(reserved_on=date.today())
    r.expire()
    assert r.active


def test_cancel_after_expire_stays_inactive(make_reservation):
    """
    Wywołanie expire() na przeterminowanej rezerwacji ustawia active=False,
    a kolejne wywołanie expire() nie przywraca aktywności.
    """
    r = make_reservation(reserved_on=date.today() - timedelta(days=10))
    r.expire()
    assert not r.active
    r.expire()
    assert not r.active


def test_str_shows_state(make_reservation):
    """
    __str__() powinno zawierać informację
    o identyfikatorze i stanie rezerwacji:
    'active' gdy aktywna, 'inactive' po anulowaniu.
    """
    r = make_reservation()
    s1 = str(r)
    assert "active" in s1
    r.cancel()
    s2 = str(r)
    assert "inactive" in s2

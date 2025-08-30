import pytest
import unittest
from datetime import date, timedelta
from biblioteka.models.member import Member
from biblioteka.utils.exceptions import MembershipExpired


@pytest.fixture
def make_member():
    """
    Fabryka obiektów Member do testów.
    Umożliwia przekazanie parametrów przez kwargs,
    a domyślnie ustawia member_id, name i registered_on na dzisiaj.
    """
    def _make_member(**kwargs):
        defaults = {
            "member_id": "M1",
            "name": "Jan Kowalski",
            "registered_on": date.today(),
            "email": None,
            "phone": None,
        }
        defaults.update(kwargs)
        return Member(**defaults)
    return _make_member


def test_valid_email_and_phone(make_member):
    """
    Poprawny email i telefon powinny zostać przyjęte bez błędu
    i przypisane do obiektu.
    """
    m = make_member(email="a.b-c@d.pl", phone="+48123456789")
    assert m.email == "a.b-c@d.pl"
    assert m.phone == "+48123456789"


@pytest.mark.parametrize("email", ["blad@", "nie@prawidłowo", "aaa"])
def test_invalid_email_raises(email, make_member):
    """
    Niepoprawne adresy email powinny powodować ValueError w __post_init__.
    """
    with pytest.raises(ValueError):
        make_member(email=email)


@pytest.mark.parametrize("phone", ["123", "++48123", "telefon"])
def test_invalid_phone_raises(phone, make_member):
    """
    Niewłaściwy format numeru telefonu również powinien rzucać ValueError.
    """
    with pytest.raises(ValueError):
        make_member(phone=phone)


def test_is_membership_active_and_expiry(make_member):
    """
    is_membership_active() zwraca True, jeśli expiry >= dziś,
    oraz False, gdy expiry < dziś.
    """
    m_active = make_member()
    assert m_active.is_membership_active()

    m_expired = make_member(membership_expiry=date.today() - timedelta(days=1))
    assert not m_expired.is_membership_active()


def test_can_loan_and_limit(make_member):
    """
    Dodawanie kolejnych loan_id do current_loans aż do max_books,
    następnie add_loan() rzuca ValueError.
    """
    m = make_member()
    # wypełniamy listę po brzegi
    for i in range(m.max_books):
        m.current_loans.append(f"L{i}")
    with pytest.raises(ValueError):
        m.add_loan("LX")


def test_membership_expired_raises(make_member):
    """
    Jeśli membership_expiry < dziś, can_loan() rzuca MembershipExpired.
    """
    expired = make_member(membership_expiry=date.today() - timedelta(days=1))
    with pytest.raises(MembershipExpired):
        expired.can_loan()


def test_add_and_remove_loan(make_member):
    """
    add_loan() poprawnie dodaje loan_id,
    remove_loan() usuwa je z listy,
    a próba usunięcia nieistniejącego loan_id rzuca ValueError.
    """
    m = make_member()
    m.add_loan("L1")
    assert "L1" in m.current_loans
    m.remove_loan("L1")
    assert "L1" not in m.current_loans
    with pytest.raises(ValueError):
        m.remove_loan("L2")


def test_renew_membership_extends_expiry(make_member):
    """
    renew_membership() przesuwa datę expiry o podaną liczbę dni,
    gdy członkostwo jest nadal aktywne.
    """
    m = make_member()
    old_exp = m.membership_expiry
    m.renew_membership(30)
    assert m.membership_expiry == old_exp + timedelta(days=30)


def test_str_contains_id_and_name(make_member):
    """
    __str__() powinno zawierać member_id i name dla czytelnej prezentacji.
    """
    m = make_member()
    s = str(m)
    assert m.member_id in s and m.name in s


class TestMemberUnittest(unittest.TestCase):
    """
    Przykład testów unittest dla klasy Member.
    Używamy metod setUp oraz standardowych asercji.
    """
    def setUp(self):
        self.today = date.today()
        self.m = Member(member_id="U1", name="Test", registered_on=self.today)

    def test_str_contains_id_and_name_unittest(self):
        """
        Sprawdza, czy __str__() zwraca poprawne ID i nazwę użytkownika.
        """
        s = str(self.m)
        self.assertIn("U1", s)
        self.assertIn("Test", s)

    def test_remove_loan_updates_list(self):
        """
        remove_loan() usuwa istniejące loan_id z listy.
        """
        self.m.current_loans = ["L1"]
        self.m.remove_loan("L1")
        self.assertEqual(self.m.current_loans, [])


def test_renew_on_expired_member_resets_expiry(make_member):
    """
    Gdy członkostwo jest już przeterminowane,
    renew_membership() powinno ustawić expiry = dziś + extra_days.
    """
    past_date = date.today() - timedelta(days=10)
    m = make_member(membership_expiry=past_date)
    m.renew_membership(5)
    assert m.membership_expiry == date.today() + timedelta(days=5)


def test_add_loan_after_expiry_raises_membershipexpired(make_member):
    """
    Próba add_loan() na przeterminowanym członkostwie
    powinna rzucić MembershipExpired.
    """
    expired = make_member(membership_expiry=date.today() - timedelta(days=1))
    with pytest.raises(MembershipExpired):
        expired.add_loan("L100")

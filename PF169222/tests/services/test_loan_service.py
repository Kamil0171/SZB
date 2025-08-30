import pytest
from datetime import date, timedelta
from biblioteka.models.book import Book
from biblioteka.models.member import Member
from biblioteka.services.loan_service import LoanService
from biblioteka.storage.repository import Repository
from biblioteka.utils.exceptions import (
    BookNotAvailable,
    MemberNotFound,
    MaxRenewalsExceeded,
)


@pytest.fixture
def repo():
    return Repository()


@pytest.fixture
def loan_svc(repo):
    return LoanService(repo)


@pytest.fixture
def setup_book_member(repo):
    """
    Dodaje do repozytorium przykładową książkę i członka,
    aby przygotować środowisko do testów wypożyczeń.
    """
    book = Book(isbn="B1", title="T", author="A")
    member = Member(member_id="M1", name="X", registered_on=date.today())
    repo.add(book)
    repo.add(member)
    return book, member


def test_loan_book_success(loan_svc, repo, setup_book_member):
    loan = loan_svc.loan_book("M1", "B1")
    assert loan.member_id == "M1"
    assert not repo.get(Book, "B1").is_available()


def test_loan_nonexistent_member(loan_svc):
    with pytest.raises(MemberNotFound):
        loan_svc.loan_book("NOPE", "B1")


def test_loan_unavailable_book(loan_svc, repo):
    member = Member(member_id="M1", name="X", registered_on=date.today())
    repo.add(member)
    with pytest.raises(BookNotAvailable):
        loan_svc.loan_book("M1", "NOPE")


def test_return_book(loan_svc, repo, setup_book_member):
    loan = loan_svc.loan_book("M1", "B1")
    loan_svc.return_book(loan.loan_id)
    assert repo.get(Book, "B1").is_available()
    assert repo.get(Member, "M1").current_loans == []


def test_renew_within_limits(loan_svc, repo, setup_book_member):
    loan = loan_svc.loan_book("M1", "B1")
    old_due = loan.due_date
    renewed = loan_svc.renew_loan(loan.loan_id, extra_days=5)
    assert renewed.due_date == old_due + timedelta(days=5)


def test_renew_exceeds_limit(loan_svc, repo, setup_book_member):
    loan = loan_svc.loan_book("M1", "B1")
    loan.renew_count = 2
    with pytest.raises(MaxRenewalsExceeded):
        loan_svc.renew_loan(loan.loan_id)

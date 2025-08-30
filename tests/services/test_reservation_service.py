import pytest
from datetime import date, timedelta
from biblioteka.models.book import Book
from biblioteka.services.reservation_service import ReservationService
from biblioteka.storage.repository import Repository
from biblioteka.utils.exceptions import BookNotAvailable


@pytest.fixture
def repo():
    return Repository()


@pytest.fixture
def res_svc(repo):
    return ReservationService(repo)


@pytest.fixture
def setup_book(repo):
    book = Book(isbn="B1", title="T", author="A")
    repo.add(book)
    return book


def test_reserve_book_success(res_svc, repo, setup_book):
    res = res_svc.reserve_book("M1", "B1")
    assert res.active
    assert repo.get(Book, "B1").status.name == "RESERVED"


def test_reserve_unavailable_book(res_svc):
    with pytest.raises(BookNotAvailable):
        res_svc.reserve_book("M1", "NOPE")


def test_cancel_reservation(res_svc, repo, setup_book):
    r = res_svc.reserve_book("M1", "B1")
    res_svc.cancel_reservation(r.reservation_id)
    assert not repo.get(type(r), r.reservation_id).active
    assert repo.get(Book, "B1").is_available()


def test_expire_reservations(res_svc, repo, setup_book):
    r = res_svc.reserve_book("M1", "B1")
    past = date.today() - timedelta(days=10)
    r.reserved_on = past
    r.expiration_date = past
    expired = res_svc.expire_reservations()
    assert r in expired
    assert not r.active

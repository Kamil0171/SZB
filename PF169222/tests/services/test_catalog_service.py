import pytest
from biblioteka.models.book import Book
from biblioteka.services.catalog_service import CatalogService
from biblioteka.storage.repository import Repository
from biblioteka.utils.exceptions import PermissionDenied, BookNotAvailable


@pytest.fixture
def repo():
    return Repository()


@pytest.fixture
def catalog(repo):
    return CatalogService(repo)


@pytest.fixture
def sample_book():
    return Book(
        isbn="ISBN123",
        title="Pan Tadeusz",
        author="Mickiewicz",
        publication_year=1834,
        genre="epos",
        description="Klasyka literatury"
    )


def test_add_book_with_permission(catalog, repo, sample_book):
    catalog.add_book(sample_book, user_role="LIBRARIAN")
    assert repo.get(Book, "ISBN123") is sample_book


def test_add_book_without_permission(catalog, sample_book):
    with pytest.raises(PermissionDenied):
        catalog.add_book(sample_book, user_role="STUDENT")


def test_add_duplicate_book_raises(catalog, sample_book):
    catalog.add_book(sample_book, user_role="ADMIN")
    with pytest.raises(ValueError):
        catalog.add_book(sample_book, user_role="ADMIN")


def test_remove_book_success(catalog, repo, sample_book):
    catalog.add_book(sample_book, user_role="ADMIN")
    catalog.remove_book("ISBN123", user_role="LIBRARIAN")
    assert repo.get(Book, "ISBN123") is None


def test_remove_nonexistent_book(catalog):
    with pytest.raises(KeyError):
        catalog.remove_book("NOPE", user_role="ADMIN")


def test_remove_loaned_or_reserved_book(catalog, sample_book):
    catalog.add_book(sample_book, user_role="ADMIN")
    sample_book.mark_loaned()
    catalog.repo.update(sample_book)
    with pytest.raises(BookNotAvailable):
        catalog.remove_book(sample_book.isbn, user_role="ADMIN")


def test_update_book_info(catalog, sample_book):
    catalog.add_book(sample_book, user_role="ADMIN")
    updated = catalog.update_book_info(
        sample_book.isbn, title="Nowy Tytuł", genre="dramat"
    )
    assert updated.title == "Nowy Tytuł"
    assert updated.genre == "dramat"


def test_list_and_search(catalog, sample_book):
    other = Book(isbn="X2", title="Inna", author="Ktoś")
    catalog.add_book(sample_book, user_role="ADMIN")
    catalog.add_book(other, user_role="ADMIN")

    all_isbns = {b.isbn for b in catalog.list_all()}
    assert all_isbns == {"ISBN123", "X2"}

    by_author = catalog.list_by_author("Mickiewicz")
    assert [b.isbn for b in by_author] == ["ISBN123"]

    match = catalog.search_title_contains("Pan")
    assert match and match[0].isbn == "ISBN123"

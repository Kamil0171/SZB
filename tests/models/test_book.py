import pytest
from biblioteka.models.book import Book, BookStatus


@pytest.fixture
def sample_book():
    """
    Przygotowuje przykładowy obiekt Book do testów.
    Zwraca książkę o określonym ISBN,
    tytule i autorze oraz dodatkowych opcjach.
    """
    return Book(
        isbn="123-456",
        title="Tytuł",
        author="Autor",
        publication_year=2020,
        genre="Fantastyka",
        description="Opis",
        cover_url="http://okładka",
        location="Regał 1"
    )


def test_initial_status_available(sample_book):
    """
    Po utworzeniu książka powinna być dostępna (AVAILABLE).
    Metoda is_available() powinna zwracać True.
    """
    assert sample_book.status == BookStatus.AVAILABLE
    assert sample_book.is_available()


def test_mark_loaned_changes_status(sample_book):
    """
    Po wywołaniu mark_loaned() status powinien zmienić się na LOANED,
    a ponowna próba wypożyczenia powinna rzucić ValueError.
    """
    sample_book.mark_loaned()
    assert sample_book.status == BookStatus.LOANED
    assert not sample_book.is_available()
    with pytest.raises(ValueError):
        sample_book.mark_loaned()


def test_mark_reserved_changes_status(sample_book):
    """
    Po wywołaniu mark_reserved() status powinien być RESERVED,
    a kolejne mark_reserved() powinno rzucić ValueError.
    """
    sample_book.mark_reserved()
    assert sample_book.status == BookStatus.RESERVED
    with pytest.raises(ValueError):
        sample_book.mark_reserved()


def test_mark_returned_resets_status(sample_book):
    """
    Po wypożyczeniu (mark_loaned) i zwrocie (mark_returned)
    status powinien wrócić do AVAILABLE.
    """
    sample_book.mark_loaned()
    sample_book.mark_returned()
    assert sample_book.status == BookStatus.AVAILABLE


def test_update_info_only_overwrites_provided_fields(sample_book):
    """
    update_info() powinno nadpisać tylko przekazane argumenty,
    pozostałe pola pozostają niezmienione.
    """
    sample_book.update_info(title="Nowy", genre="Sci-Fi", location="Regał 2")
    assert sample_book.title == "Nowy"
    assert sample_book.genre == "Sci-Fi"
    assert sample_book.location == "Regał 2"
    # pola nieprzekazane pozostają bez zmian
    assert sample_book.author == "Autor"
    assert sample_book.publication_year == 2020


def test_update_info_with_no_fields(sample_book):
    """
    Jeśli nie podano żadnych argumentów, obiekt nie powinien ulec zmianie.
    """
    before = sample_book.__dict__.copy()
    sample_book.update_info()
    assert sample_book.__dict__ == before


def test_str_representation(sample_book):
    """
    __str__() powinno zawierać tytuł, autora oraz ISBN w odpowiednim formacie.
    """
    expected = (
        f"{sample_book.title} by {sample_book.author} "
        f"({sample_book.isbn})"
    )
    assert str(sample_book) == expected


def test_update_info_invalid_field_type_error(sample_book):
    """
    Próba przekazania niespodziewanego argumentu powinna rzucić TypeError.
    """
    with pytest.raises(TypeError):
        sample_book.update_info(nonexistent_field="value")


def test_multiple_transitions_are_blocked(sample_book):
    """
    Nie można wypożyczyć książki, która jest już zarezerwowana.
    """
    sample_book.mark_reserved()
    with pytest.raises(ValueError):
        sample_book.mark_loaned()

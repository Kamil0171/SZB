from typing import List, Optional
from biblioteka.storage.repository import Repository
from biblioteka.models.book import Book, BookStatus
from biblioteka.utils.exceptions import PermissionDenied, BookNotAvailable


class CatalogService:
    """
    Serwis odpowiedzialny za zarządzanie katalogiem książek:
    dodawanie, usuwanie, aktualizację metadanych oraz wyszukiwanie.
    """

    def __init__(self, repo: Repository):
        """
        Inicjalizuje serwis z przekazanym repozytorium,
        służącym do przechowywania obiektów Book.
        """
        self.repo = repo

    def add_book(self, book: Book, user_role: Optional[str] = None) -> None:
        """
        Dodaje nową książkę do katalogu.
        - Jeśli podano user_role,
        sprawdza uprawnienia (tylko LIBRARIAN i ADMIN).
        - Podnosi ValueError, gdy książka o danym ISBN już istnieje.
        """
        if user_role and user_role not in ("LIBRARIAN", "ADMIN"):
            raise PermissionDenied("Only librarian or admin can add books")
        if self.repo.get(Book, book.isbn):
            raise ValueError(f"Book with ISBN {book.isbn} already exists")
        self.repo.add(book)

    def remove_book(self, isbn: str, user_role: Optional[str] = None) -> None:
        """
        Usuwa książkę z katalogu.
        - Sprawdza uprawnienia podobnie jak w add_book.
        - Podnosi KeyError, gdy książka nie istnieje.
        - Podnosi BookNotAvailable,
        gdy książka nie jest dostępna (status != AVAILABLE).
        """
        if user_role and user_role not in ("LIBRARIAN", "ADMIN"):
            raise PermissionDenied("Only librarian or admin can remove books")
        book = self.repo.get(Book, isbn)
        if not book:
            raise KeyError(f"Book {isbn} not found")
        if book.status != BookStatus.AVAILABLE:
            raise BookNotAvailable(
                f"Cannot remove book {isbn} while status is {book.status.name}"
            )
        self.repo.delete(Book, isbn)

    def update_book_info(
        self,
        isbn: str,
        *,
        title: Optional[str] = None,
        author: Optional[str] = None,
        publication_year: Optional[int] = None,
        genre: Optional[str] = None,
        description: Optional[str] = None,
        cover_url: Optional[str] = None,
        location: Optional[str] = None
    ) -> Book:
        """
        Aktualizuje metadane istniejącej książki.
        - Podnosi KeyError, gdy książka o danym ISBN nie istnieje.
        - Zmienia tylko podane pola, zachowując resztę bez zmian.
        Zwraca zaktualizowany obiekt Book.
        """
        book = self.repo.get(Book, isbn)
        if not book:
            raise KeyError(f"Book {isbn} not found")
        book.update_info(
            title=title,
            author=author,
            year=publication_year,
            genre=genre,
            description=description,
            cover_url=cover_url,
            location=location
        )
        self.repo.update(book)
        return book

    def list_all(self) -> List[Book]:
        """
        Zwraca wszystkie książki z katalogu.
        """
        return self.repo.list(Book)

    def list_books(self) -> List[Book]:
        """
        Alias dla list_all, używany przez CLI.
        """
        return self.list_all()

    def list_available(self) -> List[Book]:
        """
        Zwraca tylko książki dostępne do wypożyczenia (status AVAILABLE).
        """
        return [b for b in self.repo.list(Book) if b.is_available()]

    def list_by_author(self, author: str) -> List[Book]:
        """
        Filtruje książki po autorze.
        """
        return self.repo.list(Book, author=author)

    def list_by_genre(self, genre: str) -> List[Book]:
        """
        Filtruje książki po gatunku.
        """
        return self.repo.list(Book, genre=genre)

    def search_title_contains(self, fragment: str) -> List[Book]:
        """
        Wyszukuje książki, których tytuł zawiera
        podany fragment (bez rozróżnienia wielkości liter).
        """
        all_books = self.repo.list(Book)
        return [b for b in all_books if fragment.lower() in b.title.lower()]

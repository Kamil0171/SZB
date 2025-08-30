from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class BookStatus(Enum):
    AVAILABLE = auto()
    LOANED = auto()
    RESERVED = auto()


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    location: Optional[str] = None
    status: BookStatus = BookStatus.AVAILABLE

    def is_available(self) -> bool:
        """Sprawdza, czy książka jest dostępna do wypożyczenia."""
        return self.status == BookStatus.AVAILABLE

    def mark_loaned(self) -> None:
        """
        Oznacza książkę jako wypożyczoną.
        Podnosi ValueError, jeśli książka nie jest aktualnie dostępna.
        """
        if not self.is_available():
            raise ValueError(f"Book {self.isbn} is not available for loan")
        self.status = BookStatus.LOANED

    def mark_reserved(self) -> None:
        """
        Oznacza książkę jako zarezerwowaną.
        Podnosi ValueError, jeśli książka nie jest aktualnie dostępna.
        """
        if self.status != BookStatus.AVAILABLE:
            raise ValueError(f"Book {self.isbn} cannot be reserved")
        self.status = BookStatus.RESERVED

    def mark_returned(self) -> None:
        """
        Resetuje status książki na dostępny
        (po zwrocie lub anulowaniu rezerwacji).
        """
        self.status = BookStatus.AVAILABLE

    def update_info(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[int] = None,
        genre: Optional[str] = None,
        description: Optional[str] = None,
        cover_url: Optional[str] = None,
        location: Optional[str] = None
    ) -> None:
        """
        Aktualizuje metadane książki.
        Nadpisuje tylko te pola, dla których przekazano nową wartość.
        """
        if title is not None:
            self.title = title
        if author is not None:
            self.author = author
        if year is not None:
            self.publication_year = year
        if genre is not None:
            self.genre = genre
        if description is not None:
            self.description = description
        if cover_url is not None:
            self.cover_url = cover_url
        if location is not None:
            self.location = location

    def __str__(self) -> str:
        """Zwraca reprezentację tekstową książki: 'Tytuł by Autor (ISBN)'."""
        return f"{self.title} by {self.author} ({self.isbn})"

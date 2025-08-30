from typing import Any, Type, Dict, List, Callable
import json
import os

from biblioteka.utils.exceptions import DataImportError, DataExportError
from biblioteka.models.book import Book


class Repository:
    """
    Prosta warstwa dostępu do danych w pamięci,
    z możliwością eksportu/importu do pliku JSON.
    Przechowuje dane w strukturze: {Klasa: {klucz: obiekt, ...}, ...}
    """

    def __init__(self):
        # Inicjalizuje puste repozytorium
        self._data: Dict[Type, Dict[str, Any]] = {}

    def add(self, obj: Any) -> None:
        """
        Dodaje nowy obiekt do repozytorium.
        Klucz wyznaczany jest dynamicznie (_get_pk).
        Podnosi KeyError, jeśli rekord o tym kluczu już istnieje.
        """
        cls_ = type(obj)
        table = self._data.setdefault(cls_, {})
        key = self._get_pk(obj)
        if key in table:
            raise KeyError(f"{cls_.__name__} with key {key} already exists")
        table[key] = obj

    def get(self, cls: Type, pk: str) -> Any:
        """
        Zwraca obiekt danego typu o podanym kluczu.
        Jeśli nie istnieje, zwraca None.
        """
        return self._data.get(cls, {}).get(pk)

    def list(self, cls: Type, **filters) -> List[Any]:
        """
        Zwraca wszystkie obiekty danego typu.
        Jeśli podano filtry (atrybut=wartość), zwraca tylko obiekty,
        których atrybuty dokładnie pasują do filtrów.
        """
        result = list(self._data.get(cls, {}).values())
        for attr, value in filters.items():
            result = [obj for obj in result if getattr(obj, attr) == value]
        return result

    def list_books(self) -> List[Book]:
        """
        Zwraca wszystkie obiekty Book z repozytorium.
        Alias dla list(Book).
        """
        return self.list(Book)

    def update(self, obj: Any) -> None:
        """
        Nadpisuje istniejący obiekt w repozytorium.
        Klucz wyznaczany jest tak jak w add().
        Podnosi KeyError, jeśli obiekt nie istnieje.
        """
        cls_ = type(obj)
        table = self._data.get(cls_, {})
        key = self._get_pk(obj)
        if key not in table:
            raise KeyError(f"{cls_.__name__} with key {key} not found")
        table[key] = obj

    def delete(self, cls: Type, pk: str) -> None:
        """
        Usuwa obiekt danego typu o kluczu pk.
        Podnosi KeyError, jeśli rekord nie istnieje.
        """
        table = self._data.get(cls, {})
        if pk not in table:
            raise KeyError(f"{cls.__name__} with key {pk} not found")
        del table[pk]

    def clear(self, cls: Type = None) -> None:
        """
        Czyści repozytorium:
        - Jeśli podano cls, usuwa tylko dane dla tej klasy.
        - W przeciwnym razie czyści wszystkie dane.
        """
        if cls:
            self._data.pop(cls, None)
        else:
            self._data.clear()

    def count(self, cls: Type = None) -> int:
        """
        Zwraca liczbę:
        - wszystkich rekordów, jeśli cls=None,
        - lub rekordów danej klasy, jeśli cls podano.
        """
        if cls:
            return len(self._data.get(cls, {}))
        return sum(len(tbl) for tbl in self._data.values())

    def export_to_json(self, cls: Type, filepath: str) -> None:
        """
        Eksportuje wszystkie obiekty danej klasy do pliku JSON.
        Obiekt musi być dataclassą lub mieć __dict__.
        Jeśli wystąpi błąd operacji, podnosi DataExportError.
        """
        try:
            data = []
            for obj in self.list(cls):
                if hasattr(obj, "__dict__"):
                    data.append(obj.__dict__)
                else:
                    raise TypeError(
                        f"Cannot serialize object of type {type(obj).__name__}"
                    )
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            raise DataExportError(
                f"Failed to export {cls.__name__} "
                f"to {filepath}: {e}"
            ) from e

    def import_from_json(
            self,
            cls: Type,
            filepath: str,
            factory: Callable[[dict], Any],
    ) -> None:
        """
        Importuje dane z pliku JSON:
        - Sprawdza istnienie pliku, inaczej podnosi DataImportError.
        - Wczytuje listę słowników, tworzy obiekty przez factory(rec).
        - Czyści wcześniejsze dane i dodaje nowe.
        Jeśli wystąpi błąd parsowania lub
        tworzenia obiektów, podnosi DataImportError.
        """
        if not os.path.isfile(filepath):
            raise DataImportError(f"No such file: {filepath}")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                records = json.load(f)
            self.clear(cls)
            for rec in records:
                obj = factory(rec)
                self.add(obj)
        except Exception as e:
            raise DataImportError(
                f"Failed to import {cls.__name__} "
                f"from {filepath}: {e}"
            ) from e

    def find_by_pattern(self, cls: Type, attr: str, pattern: str) -> List[Any]:
        """
        Wyszukuje obiekty, których wartość
        atrybutu attr (str) zawiera fragment pattern.
        Porównanie ignoruje wielkość liter.
        """
        result = []
        for obj in self.list(cls):
            value = getattr(obj, attr, "")
            if isinstance(value, str) and pattern.lower() in value.lower():
                result.append(obj)
        return result

    @staticmethod
    def _get_pk(obj: Any) -> str:
        """
        Wydobywa wartość klucza głównego z obiektu:
        próbuje kolejno atrybuty: loan_id,
        reservation_id, user_id, member_id, isbn.
        Podnosi ValueError, jeśli żaden klucz nie istnieje.
        """
        for attr in (
                "loan_id",
                "reservation_id",
                "user_id",
                "member_id",
                "isbn",
        ):
            if hasattr(obj, attr):
                return getattr(obj, attr)
        raise ValueError(f"Unsupported object type {type(obj).__name__}")

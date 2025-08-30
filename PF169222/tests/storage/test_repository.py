import pytest
import json
from dataclasses import dataclass

from biblioteka.storage.repository import Repository
from biblioteka.utils.exceptions import DataExportError, DataImportError
from biblioteka.models.book import Book


@dataclass
class Dummy:
    user_id: str
    value: int


@pytest.fixture
def repo():
    return Repository()


def test_add_get_list_update_delete_count_clear(repo):
    d1 = Dummy(user_id="U1", value=10)
    d2 = Dummy(user_id="U2", value=20)

    repo.add(d1)
    assert repo.get(Dummy, "U1") is d1

    with pytest.raises(KeyError):
        repo.add(d1)

    repo.add(d2)
    all_objs = repo.list(Dummy)
    assert set(o.user_id for o in all_objs) == {"U1", "U2"}

    assert repo.count(Dummy) == 2
    assert repo.count() >= 2

    d1.value = 99
    repo.update(d1)
    assert repo.get(Dummy, "U1").value == 99

    d3 = Dummy(user_id="U3", value=0)
    with pytest.raises(KeyError):
        repo.update(d3)

    repo.delete(Dummy, "U2")
    assert repo.get(Dummy, "U2") is None

    with pytest.raises(KeyError):
        repo.delete(Dummy, "NOPE")

    repo.clear(Dummy)
    assert repo.count(Dummy) == 0

    repo.add(Dummy(user_id="X1", value=1))
    repo.add(Book(isbn="B1", title="T", author="A"))
    repo.clear()
    assert repo.count() == 0


def test_list_with_filters(repo):
    @dataclass
    class Item:
        isbn: str
        category: str

    i1 = Item(isbn="A1", category="alpha")
    i2 = Item(isbn="B1", category="beta")
    repo.add(i1)
    repo.add(i2)

    filtered = repo.list(Item, category="alpha")
    assert filtered == [i1]
    assert repo.list(Item, category="gamma") == []


def test_export_to_json_and_import(tmp_path, repo):
    d1 = Dummy(user_id="U1", value=5)
    d2 = Dummy(user_id="U2", value=8)
    repo.add(d1)
    repo.add(d2)

    filepath = tmp_path / "dummy.json"
    repo.export_to_json(Dummy, str(filepath))
    assert filepath.exists()

    data = json.loads(filepath.read_text())
    assert isinstance(data, list)
    assert any(rec["user_id"] == "U1" for rec in data)

    repo.clear(Dummy)

    def factory(rec: dict) -> Dummy:
        return Dummy(user_id=rec["user_id"], value=rec["value"])
    repo.import_from_json(Dummy, str(filepath), factory)
    assert repo.count(Dummy) == 2
    assert repo.get(Dummy, "U2").value == 8


def test_export_to_json_error(tmp_path, repo):
    bad_path = tmp_path / "no" / "dir" / "out.json"
    with pytest.raises(DataExportError):
        repo.export_to_json(Dummy, str(bad_path))


def test_import_from_json_missing_or_bad(tmp_path, repo):
    missing = tmp_path / "nofile.json"
    with pytest.raises(DataImportError):
        repo.import_from_json(Dummy, str(missing), lambda rec: Dummy(**rec))

    bad = tmp_path / "bad.json"
    bad.write_text("not a valid json")
    with pytest.raises(DataImportError):
        repo.import_from_json(Dummy, str(bad), lambda rec: Dummy(**rec))


def test_import_factory_error(tmp_path, repo):
    d = Dummy(user_id="U1", value=10)
    repo.add(d)
    filepath = tmp_path / "dummy.json"
    repo.export_to_json(Dummy, str(filepath))
    repo.clear(Dummy)

    def bad_factory(rec: dict):
        raise ValueError("factory fail")
    with pytest.raises(DataImportError):
        repo.import_from_json(Dummy, str(filepath), bad_factory)


def test_find_by_pattern(repo):
    b1 = Book(isbn="1", title="Alpha One", author="A")
    b2 = Book(isbn="2", title="Beta Two", author="B")
    repo.add(b1)
    repo.add(b2)

    matches = repo.find_by_pattern(Book, "title", "alpha")
    assert matches == [b1]
    assert repo.find_by_pattern(Book, "title", "gamma") == []
    assert repo.find_by_pattern(Book, "nonexistent", "x") == []


def test_find_by_pattern_non_string(repo):
    class Item:
        def __init__(self, isbn, number):
            self.isbn = isbn
            self.number = number

    i = Item("X", 123)
    repo.add(i)
    assert repo.find_by_pattern(Item, "number", "123") == []

import pytest
from biblioteka.utils.exceptions import (
    BookNotAvailable,
    MemberNotFound,
    UserNotFound,
    PermissionDenied,
    MembershipExpired,
    MaxRenewalsExceeded,
    ReservationExpired,
    DataImportError,
    DataExportError,
)

ALL_EXCS = [
    BookNotAvailable,
    MemberNotFound,
    UserNotFound,
    PermissionDenied,
    MembershipExpired,
    MaxRenewalsExceeded,
    ReservationExpired,
    DataImportError,
    DataExportError,
]


def test_all_exceptions_are_subclasses_of_Exception():
    for exc in ALL_EXCS:
        assert issubclass(exc, Exception), (
            f"{exc.__name__} "
            f"powinien dziedziczyć po Exception"
        )


@pytest.mark.parametrize("exc_cls,arg", [
    (BookNotAvailable, "B1"),
    (MemberNotFound, "M1"),
    (UserNotFound, "U1"),
    (PermissionDenied, "loan"),
    (MembershipExpired, "expired"),
    (MaxRenewalsExceeded, "renew"),
    (ReservationExpired, "R1"),
    (DataImportError, "import"),
    (DataExportError, "export"),
])
def test_exception_message_contains_argument(exc_cls, arg):
    """
    Sprawdza, czy przekazany tekst wiadomości
    pojawia się w opisie wyjątku po jego podniesieniu.
    """
    msg = f"test-{arg}"
    with pytest.raises(exc_cls) as ei:
        raise exc_cls(msg)
    assert msg in str(ei.value)


def test_chaining_exceptions_preserves_context():
    """
    Weryfikuje, że przy zagnieżdżaniu wyjątków (raise ... from ...)
    zachowywany jest kontekst pierwotnego wyjątku jako __cause__.
    """
    try:
        raise MemberNotFound("brak")
    except MemberNotFound as e:
        with pytest.raises(PermissionDenied) as ei:
            raise PermissionDenied("brak uprawnień") from e
        assert ei.value.__cause__ is e

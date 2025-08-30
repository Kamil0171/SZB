class BookNotAvailable(Exception):
    """
    Podnoszony, gdy próba wypożyczenia lub rezerwacji książki
    nie może zostać zrealizowana, ponieważ książka nie jest dostępna.
    """
    pass


class MemberNotFound(Exception):
    """
    Podnoszony, gdy nie znaleziono członka o wskazanym identyfikatorze.
    """
    pass


class UserNotFound(Exception):
    """
    Podnoszony, gdy nie znaleziono użytkownika o wskazanym identyfikatorze.
    """
    pass


class PermissionDenied(Exception):
    """
    Podnoszony, gdy użytkownik nie ma odpowiednich uprawnień
    do wykonania danej operacji.
    """
    pass


class MembershipExpired(Exception):
    """
    Podnoszony, gdy operacja związana z członkostwem
    nie może być wykonana, ponieważ członkostwo wygasło.
    """
    pass


class MaxRenewalsExceeded(Exception):
    """
    Podnoszony, gdy próba odnowienia wypożyczenia przekracza
    maksymalną liczbę dozwolonych odnowień.
    """
    pass


class ReservationExpired(Exception):
    """
    Podnoszony, gdy próba anulowania rezerwacji nie powiodła się,
    ponieważ rezerwacja już wygasła.
    """
    pass


class DataImportError(Exception):
    """
    Podnoszony, gdy import danych z pliku JSON kończy się błędem,
    np. plik nie istnieje lub zawartość jest niepoprawna.
    """
    pass


class DataExportError(Exception):
    """
    Podnoszony, gdy eksport danych do pliku JSON kończy się błędem,
    np. problem z zapisem pliku lub serializacją obiektów.
    """
    pass

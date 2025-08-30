# System Zarządzania Biblioteką

![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Funkcjonalności

* **Zarządzanie książkami**

  * Dodawanie, usuwanie, aktualizacja metadanych (ISBN, tytuł, autor, rok wydania, gatunek, opis, okładka, lokalizacja)
  * Listowanie wszystkich książek
* **Zarządzanie członkami**

  * Rejestracja członków z unikalnym `member_id` i danymi kontaktowymi
  * Sprawdzanie aktywności członkostwa
* **Obsługa wypożyczeń**

  * Wypożyczenie i zwrot książek
  * Odnowienie oraz anulowanie wypożyczeń
  * Oznaczanie dostępności książek
* **Obsługa rezerwacji**

  * Tworzenie i anulowanie rezerwacji
  * Wygaszanie przeterminowanych rezerwacji
* **Zarządzanie użytkownikami**

  * Tworzenie kont z rolami (GUEST, STUDENT, LIBRARIAN, ADMIN)
  * Zmiana ról, aktywacja, dezaktywacja i logowanie użytkowników
* **Trwałe przechowywanie danych** w plikach JSON (konfigurowalne przez zmienne środowiskowe)

## Struktura projektu

```
PF169222/
├── src/
│   └── biblioteka/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── book.py
│       │   ├── member.py
│       │   ├── loan.py
│       │   ├── reservation.py
│       │   └── user.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── catalog_service.py
│       │   ├── member_service.py
│       │   ├── loan_service.py
│       │   ├── reservation_service.py
│       │   └── user_service.py
│       ├── storage/
│       │   ├── __init__.py
│       │   └── repository.py
│       └── utils/
│           ├── __init__.py
│           └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_cli.py
│   ├── models/
│   │   ├── test_book.py
│   │   ├── test_loan.py
│   │   ├── test_member.py
│   │   ├── test_reservation.py
│   │   └── test_user.py
│   ├── services/
│   │   ├── test_catalog_service.py
│   │   ├── test_loan_service.py
│   │   ├── test_member_service.py
│   │   ├── test_reservation_service.py
│   │   └── test_user_service.py
│   ├── storage/
│   │   └── test_repository.py
│   └── utils/
│       └── test_exceptions.py
├── README.md
├── requirements.txt
└── setup.py
```

## Instalacja

1. Sklonuj repozytorium

2. Zainstaluj zależności

```bash
pip install -r requirements.txt
pip install -e .
```

## Uruchamianie testów

```bash
pytest
pytest --cov=src/biblioteka tests/
```

Aby wygenerować raport pokrycia kodu w HTML:

```bash
coverage run -m pytest
coverage html
```

## Udane testy
```
pytest
=============================================================================== test session starts ===============================================================================
platform win32 -- Python 3.12.3, pytest-8.3.5, pluggy-1.5.0
rootdir: D:\PythonProjects\PF169222
plugins: cov-6.1.1
collected 117 items                                                                                                                                                                

tests\models\test_book.py .........                                                                                                                                          [  7%]
tests\models\test_loan.py ........                                                                                                                                           [ 14%] 
tests\models\test_member.py .................                                                                                                                                [ 29%]
tests\models\test_reservation.py .......                                                                                                                                     [ 35%] 
tests\models\test_user.py .......                                                                                                                                            [ 41%]
tests\services\test_catalog_service.py ........                                                                                                                              [ 47%]
tests\services\test_loan_service.py ......                                                                                                                                   [ 52%] 
tests\services\test_member_service.py .......                                                                                                                                [ 58%]
tests\services\test_reservation_service.py ....                                                                                                                              [ 62%] 
tests\services\test_user_service.py .....                                                                                                                                    [ 66%]
tests\storage\test_repository.py ........                                                                                                                                    [ 73%]
tests\test_cli.py ....................                                                                                                                                       [ 90%]
tests\utils\test_exceptions.py ...........                                                                                                                                   [100%] 

=============================================================================== 117 passed in 0.34s =============================================================================== 
```

## Pokrycie kodu
```
Name                                             Stmts   Miss  Cover
--------------------------------------------------------------------
src\biblioteka\__init__.py                           6      0   100%
src\biblioteka\cli.py                              236     74    69%
src\biblioteka\config.py                             5      0   100%
src\biblioteka\models\__init__.py                    6      0   100%
src\biblioteka\models\book.py                       47      4    91%
src\biblioteka\models\loan.py                       31      0   100%
src\biblioteka\models\member.py                     43      0   100%
src\biblioteka\models\reservation.py                28      0   100%
src\biblioteka\models\user.py                       39      2    95%
src\biblioteka\services\__init__.py                  6      0   100%
src\biblioteka\services\catalog_service.py          42      5    88%
src\biblioteka\services\loan_service.py             67     13    81%
src\biblioteka\services\member_service.py           45      9    80%
src\biblioteka\services\reservation_service.py      42      3    93%
src\biblioteka\services\user_service.py             53      5    91%
src\biblioteka\storage\__init__.py                   2      0   100%
src\biblioteka\storage\repository.py                80      3    96%
src\biblioteka\utils\__init__.py                     2      0   100%
src\biblioteka\utils\exceptions.py                  18      0   100%
--------------------------------------------------------------------
TOTAL                                              798    118    85%
```

## Przykładowe użycie

```bash
# 1) Dodajemy dwie książki
biblioteka add-book --isbn 9780140449112 --title "Pan Tadeusz" --author "Adam Mickiewicz" --year 1834 --genre "poemat" --location "A1"
biblioteka add-book --isbn 9788373272449 --title "Lalka" --author "Bolesław Prus" --year 1890 --genre "powieść" --location "B2"

# 2) Wyświetlamy katalog książek
biblioteka list-books

# 3) Rejestrujemy członków
biblioteka register-member --member-id M001 --name "Jan Kowalski"
biblioteka register-member --member-id M002 --name "Maria Nowak" --email "maria@ex.pl" --phone "+48111222333"

# 4) Wypożyczanie
biblioteka loan-book --member-id M001 --isbn 9780140449112   # zapamiętaj <LOAN1_ID>
biblioteka loan-book --member-id M002 --isbn 9780140449112   # powinno się nie udać wyrzucić error
 
# 5) Zwrot
biblioteka return-book --loan-id <LOAN1_ID>

# 6) Odnowienie i anulowanie wypożyczenia
biblioteka loan-book --member-id M001 --isbn 9780140449112   # zapamiętaj <LOAN2_ID>
biblioteka renew-loan --loan-id <LOAN2_ID> --extra-days 14
biblioteka cancel-loan --loan-id <LOAN2_ID>

# 7) Rezerwacje
biblioteka reserve-book --member-id M002 --isbn 9788373272449  # zapamiętaj <RES1_ID>
biblioteka cancel-reservation --reservation-id <RES1_ID>
biblioteka expire-reservations

# 8) Zarządzanie użytkownikami
biblioteka create-user --name root --role ADMIN            # zapamiętaj <ROOT_ID>
biblioteka create-user --name bob  --role STUDENT          # zapamiętaj <BOB_ID>
biblioteka change-role --admin-id <ROOT_ID> --target-id <BOB_ID> --role LIBRARIAN
biblioteka deactivate-user --admin-id <ROOT_ID> --target-id <BOB_ID>
biblioteka activate-user   --admin-id <ROOT_ID> --target-id <BOB_ID>
```

import os
import argparse
from datetime import date, datetime

from biblioteka.storage.repository import Repository
from biblioteka.services import (
    CatalogService,
    MemberService,
    LoanService,
    ReservationService,
    UserService,
)
from biblioteka.models import Book, Member, Role, Loan, User
from biblioteka.models.reservation import Reservation
from biblioteka.models.book import BookStatus
from biblioteka.utils.exceptions import DataImportError


DATA_BOOK_FILE = os.getenv("BIB_BOOK_DATA_FILE", "biblioteka_books.json")
DATA_MEMBER_FILE = os.getenv("BIB_MEMBER_DATA_FILE", "biblioteka_members.json")
DATA_LOAN_FILE = os.getenv("BIB_LOAN_DATA_FILE", "biblioteka_loans.json")
DATA_RESERVATION_FILE = os.getenv(
    "BIB_RESERVATION_DATA_FILE",
    "biblioteka_reservations.json",
)
DATA_USER_FILE = os.getenv("BIB_USER_DATA_FILE", "biblioteka_users.json")


def book_factory(rec: dict) -> Book:
    rec = rec.copy()
    status_val = rec.pop("status", None)
    book = Book(**rec)
    if status_val:
        key = status_val.split('.')[-1]
        book.status = BookStatus[key]
    return book


def member_factory(rec: dict) -> Member:
    rec = rec.copy()
    rec["registered_on"] = date.fromisoformat(rec["registered_on"])
    rec["membership_expiry"] = date.fromisoformat(rec["membership_expiry"])
    current = rec.pop("current_loans", [])
    member = Member(**rec)
    member.current_loans = current
    return member


def loan_factory(rec: dict) -> Loan:
    rec = rec.copy()
    rec["loan_date"] = date.fromisoformat(rec["loan_date"])
    rec["due_date"] = date.fromisoformat(rec["due_date"])
    if rec.get("returned_on"):
        rec["returned_on"] = date.fromisoformat(rec["returned_on"])
    return Loan(**rec)


def reservation_factory(rec: dict) -> Reservation:
    rec = rec.copy()
    rec["reserved_on"] = date.fromisoformat(rec["reserved_on"])
    rec.pop("expiration_date", None)
    rec.pop("active", None)
    rec.pop("cancelled_on", None)
    rec.pop("expired_on", None)
    return Reservation(**rec)


def user_factory(rec: dict) -> User:
    rec = rec.copy()
    raw_role = rec.get("role")
    if isinstance(raw_role, str):
        key = raw_role.split('.')[-1]
        rec["role"] = Role[key]
    rec["joined_on"] = datetime.fromisoformat(rec["joined_on"])
    if rec.get("last_login"):
        rec["last_login"] = datetime.fromisoformat(rec["last_login"])
    return User(**rec)


def main():
    parser = argparse.ArgumentParser(
        description="System zarządzania biblioteką",
    )
    subparsers = parser.add_subparsers(dest="command")


    p_add = subparsers.add_parser("add-book", help="Dodaj książkę")
    p_add.add_argument("--isbn", required=True)
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--author", required=True)
    p_add.add_argument("--year", type=int, dest="publication_year")
    p_add.add_argument("--genre")
    p_add.add_argument("--description")
    p_add.add_argument("--cover-url")
    p_add.add_argument("--location")


    subparsers.add_parser("list-books", help="Wyświetl wszystkie książki")


    p_reg = subparsers.add_parser(
        "register-member",
        help="Zarejestruj nowego członka",
    )
    p_reg.add_argument("--member-id", required=True)
    p_reg.add_argument("--name", required=True)
    p_reg.add_argument("--email")
    p_reg.add_argument("--phone")


    p_loan = subparsers.add_parser("loan-book", help="Wypożycz książkę")
    p_loan.add_argument("--member-id", required=True)
    p_loan.add_argument("--isbn", required=True)


    p_ret = subparsers.add_parser("return-book", help="Zwróć książkę")
    p_ret.add_argument("--loan-id", required=True)


    p_renew = subparsers.add_parser(
        "renew-loan",
        help="Odnowienie wypożyczenia",
    )
    p_renew.add_argument("--loan-id", required=True)
    p_renew.add_argument("--extra-days", type=int, default=7)


    p_cancel_loan = subparsers.add_parser(
        "cancel-loan",
        help="Anuluj wypożyczenie",
    )
    p_cancel_loan.add_argument("--loan-id", required=True)


    p_res = subparsers.add_parser("reserve-book", help="Zarezerwuj książkę")
    p_res.add_argument("--member-id", required=True)
    p_res.add_argument("--isbn", required=True)


    p_cancel = subparsers.add_parser(
        "cancel-reservation",
        help="Anuluj rezerwację",
    )
    p_cancel.add_argument("--reservation-id", required=True)


    subparsers.add_parser(
        "expire-reservations",
        help="Wygaszenie przeterminowanych rezerwacji",
    )


    p_user = subparsers.add_parser("create-user", help="Utwórz użytkownika")
    p_user.add_argument("--name", required=True)
    p_user.add_argument(
        "--role",
        choices=[r.name for r in Role],
        required=True,
    )


    p_cr = subparsers.add_parser("change-role", help="Zmień rolę użytkownika")
    p_cr.add_argument("--admin-id", required=True)
    p_cr.add_argument("--target-id", required=True)
    p_cr.add_argument("--role", choices=[r.name for r in Role], required=True)


    p_deact = subparsers.add_parser(
        "deactivate-user",
        help="Dezaktywuj użytkownika",
    )
    p_deact.add_argument("--admin-id", required=True)
    p_deact.add_argument("--target-id", required=True)


    p_act = subparsers.add_parser("activate-user", help="Aktywuj użytkownika")
    p_act.add_argument("--admin-id", required=True)
    p_act.add_argument("--target-id", required=True)


    p_login = subparsers.add_parser("login-user", help="Zaloguj użytkownika")
    p_login.add_argument("--user-id", required=True)

    args = parser.parse_args()


    repo = Repository()
    for model, factory, path in [
        (Book, book_factory, DATA_BOOK_FILE),
        (Member, member_factory, DATA_MEMBER_FILE),
        (Loan, loan_factory, DATA_LOAN_FILE),
        (Reservation, reservation_factory, DATA_RESERVATION_FILE),
        (User, user_factory, DATA_USER_FILE),
    ]:
        try:
            repo.import_from_json(model, path, factory)
        except DataImportError:
            pass


    catalog = CatalogService(repo)
    member_svc = MemberService(repo)
    loan_svc = LoanService(repo)
    res_svc = ReservationService(repo)
    user_svc = UserService(repo)

    match args.command:
        case "add-book":
            book = Book(
                isbn=args.isbn,
                title=args.title,
                author=args.author,
                publication_year=args.publication_year,
                genre=args.genre,
                description=args.description,
                cover_url=args.cover_url,
                location=args.location
            )
            try:
                catalog.add_book(book)
                repo.export_to_json(Book, DATA_BOOK_FILE)
                print(f"Added book {book.isbn}")
            except ValueError as e:
                print(f"Error: {e}")

        case "list-books":
            for b in catalog.list_books():
                print(f"{b.isbn}: {b.title} — {b.author}")

        case "register-member":
            member = Member(
                member_id=args.member_id,
                name=args.name,
                registered_on=date.today(),
                email=args.email,
                phone=args.phone
            )
            try:
                member_svc.register_member(member)
                repo.export_to_json(Member, DATA_MEMBER_FILE)
                print(f"Registered member {member.member_id}")
            except ValueError as e:
                print(f"Error: {e}")

        case "loan-book":
            try:
                loan = loan_svc.loan_book(args.member_id, args.isbn)
                repo.export_to_json(Loan, DATA_LOAN_FILE)
                repo.export_to_json(Member, DATA_MEMBER_FILE)
                repo.export_to_json(Book, DATA_BOOK_FILE)
                print(f"Loan created: {loan.loan_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "return-book":
            try:
                loan_svc.return_book(args.loan_id)
                repo.export_to_json(Loan, DATA_LOAN_FILE)
                repo.export_to_json(Member, DATA_MEMBER_FILE)
                repo.export_to_json(Book, DATA_BOOK_FILE)
                print(f"Returned loan {args.loan_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "renew-loan":
            try:
                renewed = loan_svc.renew_loan(
                    args.loan_id,
                    extra_days=args.extra_days,
                )
                repo.export_to_json(Loan, DATA_LOAN_FILE)
                print(
                    f"Renewed loan {renewed.loan_id}, "
                    f"new due date {renewed.due_date}"
                )
            except Exception as e:
                print(f"Error: {e}")

        case "cancel-loan":
            try:
                loan_svc.cancel_loan(args.loan_id)
                repo.export_to_json(Loan, DATA_LOAN_FILE)
                repo.export_to_json(Book, DATA_BOOK_FILE)
                print(f"Cancelled loan {args.loan_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "reserve-book":
            try:
                res = res_svc.reserve_book(args.member_id, args.isbn)
                repo.export_to_json(Reservation, DATA_RESERVATION_FILE)
                repo.export_to_json(Book, DATA_BOOK_FILE)
                print(f"Reserved book: {res.reservation_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "cancel-reservation":
            try:
                try:
                    repo.import_from_json(
                        Reservation,
                        DATA_RESERVATION_FILE,
                        reservation_factory,
                    )
                except DataImportError:
                    pass

                res_svc.cancel_reservation(args.reservation_id)
                repo.export_to_json(Reservation, DATA_RESERVATION_FILE)
                repo.export_to_json(Book, DATA_BOOK_FILE)
                print(f"Canceled reservation {args.reservation_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "expire-reservations":
            try:
                expired = res_svc.expire_reservations()
                repo.export_to_json(Reservation, DATA_RESERVATION_FILE)
                repo.export_to_json(Book, DATA_BOOK_FILE)
                print(f"Expired {len(expired)} reservations")
            except Exception as e:
                print(f"Error: {e}")

        case "create-user":
            try:
                user = user_svc.create_user(args.name, Role[args.role])
                repo.export_to_json(User, DATA_USER_FILE)
                print(f"Created user: {user.user_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "change-role":
            try:
                user = user_svc.change_role(
                    args.admin_id,
                    args.target_id,
                    Role[args.role],
                )
                repo.export_to_json(User, DATA_USER_FILE)
                print(f"Changed role for {user.user_id} to {user.role.name}")
            except Exception as e:
                print(f"Error: {e}")

        case "deactivate-user":
            try:
                user = user_svc.deactivate_user(args.admin_id, args.target_id)
                repo.export_to_json(User, DATA_USER_FILE)
                print(f"Deactivated user: {user.user_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "activate-user":
            try:
                user = user_svc.activate_user(args.admin_id, args.target_id)
                repo.export_to_json(User, DATA_USER_FILE)
                print(f"Activated user: {user.user_id}")
            except Exception as e:
                print(f"Error: {e}")

        case "login-user":
            try:
                user = user_svc.login_user(args.user_id)
                repo.export_to_json(User, DATA_USER_FILE)
                print(f"User {user.user_id} logged in at {user.last_login}")
            except Exception as e:
                print(f"Error: {e}")

        case _:
            parser.print_help()


if __name__ == "__main__":
    main()

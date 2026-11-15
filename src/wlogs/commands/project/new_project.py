from wlogs.utils.crud import post_record


# get input from user
def get_book_details(code):
    book = {"code": code}
    book["title"] = input("Enter book title: ")
    book["series"] = input("Enter series title (enter to skip): ")
    book["goal"] = input("Enter book word count goal (default 100,000): ")
    if not book["goal"]:
        book["goal"] = 100000
    return book


def add_new_book(args):
    book = get_book_details(args.code)
    post_record(book, "projects")


def parse_new_project(project_subparsers):
    book_parser = project_subparsers.add_parser("add")
    book_parser.add_argument(
        "--code", "-c", required=True, help="Code for the new book."
    )
    book_parser.set_defaults(func=add_new_book)

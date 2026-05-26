from .library import *
def session_status(_):
  if session_in_progress():
      print(f"Current session:")
      print_dict(load_session_data())
  else:
      print("No session currently running.")

def parse_session_status(session_subparsers):
    status_parser = session_subparsers.add_parser("status", help="Show the currently running session")
    status_parser.set_defaults(func=session_status)
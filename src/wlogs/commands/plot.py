import sys
import pandas as pd

from wlogs.library.dates import print_list_dict

pd.set_option("display.max_rows", 100)
from wlogs import load_config
from wlogs.library.api.auth import send_auth_request


def get_plotter(book_code):
    request = {
        "method": "GET",
        "endpoint": f"{load_config()['api_url']}/projects/plotter/{book_code}",
    }
    res = send_auth_request(request)
    if 200 <= res.status_code < 300:
        return res.json()
    elif res.status_code == 404:
        print("Book not found.")
        sys.exit(1)
    else:
        print(f"Error: ", res.status_code, res.reason, res.reason)
        sys.exit(1)

def show_plotter(args):
    plotter = get_plotter(args.book)
    if args.plotline:
        plotter = [sc for sc in plotter if sc['plotline'] == args.plotline]
    if args.act:
        print(args, plotter[0]['pot'])
        quarter = 25
        max_pot = int(args.act) * quarter
        min_pot = max_pot - quarter
        plotter = [sc for sc in plotter if min_pot <= sc['pot'] <= max_pot]
    #plotter.sort(key=lambda x: x["sequence"])
    dataframe = pd.DataFrame(plotter)
    print(dataframe.from_dict(plotter))

def parse_plotter(subparsers):
    parser = subparsers.add_parser("plot")
    parser.add_argument("--book", "-b", required=True, help="Book code")
    parser.add_argument("--act", "-k", required=False, help="The quarter of the plot that you would like to view. Can be one of 1, 2, 3, or 4")
    parser.add_argument("--plotline", "-p", required=False, help="Plot line")
    parser.set_defaults(func=show_plotter)
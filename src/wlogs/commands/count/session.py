from datetime import datetime, date, timedelta
import csv
from wlogs.config import CONFIG

LOG_PATH = CONFIG["log_path"]
def sum_day(day):
    with open(LOG_PATH, "r") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if row["date"] == day:
                count += int(row["words"])
    return count

def sum_year_span(span: str):
    with open(LOG_PATH, "r") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if row["date"].startswith(span):
                count += int(row["words"])
    return count

def sum_week(start_date):
    end_date = start_date + timedelta(days=7)
    with open(LOG_PATH, "r") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            current_date = datetime.strptime(row["date"], "%Y-%m-%d")
            if start_date <= current_date <= end_date:
                count += int(row["words"])
    return count
def count_sessions(args):
    if args.day:
        wc = sum_day(args.day)
    elif args.week:
        timeframe = datetime.strptime(args.week, "%Y-%m-%d")
        wc = sum_week(timeframe)
    elif args.year:
        timeframe = args.year
        wc = sum_year_span(timeframe)
    elif args.month:
        timeframe = args.month
        wc = sum_year_span(timeframe)
    else:
        timeframe = date.today()
        wc = sum_day(timeframe)
    print(wc)

def parse_count_sessions(count_subparsers):
    sessions_parser = count_subparsers.add_parser("sessions", help="count words written in a number of (sessions determined by arguments)")
    sessions_parser.add_argument("-t", "--today", help="count words written in all sessions recorded for the current date", action="store_true")
    sessions_parser.add_argument("-d", "--day", help="count words written in all sessions recorded for the submitted date in the following format: YYYY-MM-DD")
    sessions_parser.add_argument("-m", "--month", help="count words written in all sessions recorded for the submitted month in the following format: YYYY-MM")
    sessions_parser.add_argument("-y", "--year", help="count words written in all sessions recorded for the submitted year in the following format: YYYY")
    sessions_parser.add_argument("-w", "--week", help="count words written in all sessions recorded for the week starting with the submitted date in the following format: YYYY-MM-DD")
    sessions_parser.set_defaults(func=count_sessions)
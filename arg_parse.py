from argparse import ArgumentParser, RawTextHelpFormatter
from datetime import datetime


def parse_arguments():
  parser = ArgumentParser(description='Public transport data', formatter_class=RawTextHelpFormatter)
  parser.add_argument('-d', '--download', action='store_true', help='Download data from the internet')
  parser.add_argument('-s', '--save', action='store_true', help='Save data into NoSQL database')
  parser.add_argument('--dont-save-fixes', action='store_true', dest='dont_save_fixes', help='Do not save fixes to the database')
  parser.add_argument('--drop-db', action='store_true', dest='drop_db', help='Drop the database')
  parser.add_argument('--from', metavar='STATION', dest='departure', help='Departure station')
  parser.add_argument('--to', metavar='STATION', dest='destination', help='Destination station')
  parser.add_argument('--start-date', metavar='DATE', dest='start_date', help='Show timetables after this date\nDATE must be in format YYYY-MM-DD')
  parser.add_argument('--start-time', metavar='TIME', dest='start_time', default='00:00:00', help='Show timetables after this time\nTIME must be in format hh:mm:dd (default: %(default)s)')
  parser.add_argument('--end-date', metavar='DATE', dest='end_date', help='Show before this date\nDATE must be in format YYYY-MM-DD')
  parser.add_argument('--end-time', metavar='TIME', dest='end_time', help='Show before this time\nTIME must be in format hh:mm:dd')
  return parser.parse_args()

def valid_date(date_text: str):
  try:
    datetime.strptime(date_text, '%Y-%m-%d')
    return True
  except ValueError:
    print(f"Date '{date_text}' must be in format YYYY-MM-DD")
    return False

def valid_time(time_text: str):
  try:
    datetime.strptime(time_text, '%H:%M:%S')
    return True
  except ValueError:
    print(f"Time '{time_text}' must be in format hh:mm:ss")
    return False

def modify_datetime(start_date: str, start_time: str, end_date: str, end_time: str):
  return  start_date + 'T' + start_time, end_date + 'T' + end_time

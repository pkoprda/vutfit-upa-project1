from arg_parse import parse_arguments, valid_date, valid_time, modify_datetime
from download_data import download_page
from process_data import drop_coll, save_data_to_db, MONGO_COLL, MONGO_COLL_FIXES
from find_data import find_road


def main():
  args = parse_arguments()

  if args.drop_db:
    drop_coll(MONGO_COLL)
    drop_coll(MONGO_COLL_FIXES)

  if args.download:
    download_page()

  if args.save:
    save_data_to_db(dont_save_fixes=args.dont_save_fixes)

  if args.start_date and args.start_time and args.end_date and args.end_time:
    if not valid_date(args.start_date) or not valid_time(args.start_time) \
      or not valid_date(args.end_date) or not valid_time(args.end_time):
      return

    start_datetime, end_datetime = modify_datetime(args.start_date, args.start_time, args.end_date, args.end_time)
    
  if bool(args.departure) ^ bool(args.destination): # xor
    print('Both departure and destination stations are needed as an input')
    return

  if args.departure and args.destination:
    find_road(args.departure, args.destination, start_datetime)


if __name__ == "__main__":
  main()

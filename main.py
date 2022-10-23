import argparse

from download_data import download_page
from process_data import xml_to_nosql


def parse_arguments():
  parser = argparse.ArgumentParser(description='Public transport data')
  parser.add_argument('-d', '--download', action='store_true', help='Download data from website')
  parser.add_argument('-s', '--save', action='store_true', help='Save data into NoSQL database')
  return parser.parse_args()

if __name__ == "__main__":
  args = parse_arguments()

  if args.download:
    download_page()
  xml_to_nosql(args)

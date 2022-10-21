import os
import re
from urllib import request

from bs4 import BeautifulSoup
from zipfile import ZipFile
from tqdm import tqdm


def download_page():
  url = "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/"
  opener = request.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  response = opener.open(url).read()
  s = BeautifulSoup(response, features="html.parser")
  link_prefix = "https://portal.cisjr.cz"

  # mazem prvy, ktory je odkaz na parent dir
  s.select_one('a').decompose()

  for link in s.find_all('a'):
    l = link.get('href')
    if re.match(r'.*\.zip', l ):
      r = opener.open(link_prefix+l).read()
      open('data/' + l.split('/')[-1], 'wb').write(r)
      with ZipFile('data/' + l.split('/')[-1], 'r') as zip_ref:
        zip_ref.extractall('data')
    else:        
      month = l.split('/')[-2]
      download_subpages(link_prefix+l, month)

def download_subpages(link, month):
  opener = request.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0')]
  response = opener.open(link).read()
  s = BeautifulSoup(response, features="html.parser")
  link_prefix = "https://portal.cisjr.cz"

  # vytvorim dir pre subor ak este neexistuje
  path = os.path.join('data', month)
  if not os.path.exists(path):
    os.makedirs(path)

  # mazem prvy, ktory je odkaz na parent dir
  s.select_one('a').decompose()

  for link in tqdm(s.find_all('a'), total=len(s.find_all('a')), desc=f"Downloading files for {month}"):
    l = link.get('href')
    if re.match(r'.*\.zip', l):
      file_link = link_prefix + l
      r = opener.open(file_link).read()
      open(os.path.join(path, l.split('/')[-1]), 'wb').write(r)

from urllib import response
import requests
from bs4 import BeautifulSoup
import urllib
import re
import os 
from zipfile import ZipFile
def get_subpages(link, month):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    response = opener.open(link).read()
    s = BeautifulSoup(response, features="html.parser")
    link_prefix = "https://portal.cisjr.cz"
    
    # vytvorim dir pre subor ak este neexistuje
    path = 'data/'+month
    if not os.path.exists(path):
        os.makedirs(path)


    # mazem prvy, ktory je odkaz na parent dir
    s.select_one('a').decompose()
    for link in s.find_all('a'):
        l = link.get('href')
        if re.match(r'.*\.zip', l ):
            print("\nstahujem\n",link_prefix+l)
            r = opener.open(link_prefix+l).read()
            open(path+'/' + l.split('/')[-1], 'wb').write(r)
            # with gzip.open(path+'/' + l.split('/')[-1]) as f:
            # sem moze ist rovno pandas na parsovanie 
            
            
    
url = "https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/"

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
response = opener.open(url).read()

s = BeautifulSoup(response, features="html.parser")
link_prefix = "https://portal.cisjr.cz"
# mazem prvy, ktory je odkaz na parent dir
s.select_one('a').decompose()

for link in s.find_all('a'):
    l = link.get('href')
    if re.match(r'.*\.zip', l ):
        print("\nstahujem\n",link_prefix[:-1]+l)
        r = opener.open(link_prefix+l).read()
        open( 'data/' + l.split('/')[-1], 'wb').write(r)
        with ZipFile('data/' + l.split('/')[-1],"r") as zip_ref:
                zip_ref.extractall('data')
    else :        
        month = l.split('/')[-2]
        get_subpages(link_prefix+l, month)
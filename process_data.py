from pathlib import Path
from xml.etree import ElementTree as ET
from tqdm import tqdm
import xmltodict
import json

from create_db import get_db
from create_db import get_collection


def xml_to_nosql():
  db = get_db()
  coll = get_collection(db)
  message_dict = {}

  for xml_file in tqdm(Path('data').glob('*.xml'),
                       total=len(list(Path('data').glob('*.xml'))),
                       desc='Converting files to dictionary'):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    message_dict.update(xmltodict.parse(ET.tostring(root)))

    coll.insert_one(message_dict)
    break

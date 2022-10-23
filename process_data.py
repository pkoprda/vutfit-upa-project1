from pathlib import Path
from xml.etree import ElementTree as ET
from tqdm import tqdm
import xmltodict

from create_db import get_db
from create_db import get_collection


def xml_to_nosql(args):
  db = get_db()
  coll = get_collection(db)
  message_dict = {}
  id_curr = 1

  if args.save:
    coll.drop()
    for xml_file in tqdm(Path('data').glob('*.xml'),
                        total=len(list(Path('data').glob('*.xml'))),
                        desc='Storing data into mongodb'):
      tree = ET.parse(xml_file)
      root = tree.getroot()

      message_dict.update({ "_id": id_curr, **xmltodict.parse(ET.tostring(root))})
      id_curr += 1

      coll.insert_one(message_dict)

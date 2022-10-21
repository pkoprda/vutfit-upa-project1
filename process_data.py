from pathlib import Path
from xml.etree import ElementTree as ET
from tqdm import tqdm
import xmltodict


def xml_to_nosql():
  message_dict = {}
  for xml_file in tqdm(Path('data').glob('*.xml'), total=len(list(Path('data').glob('*.xml'))), desc='Converting files to dictionary'):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for info in root:
      message_dict.update(xmltodict.parse(ET.tostring(info)))

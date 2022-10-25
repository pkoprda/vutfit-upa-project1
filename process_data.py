from pathlib import Path
import zipfile
import gzip
from datetime import datetime
import xmltodict
from tqdm import tqdm

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_USER = "demo"
MONGO_PASS = "demo"

MONGO_DB = "messages"
MONGO_COLL = "message_items"
MONGO_COLL_FIXES = "message_item_fixes"


def get_db(
    db_name: str = MONGO_DB, host: str = MONGO_HOST, port: int = MONGO_PORT
) -> Database:
    database: Database = MongoClient(host, port)[db_name]
    return database


def get_collection(db: Database, coll_name: str = MONGO_COLL) -> Collection:
    return db[coll_name]


def drop_coll(c: str):
    print("Dropping collection %s" % c)
    db = get_db()
    coll = get_collection(db, c)
    coll.drop()


def save_fixes_to_db_old(data_path: str = "data/2022-05"):
    data_folder = Path(data_path)
    if not data_folder.is_dir():
        print("Source folder is not present, check the path")
        return

    db = get_db()
    coll = get_collection(db, MONGO_COLL_FIXES)
    message_dict = {}

    data_fixes = list(data_folder.rglob("*.xml.zip"))

    for fix_path in data_fixes:
        
        xml_filename = Path(Path(fix_path).stem).stem
        xml_dir = (Path(fix_path).parts)[1]
        xml_id = xml_filename + "_" + xml_dir
        
        try:
            fix_archive = gzip.GzipFile(fix_path, "r")
            fix_file = fix_archive.read()
        except gzip.BadGzipFile:
            fix_archive = zipfile.ZipFile(fix_path, "r")
            fix_file = fix_archive.read(fix_archive.namelist()[0])

        found = coll.find_one({"_id": xml_id})
        if found:
            continue

        message_dict.update({"_id": xml_id, **xmltodict.parse(fix_file)})
        coll.insert_one({"_id": xml_id}, message_dict, upsert=True)

def save_fixes_to_db(data_path: str = "data/2022-05"):
    data_folder = Path(data_path)
    if not data_folder.is_dir():
        print("Source folder is not present, check the path")
        return

    db = get_db()
    coll_fix = get_collection(db, MONGO_COLL_FIXES)
    coll = get_collection(db, MONGO_COLL)
    
    message_dict = {}

    data_fixes = list(data_folder.rglob("*.xml.zip"))
    d = list(reversed(data_fixes))
    for fix_path in tqdm(
        d,
        total=len(d),
        desc="Storing fix data to MongoDB",
      ):
        
        xml_filename = Path(Path(fix_path).stem).stem
        xml_dir = (Path(fix_path).parts)[1]
        xml_id = xml_filename + "_" + xml_dir
        
        try:
            fix_archive = gzip.GzipFile(fix_path, "r")
            fix_file = fix_archive.read()
        except gzip.BadGzipFile:
            fix_archive = zipfile.ZipFile(fix_path, "r")
            fix_file = fix_archive.read(fix_archive.namelist()[0])

        content = xmltodict.parse(fix_file)
        if 'cancel' in xml_filename:
          if type(content['CZCanceledPTTMessage']['PlannedTransportIdentifiers']) is dict:
            res = coll.find_one({"CZPTTCISMessage.Identifiers.PlannedTransportIdentifiers.Core": content['CZCanceledPTTMessage']['PlannedTransportIdentifiers']['Core']})
          else:
            res = coll.find_one({"CZPTTCISMessage.Identifiers.PlannedTransportIdentifiers.Core": content['CZCanceledPTTMessage']['PlannedTransportIdentifiers'][0]['Core']})
          if res:
            validity_start = content["CZCanceledPTTMessage"]["PlannedCalendar"][
              "ValidityPeriod"
              ]["StartDateTime"][:10]
            validity_end = content["CZCanceledPTTMessage"]["PlannedCalendar"][
              "ValidityPeriod"
              ]["EndDateTime"][:10]
            validity_start = datetime.strptime(validity_start, "%Y-%m-%d")
            validity_end = datetime.strptime(validity_end, "%Y-%m-%d")
            number_of_days = validity_end - validity_start
            
            orig_validity_start = res["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"][
              "ValidityPeriod"
              ]["StartDateTime"][:10]
            orig_validity_start = datetime.strptime(orig_validity_start, "%Y-%m-%d")
            offset = validity_start - orig_validity_start
            fixed_bitmap = content["CZCanceledPTTMessage"]["PlannedCalendar"]['BitmapDays']
            orig_bitmap = list(res["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"]['BitmapDays'])

            list_size = len(orig_bitmap)
            for i in range(0, number_of_days.days+1):
              if fixed_bitmap[i] == '1':
                # zacina premavat skorej ako nahradeny vlak
                if (offset.days + i) < 0:
                  continue
                # premava aj po obnoveni nahradneho vlaku
                if (offset.days+ i) >= list_size:
                  break
                orig_bitmap[offset.days + i] = '0'

            orig_bitmap = "".join(orig_bitmap)
            res["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"]['BitmapDays'] = orig_bitmap
            message_dict = {}
            message_dict.update({"_id": res['_id'], **res})
            coll.update_one({'_id': res['_id']}, {"$set": message_dict}, upsert=True)
            message_dict = {}
            message_dict.update({"_id": xml_filename, **content})
            coll_fix.replace_one({'_id': xml_filename}, message_dict, upsert=True)
            
            
        else:
          # "Replacement line" doesn't have to replace anything so we just save it to original collection
          if 'RelatedPlannedTransportIdentifiers' in content['CZPTTCISMessage']['Identifiers']:
            if type(content['CZPTTCISMessage']['Identifiers']['RelatedPlannedTransportIdentifiers']) is dict:
              res = coll.find_one({"CZPTTCISMessage.Identifiers.PlannedTransportIdentifiers.Core": content['CZPTTCISMessage']['Identifiers']['RelatedPlannedTransportIdentifiers']['Core']})
            else:
              res = coll.find_one({"CZPTTCISMessage.Identifiers.PlannedTransportIdentifiers.Core": content['CZPTTCISMessage']['Identifiers']['RelatedPlannedTransportIdentifiers']['Core']})
            
            if res:
              validity_start = content["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"][
                "ValidityPeriod"
                ]["StartDateTime"][:10]
              validity_end = content["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"][
                "ValidityPeriod"
                ]["EndDateTime"][:10]
              validity_start = datetime.strptime(validity_start, "%Y-%m-%d")
              validity_end = datetime.strptime(validity_end, "%Y-%m-%d")
              number_of_days = validity_end - validity_start
              
              orig_validity_start = res["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"][
                "ValidityPeriod"
                ]["StartDateTime"][:10]
              orig_validity_start = datetime.strptime(orig_validity_start, "%Y-%m-%d")
              offset = validity_start - orig_validity_start
              
              fixed_bitmap = content["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"]['BitmapDays']
              orig_bitmap = list(res["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"]['BitmapDays'])

              list_size = len(orig_bitmap)
              for i in range(0, number_of_days.days+1):
                if fixed_bitmap[i] == '1':
                  # zacina premavat skorej ako nahradeny vlak
                  if (offset.days + i) < 0:
                    continue
                  # premava aj po obnoveni nahradneho vlaku
                  if (offset.days+ i) >= list_size:
                    break
                  orig_bitmap[offset.days + i] = '0'

              orig_bitmap = "".join(orig_bitmap)
              res["CZPTTCISMessage"]["CZPTTInformation"]["PlannedCalendar"]['BitmapDays'] = orig_bitmap
          
              message_dict = {}
              message_dict.update({"_id": res['_id'], **res})
              coll.update_one({'_id': res['_id']}, {"$set": message_dict}, upsert=True)


            message_dict = {}
            
            message_dict.update({"_id": xml_id, **content})
            coll.replace_one({'_id': xml_id}, message_dict, upsert=True)


def save_data_to_db(src_path: str = "data/GVD2022.zip", dont_save_fixes: bool = False):
    data_path = Path(src_path)
    if not data_path.is_file():
        print("Source data are not present, check the path or download the data")
        return

    db = get_db()
    coll = get_collection(db, MONGO_COLL)
    message_dict = {}

    # Load the data to the database
    archive = zipfile.ZipFile(data_path, "r")
    for name in tqdm(
        archive.namelist(),
        total=len(archive.namelist()),
        desc="Storing data to MongoDB",
    ):
        xml_file = archive.read(name)
        xml_filename = Path(name).stem

        found = coll.find_one({"_id": xml_filename})
        if found:
            continue

        message_dict.update({"_id": xml_filename, **xmltodict.parse(xml_file)})
        coll.replace_one({"_id": xml_filename},message_dict, upsert=True)

    # Save the fix data
    if not dont_save_fixes:
        save_fixes_to_db()

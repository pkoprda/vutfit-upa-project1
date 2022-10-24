from pathlib import Path
import zipfile
import gzip

import xmltodict
from tqdm import tqdm

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.collation import Collation


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


def prepare_data():
    db = get_db()
    coll_1 = get_collection(db, MONGO_COLL)
    #coll_2 = get_collection(db, MONGO_COLL_FIXES)

    try:
        coll_1.drop_index("PrimaryLocationName_1")
    except:
        pass
    coll_1.create_index("PrimaryLocationName")

    #CZForeignDestinationLocation

    #coll_1.create_index("PrimaryLocationName", collation=Collation(locale="cs"))

    for i in coll_1.list_indexes():
        print(i)


def save_fixes_to_db(data_path: str = "data"):
    data_folder = Path(data_path)
    if not data_folder.is_dir():
        print("Source folder is not present, check the path")
        return

    db = get_db()
    coll = get_collection(db, MONGO_COLL_FIXES)
    message_dict = {}

    data_fixes = list(data_folder.rglob("*.xml.zip"))

    for fix_path in tqdm(
        data_fixes, total=len(data_fixes), desc="Storing fixes to MongoDB"
    ):
        xml_filename = Path(fix_path).stem
        xml_dir = (Path(fix_path).parts)[1]
        xml_id = xml_filename + "_" + xml_dir

        found = coll.find_one({"_id": xml_id})
        if found:
            continue

        try:
            fix_archive = gzip.GzipFile(fix_path, "r")
            fix_file = fix_archive.read()
        except gzip.BadGzipFile:
            fix_archive = zipfile.ZipFile(fix_path, "r")
            fix_file = fix_archive.read(fix_archive.namelist()[0])

        message_dict.update({"_id": xml_id, **xmltodict.parse(fix_file)})
        coll.insert_one(message_dict)


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
        coll.insert_one(message_dict)

    # Save the fix data
    if not dont_save_fixes:
        save_fixes_to_db()


if __name__ == "__main__":
    prepare_data()
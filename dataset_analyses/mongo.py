# mongo utils

from pymongo import MongoClient
import pymongo

def get_db_collection():
    client = MongoClient()
    db = client.openneuro
    return(db.datasets)


def add_info_to_db(info):
    collection = get_db_collection()
    collection.insert_one(info)


def ds_from_database(dsnum):
    collection = get_db_collection()
    return(collection.find_one({'dsnum': dsnum}))


def delete_ds_from_db(dsnum):
    collection = get_db_collection()
    query = {'dsnum': dsnum}
    d = collection.delete_many(query)
    print(f"{d.deleted_count} documents deleted for {dsnum}!!")

from pymongo import MongoClient
from settings import DATABASE

_db = None

def database():
    global _db
    if _db == None:
        conn = MongoClient(DATABASE['HOST'], DATABASE['PORT'])
        _db = conn[DATABASE['NAME']]
    return _db


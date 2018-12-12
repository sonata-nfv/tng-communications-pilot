#!/usr/bin/python3

import os
from pymongo import MongoClient


DB_URI = os.environ['DB_URI']

client = MongoClient('mongodb://' + DB_URI + ':27017/')
db = client['wacDev']
session_collection = db['session']

registered_users = session_collection.count({'to': -1})
print(registered_users)
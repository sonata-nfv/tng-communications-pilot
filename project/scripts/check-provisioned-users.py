#!/usr/bin/python3

import os
from pymongo import MongoClient


DB_URI = os.environ['DB_URI']

client = MongoClient('mongodb://' + DB_URI + ':27017/')
db = client['wacDev']
user_collection = db['user']

provisioned_users = user_collection.count()
print(provisioned_users)

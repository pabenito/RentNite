import pymongo
from os import environ

# Database connection

client = pymongo.MongoClient(environ["db_url"])
db = client[environ["db_client"]]
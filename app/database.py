import config
import pymongo

# Database connection

client = pymongo.MongoClient(config.db_url)
db = client[config.db_client]
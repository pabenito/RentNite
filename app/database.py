import config
import pymongo
import cloudinary

cloudinary.config(
    cloud_name = config.cloud_name,
    api_key = config.api_key,
    api_secret = config.api_secret
)

# Database connection

client = pymongo.MongoClient(config.db_url)
db = client[config.db_client]
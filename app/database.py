import pymongo
import cloudinary

cloudinary.config(
    cloud_name = "dc4yqjivf",
    api_key = "387197219888788",
    api_secret = "D87sGRe-kJFShGl3rnFUoa9vSXc",
)

# Database connection

client = pymongo.MongoClient("mongodb+srv://IWA1:2NMRwrIIMLFSy307@cluster0.br1ipw2.mongodb.net/?retryWrites=true&w=majority")
db = client["iweb"]
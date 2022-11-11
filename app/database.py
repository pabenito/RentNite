import pymongo

# Database connection

client = pymongo.MongoClient("mongodb+srv://IWA1:2NMRwrIIMLFSy307@cluster0.br1ipw2.mongodb.net/?retryWrites=true&w=majority")
db = client["iweb"]
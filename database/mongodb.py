from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")
mongo_client = MongoClient(config['MONGO_DB'])

db = mongo_client.hrms

cityCollection = db["city"]
hotelsCollection = db["hotels"]
detailCollection = db["hotel"]
changeCollection = db["change"]
testCollection = db["test"]








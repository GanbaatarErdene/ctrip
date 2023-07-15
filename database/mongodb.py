from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")
mongo_client = MongoClient(config['MONGO_DB'])
db = mongo_client.hrms
employee = db["employee"]
cityCollection = db["city"]
hotelsCollection = db["hotels"]
hotelCollection = db["hotel"]
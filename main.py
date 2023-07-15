from ctrip_sync import request
# from ctrip_sync import token
from fastapi import FastAPI
from redis import Redis
from database.mongodb import employee
from database.mongodb import cityCollection
from database.mongodb import hotelsCollection
from database.mongodb import hotelCollection
from dotenv import load_dotenv
from dotenv import dotenv_values
import requests
import json
import redis
import time

config = dotenv_values(".env")
app = FastAPI()
ctrip = request.HotelDataFetcher()

@app.get("/")
def read_root():
    return config['MONGO_DB']

@app.get("/city")
def read_root():
    ctrip.get_city()

@app.get("/hotels")
def read_root():
    ctrip.get_hotels()

@app.get("/hotel")
def read_root():
     ctrip.get_hotel()
 


    

    

        








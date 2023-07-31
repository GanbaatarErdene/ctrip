import concurrent.futures
from ctrip_request import ctrip_req
from ctrip_sync import request
from fastapi import FastAPI
from redis import Redis
from database.mongodb import cityCollection
from database.mongodb import hotelsCollection
from database.mongodb import hotelCollection
from dotenv import load_dotenv
from dotenv import dotenv_values

config = dotenv_values(".env")
app = FastAPI()
ctrip = request.HotelDataFetcher()

@app.get("/")
def read_root():
    return config['MONGO_DB']

@app.get("/city")
def read_root():
    ctrip.save_city()

@app.get("/hotels")
def read_root():
    ctrip.save_hotels()

@app.get("/hotel")
def read_root():
    ctrip.get_hotel()

@app.get("/change")
def read_root():
    ctrip.get_changes()

@app.get("/upHotel")
def read_root():
    ctrip.update_detail()



@app.get("/data")
def read_root():
    ctrip.get_city()
    ctrip.get_hotels()
    ctrip.get_hotel()




    

    

        








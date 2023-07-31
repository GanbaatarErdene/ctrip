from ctrip_request import ctrip_req
from fastapi import FastAPI
import requests
import json
from dotenv import dotenv_values
from database.mongodb import cityCollection
from database.mongodb import hotelsCollection
from database.mongodb import hotelCollection
from database.mongodb import changeCollection
from .ctripToken import CtripAuthorizationCache


import concurrent.futures
from datetime import datetime,timedelta
import json
import ratelimitqueue
import multiprocessing.dummy


config = dotenv_values(".env")
app = FastAPI()
c_request = ctrip_req.HotelDataRequest()
class HotelDataFetcher:

    def save_city(self):
        response = c_request.get_city()
        save = []
        for i in response['CityInfos']['CityInfo']:
            save.append({
                "CityID": i['CityID'],
                "CityEnName": i['CityEnName'],
                "CountryID": i['CountryID'],
                "CountryEnName": i['CountryEnName']
            })
        res = cityCollection.insert_many(save)


    def save_hotels(self):
        city_datas = cityCollection.find()

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(self.fetch_hotels,city_datas)

    def fetch_hotels(self,city_datas):

        error = []
        hotelCount = 0
        city_id = city_datas.get("CityID")

        last_hotel_id = ""
        while True:

            try:
                response = c_request.get_hotels(city_id,last_hotel_id)
                hotel_ids = response['HotelIDs']
                hotelCount += len(hotel_ids)
                print("HotelCount =", hotelCount)

                if not hotel_ids:
                    break

                save = []
                for hotel_id in hotel_ids:
                    last_hotel_id = hotel_id
                    save.append({
                        "HotelID": hotel_id,
                        "CityID": city_id,
                        "CityEnName": city_datas.get("CityEnName"),
                        "CountryID": city_datas.get("CountryID"),
                        "CountryEnName": city_datas.get("CountryEnName"),
                    })
                hotelsCollection.insert_many(save)
            except Exception as e:
                print("Error", e)
                error.append(last_hotel_id)
                pass
        print("Errors:", error)


    def get_hotel(self):
        hotels = hotelsCollection.find()

        rlq = ratelimitqueue.RateLimitQueue(calls=500, per=60) 
        n_workers = 16

        def fetch_hotel(rlq):
            while rlq.qsize() > 0:
                try:
                    hotel_id = rlq.get()
                    print("Hotel_id =============== : ", hotel_id)

                    response = c_request.get_details(hotel_id) 
                
                    res = hotelCollection.insert_many([response])
                    rlq.task_done()

                except Exception as e:
                    print("Details error : ", e)
                    pass
        
        for hotel in hotels:
            rlq.put(hotel .get("HotelID"))

        with multiprocessing.dummy.Pool(n_workers) as pool:
            pool.map(fetch_hotel, (rlq,))


    def get_changes(self):
        right_now = datetime.now()
        before_day = right_now - timedelta(days = 1)

        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
            executor.submit(self.get_change, before_day, right_now)

    def get_change(self,before_day, right_now):
        time_stop = False
        last_record_id = ""

        while not time_stop:

            stop = False
            while not stop:
                try:
                    response = c_request.get_update(before_day,last_record_id)
                    last_record_id = response['PagingInfo']['LastRecordID']
                    changes = response['ChangeInfos']

                    if not last_record_id:
                        break

                    for item in changes:
                        if item['Category'] == "Hotel": 
                            changeCollection.update_one(
                                    {"_id": item["HotelID"]},
                                    {"$set": {"HotelID": item["HotelID"]}},
                                    upsert=True
                            )

                    stop = len(changes) < 1000

                except Exception as e:
                    print("Change Errors:", e)
                    pass

            if before_day == right_now:
                time_stop = True

            before_day = before_day + timedelta(minutes=10)
            print("Before-day ============:", before_day)


    def update_detail(self):
        change = changeCollection.find()

        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
            executor.map(self.update_hotel, change)

    def update_hotel(self,hotel):
        try:
            hotel_id = hotel.get('HotelID')
            print("change-iin hotel id: ",hotel_id)
          
            response = c_request.get_details(hotel_id)
            hotelCollection.update_many(
                {"HotelStaticInfo.HotelID": int(hotel_id) },
                {"$set": response},  
                upsert=True
            )
        except Exception as e:
            print("Details error : ", e)
            pass

from ctrip_request import ctrip_req
from fastapi import FastAPI
from dotenv import dotenv_values
from database.mongodb import cityCollection
from database.mongodb import hotelsCollection
from database.mongodb import detailCollection
from database.mongodb import changeCollection
from database.mongodb import testCollection
from collections import Counter
import concurrent.futures
from datetime import datetime,timedelta
import ratelimitqueue
import multiprocessing.dummy


config = dotenv_values(".env")
app = FastAPI()
c_request = ctrip_req.HotelDataRequest()
class HotelDataFetcher:

#  full sync CityID-г нь авна.
    def save_city(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.submit(self.fetch_city)

    def fetch_city(self):
        last_record_id = ""
        stop = False
        while not stop:
            try:
                response = c_request.get_city(last_record_id)
                if response.get("CityInfos",{}) is None:
                    print("CityInfos --------------------------------------- NONE ")
                    break

                CityInfos = response.get("CityInfos",{}).get("CityInfo",[]) 
                
                if CityInfos is not None:
                    for cityInfo in CityInfos:
                        cityCollection.update_one(
                            {"_id": cityInfo["CityID"]},
                            {"$set": {
                                "CityID": cityInfo["CityID"],
                                "CityEnName": cityInfo["CityEnName"],
                                "CountryID": cityInfo["CountryID"],
                                "CountryEnName": cityInfo["CountryEnName"]
                            }},
                            upsert=True
                        )
                if response.get("PagingInfo",{}) is None:
                    print("PagingInfo+++++++++++++++++++++++++++++++++ NONE")
                    break
                
                last_record_id = response.get("PagingInfo",{}).get("LastRecordID")

                if not last_record_id or len(CityInfos) < 2000:
                    stop = True

                print("Last_record_id :", last_record_id)
            except Exception as e:
                print("Change Errors:", e)
                pass


#  full sync CityID-р HotelID-г нь авна.
    def save_hotels(self):

        city_datas = cityCollection.find()

        rlq = ratelimitqueue.RateLimitQueue(calls=200, per=60)
        n_workers = 8

        def fetch_hotels(rlq):
            hotelCount = 0

            while rlq.qsize() > 0:
                city_id = rlq.get()
                print("CityID ========== : ", city_id)

                last_hotel_id = ""
                a =[]
                while True:
                    try:
                        response = c_request.get_hotels(city_id, last_hotel_id)
                        hotel_ids = response.get('HotelIDs')
                        if hotel_ids is None:
                            a.append(city_id)
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
                                # "CityEnName": city_data.get("CityEnName"),
                                # "CountryID": city_data.get("CountryID"),
                                # "CountryEnName": city_data.get("CountryEnName"),
                            })
                        hotelsCollection.insert_many(save)
                    except Exception as e:
                        print("Error", e)
                        pass
                print("Haalttai Hoteliin City ID ============== : ",a)

        for city_data in city_datas:
            rlq.put(city_data.get("CityID"))

        with multiprocessing.dummy.Pool(n_workers) as pool:
            pool.map(fetch_hotels, (rlq,))


# full sync HotelID-р detail-н авна.
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
                
                    res = detailCollection.insert_many([response])
                    # res = testCollection.insert_many([response])
                    rlq.task_done()

                except Exception as e:
                    print("Details error : ", e)
                    pass
        
        for hotel in hotels:
            rlq.put(hotel .get("HotelID"))

        with multiprocessing.dummy.Pool(n_workers) as pool:
            pool.map(fetch_hotel, (rlq,))


# 24 цагийн өөрчлөлтийг авна өдөр бүр авна. 
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


# 24 цагийн change өөрчлөгдсөн HotelID-р detail-н дуудаж хуучин байга detail дээрээ update хийнэ.
    def update_detail(self):
        change = changeCollection.find()

        rlq = ratelimitqueue.RateLimitQueue(calls=500, per=60) 
        n_workers = 32

        def update_hotel(rlq):
            while rlq.qsize() > 0:
                try:
                    hotel_id = rlq.get()
                    print("change-iin hotel id: ",hotel_id)
                
                    response = c_request.get_details(hotel_id)
                    detailCollection.update_many(
                        {"HotelStaticInfo.HotelID": int(hotel_id) },
                        {"$set": response},  
                        upsert=True
                    )
                    rlq.task_done
                except Exception as e:
                    print("Details error : ", e)
                    pass

        for hotel in change:
            rlq.put(hotel .get("HotelID"))

        with multiprocessing.dummy.Pool(n_workers) as pool:
            pool.map(update_hotel, (rlq,))


# Хоосон ирсэн ResponseStatus.Ack": 'Warning' байга detail-г устгана.
    def delete_detail(self): 
        query = {"ResponseStatus.Ack": 'Warning'}
        dlt = detailCollection.delete_many(query)
        print(dlt.deleted_count, " documents deleted !!")

            
# HotelID нь давхардсан үгүйг шалгах.
    def find_hotels(self):
        test = hotelsCollection.find({}, { 'HotelID': 1, '_id': 0})
        document_array = list(test)

        a = []
        for i in document_array:
            a.append(i["HotelID"])

        duplicate_values = self.get_duplicates(a)
        print("Duplicate values:", duplicate_values)

    def get_duplicates(self,arr):
        counter = Counter(arr)
        return [item for item, count in counter.items() if count > 1]


# Detail нь давхардсан үгүйг шалгах.
    def find_details(self):

        query = [
            {"$group": {"_id": "$HotelStaticInfo", "count": {"$sum": 1}}},
            {"$match": {"_id": {"$ne": "null"}, "count": {"$gt": 1}}},
            # {"$project": {"HotelStaticInfo": "$_id", "_id": 0}},
        ]

        result = list(detailCollection.aggregate(query)) 
        print("Давхардсан detail ========", result) 

        duplicate_documents = list(detailCollection.aggregate(query))

        for doc in duplicate_documents:
            hotel_info = doc["_id"]
            detailCollection.delete_one({"HotelStaticInfo": hotel_info})
            print(f"Адилхан detail-г устгасан: {hotel_info}")

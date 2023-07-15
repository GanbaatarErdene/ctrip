from fastapi import FastAPI
import requests
import json
from dotenv import load_dotenv
from dotenv import dotenv_values
from database.mongodb import employee
from database.mongodb import cityCollection
from database.mongodb import hotelsCollection
from database.mongodb import hotelCollection
from .ctripToken import CtripAuthorizationCache
import redis


config = dotenv_values(".env")
app = FastAPI()
class HotelDataFetcher:
    def __init__(self):
        # self.MONGO_DB = config['MONGO_DB']
        self.HOST = config['HOST']
        self.AID = config['AID']
        self.SID = config['SID']
        self.UUID = config['UUID']
        # self.TOKEN = "76821151eebe4a7584d32fb42a27e6cd"

        self.token = CtripAuthorizationCache()
        # self.TOKEN = self.token.get_token()
        self.ICODE = config['ICODE']
        self.HOTEL_ICODE = config['HOTEL_ICODE']
        self.HOTEL_STATIC_ICODE = config['HOTEL_STATIC_ICODE']
        self.REFRESH_TOKEN = config['REFRESH_TOKEN']
        self.KEY = config['KEY']

    def get_data(self, data, icode): 
        # token = CtripAuthorizationCache().get_token()
        
        token = self.token.get_token()
        print("=========================")
        print(token)
        headers = {'Accept': 'application/json', 'content-type': 'application/json'}
        url = f"{self.HOST}/OpenService/ServiceProxy.ashx?AID={self.AID}&SID={self.SID}&ICODE={icode}&UUID={self.UUID}&Token={token}&format=json"
        response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
        return response.json()


    def save_city(self, response):
        save = [] 
        # print("==============================")
        # print(response)
        for i in response['CityInfos']['CityInfo']:
            save.append({
                "CityID": i['CityID'],
                "CityEnName": i['CityEnName'],
                "CountryID": i['CountryID'],
                "CountryEnName": i['CountryEnName']
            })

        res = cityCollection.insert_many(save)
        # cityCollection.insert_many(save)

    def get_city(self):
        data = {
            "SearchCandidate": {
                "SearchByType": {
                    "SearchType": "2",
                    "IsHaveHotel": "F"
                }
            },
            "PagingSettings": {
                "PageSize": 100,
                "LastRecordID": ""
            }
        }
        
        response = self.get_data(data, self.ICODE)
        # print(response)
        self.save_city(response)
        


    def get_hotels(self):
        # print("------------------------------")
        city_datas = cityCollection.find()
        # # a = []
        error = []
        # save = []
        hotelCount = 0
        for city_data in city_datas:
            city_id = city_data.get("CityID")
            data = {
                "SearchCandidate": {
                    "SearchByCityID": {
                        "CityID": city_id
                    }
                },
                "PagingSettings": {
                    "PageSize":100,
                    "LastRecordID": ""
                }
            }
        
            # save = []
            last_hotel_id = ""
            errorCount = 0
            # hotelCount = 0
            while True:
                data["PagingSettings"]["LastRecordID"] = last_hotel_id
                try:
                    response = self.get_data(data, self.HOTEL_ICODE)
                    # hotel_ids = response.get('HotelIDs', [])
                    hotel_ids = response['HotelIDs']
                    # print(response)
                    hotelCount = hotelCount + len(hotel_ids) 
                    print("HotelCount ==============",hotelCount)

                    if not hotel_ids: 
                        break

                    save = []
                    for hotel_id in hotel_ids:
                        # hotls = city_data.get("CityEnName")
                        last_hotel_id = hotel_id

                        save.append({
                            "HotelID": hotel_id,
                            "CityID": city_id,
                            "CityEnName": city_data.get("CityEnName"),
                            "CountryID": city_data.get("CountryID"),
                            "CountryEnName": city_data.get("CountryEnName"),
                            })
                    # a.append(save)
                    hotelsCollection.insert_many(save)
                except Exception as e: 
                    print("Error",e)
                    # errorCount = errorCount + 1
                    # errorCount = errorCount + len(error) 
                    print("errorCount ==============",errorCount)
                    # errorCount = errorCount + 1
                    error.append(last_hotel_id)
                    print("ALDANII TOO =====",errorCount)
                    pass
        # hotelsCollection.insert_many(save)
                    # error.append(last_hotel_id)
        print("aldaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",error)
        print("Aldaaniiiiiiii tooooooooooooooooooooooooooooooooo", errorCount)
                    
              

        # while(error != []):
        #     for i in error:
        #         data["PagingSettings"]["LastRecordID"] = last_hotel_id
        #         try:
        #             response = self.get_data(data, self.HOTEL_ICODE)
        #             # hotel_ids = response.get('HotelIDs', [])
        #             hotel_ids = response['HotelIDs']
        #             # print(response)
        #             hotelCount = hotelCount + len(hotel_ids) 
        #             print("HotelCount ==============",hotelCount)

        #             if not hotel_ids: 
        #                 break

        #             for hotel_id in hotel_ids:
        #                 # hotls = city_data.get("CityEnName")
        #                 last_hotel_id = hotel_id

        #                 save.append({
        #                     "HotelID": hotel_id,
        #                     "CityID": city_id,
        #                     "CityEnName": city_data.get("CityEnName"),
        #                     "CountryID": city_data.get("CountryID"),
        #                     "CountryEnName": city_data.get("CountryEnName"),
        #                     })
        #             # a.append(save)
        #         # hotels_res = hotelsCollection.insert_many(save)
        #         except:
        #             errorCount = errorCount + 1
        #             error.append(last_hotel_id)
        #             print("ALDANII TOO =====",errorCount)
        #             pass
        # hotelsCollection.insert_many(save)
                # error дотор буудлын кодууд орсон байгаа тэдгээрийг дахин татаж авна татаж авчаад татаж авсан буудлын кодыг 
                #  error массиваас арилгана энэ процесс error массив хоосон болох хүртэл давтагдана.
        


    def get_hotel(self):

        hotels = hotelsCollection.find()
        for hotel in hotels:
            try:
                hotel_id = hotel.get('HotelID')
                data = {
                    "SearchCandidate": {
                        "HotelID": hotel_id
                    },
                    "Settings": {
                        "PrimaryLangID": "en",
                        "ExtendedNodes": [
                            "HotelStaticInfo.GeoInfo",
                            "HotelStaticInfo.TransportationInfos",
                            "HotelStaticInfo.Brand",
                            "HotelStaticInfo.Group",
                            "HotelStaticInfo.Ratings",
                            "HotelStaticInfo.Policies",
                            "HotelStaticInfo.AcceptedCreditCards",
                            "HotelStaticInfo.ImportantNotices",
                            "HotelStaticInfo.FacilitiesV2",
                            "HotelStaticInfo.Pictures",
                            "HotelStaticInfo.Descriptions",
                            "HotelStaticInfo.ContactInfo",  
                            "HotelStaticInfo.Tel",
                            "HotelStaticInfo.HotelTags.IsBookable",
                            "HotelStaticInfo.ArrivalTimeLimitInfo",
                            "HotelStaticInfo.DepartureTimeLimitInfo",
                            "HotelStaticInfo.ExternalFacility.Parking",
                            "HotelStaticInfo.ExternalFacility.ChargingPoint",
                            "HotelStaticInfo.NormalizedPolicies.ChildAndExtraBedPolicy",
                            "HotelStaticInfo.HotelDiscount",
                            "HotelStaticInfo.SellerShowInfos",
                            "HotelStaticInfo.VideoItems",
                            "HotelStaticInfo.NormalizedPolicies.MealsPolicyV2",
                            "HotelStaticInfo.HotelTags.ReservedData",
                            "HotelStaticInfo.HotelPromotions",
                            "HotelStaticInfo.HotelTaxRuleInfos",
                            "HotelStaticInfo.SepecialServiceForChinese",
                            "HotelStaticInfo.HotelFeatures",
                            "HotelStaticInfo.HotelUsedNames",
                            "HotelStaticInfo.BnBHotel",
                            "HotelStaticInfo.ContactPersonInfos",
                            "HotelStaticInfo.HotelCloseTime",
                            "HotelStaticInfo.HotelCertificates",
                            "HotelStaticInfo.NormalizedPolicies.ArrivalAndDeparturePolicy",
                            "HotelStaticInfo.NormalizedPolicies.DepositPolicy",
                            "HotelStaticInfo.NearbyPOIs",
                            "HotelStaticInfo.Themes",
                            "HotelStaticInfo.HotelTags.IsHeCheng",
                            "HotelStaticInfo.BossInfos",
                            "HotelStaticInfo.NormalizedPolicies.MealsPolicy", 
                            "HotelStaticInfo.Facilities" 
                        ]
                    }
                }

                response = self.get_data(data, self.HOTEL_STATIC_ICODE)
                res = hotelCollection.insert_many([response])
            except:

                pass






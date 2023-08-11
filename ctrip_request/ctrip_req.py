from fastapi import FastAPI
import requests
import json
from dotenv import dotenv_values
from ctrip_sync import ctripToken
import json

config = dotenv_values(".env")
app = FastAPI()

class HotelDataRequest(object):
    def __init__(self):
        self.session = requests.Session()
        self.MONGO_DB = config['MONGO_DB']
        self.HOST = config['HOST']
        self.AID = config['AID']
        self.SID = config['SID']
        self.UUID = config['UUID']
        self.token = ctripToken.CtripAuthorizationCache()
        self.ICODE = config['ICODE']
        self.HOTEL_ICODE = config['HOTEL_ICODE']
        self.HOTEL_STATIC_ICODE = config['HOTEL_STATIC_ICODE']
        self.CHECK_STATIC_ICODE = config['CHECK_STATIC_ICODE']
        self.REFRESH_TOKEN = config['REFRESH_TOKEN']
        self.KEY = config['KEY']
    
    def get_data(self, data, icode):
        token = self.token.get_token()
        print("=========================")
        print(token)
        headers = {'Accept': 'application/json', 'content-type': 'application/json'}
        url = f"{self.HOST}/OpenService/ServiceProxy.ashx?AID={self.AID}&SID={self.SID}&ICODE={icode}&UUID={self.UUID}&Token={token}&format=json"
        response = self.session.post(url, data=json.dumps(data), headers=headers, verify=False, timeout=180)
        return response.json()
    
    def get_city(self,last_record_id):
        data = {
            "SearchCandidate": {
                "SearchByType": {
                    "SearchType": "2",
                    "IsHaveHotel": "T"
                }
            },
            "PagingSettings": {
                "PageSize": 2000,
                "LastRecordID": f"{last_record_id}"
            }
        }
        response = self.get_data(data, self.ICODE)
        return response

    def get_hotels(self, city_id, last_hotel_id):
        data = {
            "SearchCandidate": {
                "SearchByCityID": {
                    "CityID": city_id
                }
            },
            "PagingSettings": {
                "PageSize": 2000,
                "LastRecordID": last_hotel_id
            }
        }
        response = self.get_data(data, self.HOTEL_ICODE)
        return response
    
    def get_details(self, hotel_id):
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
        return response
    
    def get_update(self,before_day,last_record_id):
        data = {
                "SearchCandidate": {
                    "StartTime": f"{before_day}",
                    "Duration": 600
                },
                "Settings": {
                    "IsShowChangeDetails": "string",
                    "IsShowChangeType": "string",
                    "DataCategory": "string"
                },
                "PagingSettings": {
                    "PageSize": 1000,
                    "LastRecordID": last_record_id
                }
            }
        response = self.get_data(data, self.CHECK_STATIC_ICODE)
        return response

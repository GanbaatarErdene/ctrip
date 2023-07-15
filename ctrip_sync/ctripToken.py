import os
import requests
import redis
from dotenv import load_dotenv
from dotenv import dotenv_values

config = dotenv_values(".env")

class CtripAuthorizationCache(object):
    def __init__(self):
        self.aid = config['AID']
        # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        # print(self.aid)
        self.sid = config['SID']
        self.key = config['KEY']
        self.base_url = config['HOST']
        self.pool = redis.ConnectionPool(
            host='localhost', port=6379, db=6, decode_responses=True
        )
        # self.pool = redis.ConnectionPool.from_url('redis://localhost:6379/6')

        self.cache = redis.Redis(connection_pool=self.pool)
        self.REFRESH_TOKEN_CACHE_KEY = "ctrip_refresh_token"
        self.ACCESS_TOKEN_CACHE_KEY = "ctrip_access_token"

    def get_access_token_ctrip(self):
        params = {"AID": self.aid, "SID": self.sid, "KEY": self.key}
        # url = self.base_url + "openserviceauth/authorize.ashx?"
        url = self.base_url + "/openserviceauth/authorize.ashx?"
        response = requests.get(url, params=params, timeout=20)
        self.check_request(response=response)
        return self.get_access_token()


    def set_token(self, access, refresh):
        REFRESH_TOKEN_CACHE_KEY = "ctrip_refresh_token"
        ACCESS_TOKEN_CACHE_KEY = "ctrip_access_token"

        self.cache.set(ACCESS_TOKEN_CACHE_KEY, access)
        self.cache.set(REFRESH_TOKEN_CACHE_KEY, refresh)

    def check_access_token(self):
        # print("CHECK access token")
        return self.check_cache(self.ACCESS_TOKEN_CACHE_KEY)

    def check_refresh_token(self):
        return self.check_cache(self.REFRESH_TOKEN_CACHE_KEY)

    def get_access_token(self):
        return self.get_cache(self.ACCESS_TOKEN_CACHE_KEY)

    def get_refresh_token(self):
        return self.get_cache(self.REFRESH_TOKEN_CACHE_KEY)

    def refresh_to_access_ctrip(self):
        params = {"AID": self.aid, "SID": self.sid}
        url = self.base_url + "/openserviceauth/refresh.ashx?"
        refresh_token = self.get_refresh_token()
        params["refresh_token"] = refresh_token
        response = requests.get(url, params=params)
        if response.json().get("ErrCode"):
            self.get_access_token_ctrip()
        else:
            self.check_request(response)
        return self.get_access_token()

    def set_cache(self, key, data, timeout=1800) -> None:
        self.cache.set(key, data, timeout)

    def get_cache(self, key):
        data = self.cache.get(key)

        return data

    def check_cache(self, key):
        hotel_caches = self.cache
        if hotel_caches.exists(key):
            return True
        return False

    # manage function
    def get_token(self):
        # print('GET Token')
        if self.check_access_token():
            return self.get_access_token()
        elif self.check_refresh_token():
            return self.refresh_to_access_ctrip()
        else:
            return self.get_access_token_ctrip()

    def check_request(self, response):
        if response.status_code == 200:
            _req_data = response.json()
            expire_time = _req_data.get("Expires_In")
            if _req_data.get("Access_Token"):
                access_token = _req_data.get("Access_Token")
                self.set_cache(
                    self.ACCESS_TOKEN_CACHE_KEY,
                    access_token,
                    timeout=expire_time - 60 if expire_time > 60 else expire_time,
                )
            if _req_data.get("Refresh_Token"):
                refresh_token = _req_data.get("Refresh_Token")
                self.set_cache(
                    self.REFRESH_TOKEN_CACHE_KEY,
                    refresh_token,
                    timeout=840,
                )
            if expire_time and expire_time < 60:
                self.get_token()
        else:
            print("code", response.status_code, "message", response.message)
 
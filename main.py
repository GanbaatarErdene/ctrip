from ctrip_sync import request
from fastapi import FastAPI
from dotenv import dotenv_values

config = dotenv_values(".env")
app = FastAPI()
ctrip = request.HotelDataFetcher()

@app.get("/")
def read_root():
    return config['MONGO_DB']

# full sync CityID-г авна.
@app.get("/city")
def read_root():
    ctrip.save_city()

# full sync HotelID-г авна.
@app.get("/hotel")
def read_root():
    ctrip.save_hotels()

# full sync Hotel Detail-г авна.
@app.get("/detail")
def read_root():
    ctrip.get_hotel()

# 24 цагийн өөрчлөлтийг авна.
@app.get("/change")
def read_root():
    ctrip.get_changes()

# 24 цагийн change өөрчлөгдсөн HotelID-р detail-н дуудаж хуучин байга detail дээрээ update хийнэ.
@app.get("/update")
def read_root():
    ctrip.update_detail()

# Хоосон ирсэн ResponseStatus.Ack": 'Warning' байга detail-г устгана.
@app.get("/delete")
def read_root():
    ctrip.delete_detail()

# HotelID нь давхардсан үгүйг шалгах.
@app.get("/same")
def read_root():
    ctrip.find_hotels()

# Detail нь давхардсан үгүйг шалгах.
@app.get("/sameDetail")
def read_root():
    ctrip.find_details()

@app.get("/data")
def read_root():
    ctrip.save_city()
    ctrip.save_hotels()
    ctrip.get_hotel()




    

    

        








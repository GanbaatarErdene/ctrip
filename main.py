from fastapi import FastAPI
from pymongo import MongoClient
from redis import Redis

app = FastAPI()

@app.get("/")
def read_root():
    return{"Helloooo": "World"}

# # MongoDB
mongo_client = MongoClient("mongodb://mongodb:27017/")
db = mongo_client.hrms
employee = db["employee"]
def todo_serializer(todo) -> dict:
    return {
        "id": str(todo["_id"]),
        "name": todo["name"],
    }

def todos_serializer(todos) -> list:
    return [todo_serializer(todo) for todo in todos]
# # Redis
# redis_client = Redis(host="redis", port=6379)

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

@app.get("/mongo")
def test_mongo():
    a = todos_serializer(employee.find())
    return a

# @app.get("/redis")
# def test_redis():
#     redis_client.set("message", "Redis is connected!")
#     return {"status": "success"}

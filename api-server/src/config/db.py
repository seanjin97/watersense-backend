from pymongo import MongoClient
import config.config as config
import certifi

if config.ENV == "prod":
    client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
else:
    client = MongoClient(config.MONGO_URI)

db = client.watersense
sensor = db.sensor
user = db.user
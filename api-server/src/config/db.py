from pymongo import MongoClient
import config.config as config
import certifi

client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())

db = client.watersense
sensor = db.sensor
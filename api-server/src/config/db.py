from pymongo import MongoClient
import config.config as config

client = MongoClient(config.MONGO_URI)

db = client.watersense
sensor = db.sensor
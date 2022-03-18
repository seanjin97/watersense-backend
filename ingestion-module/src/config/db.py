from pymongo import MongoClient
import config.config as config
import certifi

if config.ENV == "prod":
    client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
else:
    client = MongoClient(config.MONGO_URI)

db = client.watersense

if 'sensor' not in db.list_collection_names():
    db.create_collection('sensor',timeseries={'timeField':'startTime', 'granularity': 'seconds'})

sensor = db.get_collection("sensor")
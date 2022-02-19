import config.db as db

def insert(data):
    print("Inserting data:", data)
    db.sensor.insert_one(data)
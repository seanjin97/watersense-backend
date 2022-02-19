import config.db as db

def get_all():
    data = list(db.sensor.find({}))
    if data:
        for i in data:
            i["_id"] = str(i["_id"])

    return data
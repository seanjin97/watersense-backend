import datetime
from datetime import timedelta
import json
from bson import json_util

def parse_json(data):
    return json.loads(json_util.dumps(data))

def get_current_week_dates():
     now = datetime.datetime.now()

     now_day_1 = now - datetime.timedelta(days=now.weekday())

     dates = [(now_day_1 + datetime.timedelta(days=d)) for d in range(7)]
     return dates
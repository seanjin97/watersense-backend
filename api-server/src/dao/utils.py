import datetime

# Reads in list of data retrieved from MongoDB and parses ID and Time fields
def serialize(data, renameKey=None):
     if type(data) == list:
          for i in data:
               if "_id" in i.keys():
                    if renameKey:
                         i[renameKey] = str(i["_id"])
                         i.pop("_id")
                    else:
                         i["_id"] = str(i["_id"])
               if "startTime" in i.keys():
                    i["startTime"] = int(i["startTime"].timestamp())
               if "total_usage" in i.keys():
                    i["total_usage"] = round(i["total_usage"], 2)
               if "average_usage" in i.keys():
                    i["average_usage"] = round(i["average_usage"], 2)
               if "average_duration" in i.keys():
                    i["average_duration"] = round(i["average_duration"], 2)
     if type(data) == dict:
          data["_id"] = str(data["_id"])
     return data

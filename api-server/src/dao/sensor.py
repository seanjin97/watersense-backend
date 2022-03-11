import config.db as db
import dao.utils as utils
import datetime
import calendar
def get_all():
    data = list(db.sensor.find({}))
    serialised_data = utils.serialize(data)

    return serialised_data

# Aggregates sensor data based on params
def get_aggregated_data(sensors, month=None, year=None):

    # Set date filters depending on whether month and year arguments given
    if month and year:
        # Get first and last days of provided year and month
        start = datetime.datetime.today().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = datetime.datetime.today().replace(day=last_day, hour=0, minute=0, second=0, microsecond=0)
    else:
        # If month and year arguments not given, assume current month and year
        start = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = datetime.datetime.today().replace(day=last_day, hour=0, minute=0, second=0, microsecond=0)

    # Aggregation
    data = list(db.sensor.aggregate([
        {
            "$match": {
                "device_id": {
                    "$in": sensors
                },
                "startTime": { "$gte": start, "$lte": end}
            }
        },
        {
            "$group": {
                "_id": "$device", 
                "total_usage": {"$sum": "$sessionUsage"}, 
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"},
                "count": {"$sum": 1}
                }
        }
    ]))
    return utils.serialize(data, "device")
import config.db as db
import dao.utils as utils
import datetime
import calendar

def get_all():
    data = list(db.sensor.find({}))
    serialised_data = utils.parse_json(data)

    return serialised_data

# Get total water usage for a user.
def count_by_user_sensors(sensors):
    data = list(db.sensor.aggregate([
        {
            "$match": {"device_id": {
                "$in": sensors
                }
            }
        },
        {
            "$group": {
                "_id": 1, 
                "water_usage": {"$sum": "$sessionUsage"}
                }
        },
        {
            "$project": {
                "_id": 0,
                "water_usage": "$water_usage"
            }
        }
    ]))
    return utils.parse_json(data)

# Aggregates data by sensor category in a specified time view.
def get_aggregated_data_by_sensor(sensors, day=False, week=False, month=None, year=None):

    # Set date filters depending on arguments given.

    # Month data for a specific month and year.
    if not(month == None and year == None):
        # Get first and last days of provided year and month
        start = datetime.datetime.today().replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = datetime.datetime.today().replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    # Current day.
    elif day:
        start = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        end = datetime.datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)
    # Current week.
    elif week: 
        current_week = utils.get_current_week_dates()
        start = current_week[0].replace(hour=0, minute=0, second=0, microsecond=0)
        end = current_week[-1].replace(hour=23, minute=59, second=59, microsecond=999999)
    # Current month.
    elif not (month and year):
        # If month and year arguments not given, assume current month and year.
        start = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = datetime.datetime.today().replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

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
        },
        {
            "$project": {
                "_id": 0,
                "total_usage": {"$round": ["$total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "count": "$count",
                "device": "$_id"
            }
        },
        {
            "$sort": {"device": 1}
        }
    ]))
    return utils.parse_json(data)

# Aggregates data by hours in current day.
def get_aggregated_data_by_hours_in_day(sensors):

    start = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)

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
        "$addFields": {
            "startTime": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } } } }
            }
        },
        {
            "$group": {
                "_id": { 
                    "hour": "$startTime.hour"
                }, 
                "total_usage": {"$sum": "$sessionUsage"}, 
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"},
                "count": {"$sum": 1}
                }
        },
        {
            "$project": {
                "_id": 0,
                "total_usage": {"$round": ["$total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "count": "$count",
                "hour": "$_id"
            }
        },
        {
            "$sort": {"hour": 1}
        }
    ]))
    return utils.parse_json(data)

# Aggregates data by days in a week.
def get_aggregated_data_by_days_in_week(sensors):

    current_week = utils.get_current_week_dates()
    start = current_week[0].replace(hour=0, minute=0, second=0, microsecond=0)
    end = current_week[-1].replace(hour=23, minute=59, second=59, microsecond=999999)

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
        "$addFields": {
            "startTime": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } } } }
            }
        },
        {
            "$group": {
                "_id": { 
                    "day": "$startTime.day",
                    "month": "$startTime.month",
                    "year": "$startTime.year"
                }, 
                "total_usage": {"$sum": "$sessionUsage"}, 
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"},
                "count": {"$sum": 1}
                }
        },
        {
            "$project": {
                "_id": 0,
                "total_usage": {"$round": ["$total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "count": "$count",
                "date": { "$concat": [ { "$toString": "$_id.day" }, "/", { "$toString": "$_id.month" }, "/", {"$toString": "$_id.year"} ] }
            }
        },
        {
            "$sort": {"date": 1}
        }
    ]))
    return utils.parse_json(data)


# Aggregates data by days in a week.
def get_aggregated_data_by_days_in_week(sensors):

    current_week = utils.get_current_week_dates()
    start = current_week[0].replace(hour=0, minute=0, second=0, microsecond=0)
    end = current_week[-1].replace(hour=23, minute=59, second=59, microsecond=999999)

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
        "$addFields": {
            "startTime": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } } } }
            }
        },
        {
            "$group": {
                "_id": { 
                    "day": "$startTime.day",
                    "month": "$startTime.month",
                    "year": "$startTime.year"
                }, 
                "total_usage": {"$sum": "$sessionUsage"}, 
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"},
                "count": {"$sum": 1}
                }
        },
        {
            "$project": {
                "_id": 0,
                "total_usage": {"$round": ["$total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "count": "$count",
                "date": { "$concat": [ { "$toString": "$_id.day" }, "/", { "$toString": "$_id.month" }, "/", {"$toString": "$_id.year"} ] }
            }
        },
        {
            "$sort": {"date": 1}
        }
    ]))
    return utils.parse_json(data)

def get_aggregated_data_by_last_6_months(sensors):
    end = datetime.datetime.today()
    start = (end - datetime.timedelta(6 * 30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

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
        "$addFields": {
            "startTime": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } } } }
            }
        },
        {
            "$group": {
                "_id": { 
                    "month": "$startTime.month",
                    "year": "$startTime.year"
                }, 
                "total_usage": {"$sum": "$sessionUsage"}, 
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"},
                "count": {"$sum": 1}
                }
        },
        {
            "$addFields": {
                "concatDate": { "$concat": [{"$toString": "$_id.year"}, "-", { "$toString": "$_id.month" }, "-1"] }
            }
        },
        {
            "$sort": {"concatDate": 1}
        },
        {
            "$project": {
                "_id": 0,
                "total_usage": {"$round": ["$total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "count": "$count",
                "date": { "$concat": [{ "$toString": "$_id.month" }, "/", {"$toString": "$_id.year"} ] }
            }
        },
    ]))
    return utils.parse_json(data)
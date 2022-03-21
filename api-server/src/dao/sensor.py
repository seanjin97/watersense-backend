import config.db as db
import dao.utils as utils
import datetime
import calendar
import pytz

tz_info = pytz.timezone('Asia/Singapore')


# Aggregates data by sensor category in a specified time view.
def get_aggregated_data_by_sensor(sensors, day=False, week=False, month=None, year=None):

    # Set date filters depending on arguments given.

    # Month data for a specific month and year.
    if not(month == None and year == None):
        # Get first and last days of provided year and month
        start = datetime.datetime.now(tz_info).replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = datetime.datetime.now(tz_info).replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
    
    # Current day.
    elif day:
        start = datetime.datetime.now(tz_info).replace(hour=0, minute=0, second=0, microsecond=0)
        end = datetime.datetime.now(tz_info).replace(hour=23, minute=59, second=59, microsecond=999999)
    # Current week.
    elif week: 
        current_week = utils.get_current_week_dates()
        start = current_week[0].replace(hour=0, minute=0, second=0, microsecond=0)
        end = current_week[-1].replace(hour=23, minute=59, second=59, microsecond=999999)
    # Current month.
    elif not (month and year):
        # If month and year arguments not given, assume current month and year.
        start = datetime.datetime.now(tz_info).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = calendar.monthrange(start.year, start.month)[1]
        end = datetime.datetime.now(tz_info).replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

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

    start = datetime.datetime.now(tz_info).replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.datetime.now(tz_info).replace(hour=23, minute=59, second=59, microsecond=999999)

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
            "startTime": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } }, "timezone": "Asia/Singapore" } }
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
                "hour": "$_id.hour"
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
            "startTime": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } }, "timezone": "Asia/Singapore" } }
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
    end = datetime.datetime.now(tz_info)
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
            "startTime": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } }, "timezone": "Asia/Singapore" } }
            },
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

# Get total water usage in previous month for a user.
def prev_month_water_usage_by_user_sensors(sensors):

    start = (datetime.datetime.now(tz_info) - datetime.timedelta(30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = calendar.monthrange(start.year, start.month)[1]
    end = start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    data = list(db.sensor.aggregate([
        {
            "$match": {"device_id": {
                "$in": sensors
                },
                "startTime": { "$gte": start, "$lte": end}
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

# Get total water usage in current day for a user.
def day_water_usage_by_user_sensors(sensors):

    start = datetime.datetime.now(tz_info).replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.datetime.now(tz_info).replace(hour=23, minute=59, second=59, microsecond=999999)

    data = list(db.sensor.aggregate([
        {
            "$match": {"device_id": {
                "$in": sensors
                },
                "startTime": { "$gte": start, "$lte": end}
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

# Aggregates data by days in previous month.
def get_aggregated_data_by_days_in_prev_month(sensors):

    start = (datetime.datetime.now(tz_info) - datetime.timedelta(30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = calendar.monthrange(start.year, start.month)[1]
    end = start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

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
            "tempDate": { "$dateToParts": { "date": { "$toDate": { "$toLong": "$startTime" } }, "timezone": "Asia/Singapore" } }
            }
        },
        {
            "$group": {
                "_id": { 
                    "day": "$tempDate.day",
                    "month": "$tempDate.month",
                    "year": "$tempDate.year"
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
                "date_string": { "$concat": [ { "$toString": "$_id.day" }, "/", { "$toString": "$_id.month" }, "/", {"$toString": "$_id.year"} ] },
                "date_parts": "$_id"
            }
        }
    ]))
    return utils.parse_json(data), last_day

def get_all_users_current_month_usage():

    start = datetime.datetime.now(tz_info).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = calendar.monthrange(start.year, start.month)[1]
    end = datetime.datetime.now(tz_info).replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)        

    data = list(db.sensor.aggregate([
        {
            "$match": {
                "startTime": { "$gte": start, "$lte": end}
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "device_id",
                "foreignField": "sensors",
                "as": "user"
            }
        },
        {
            "$unwind": "$user"
        },
        {
            "$group": {
                "_id": "$user.username", 
                "total_usage": {"$sum": "$sessionUsage"}, 
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"},
                "count": {"$sum": 1}
                }
        },
        {
            "$project": {
                "username": "$_id",
                "total_usage": {"$round": ["$total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "count": "$count",
                "_id": 0
            }
        },
        {
            "$sort": {
                "total_usage": 1
            }
        }
    ]))
    return utils.parse_json(data)

def get_all_other_users_prev_month_usage(sensors):

    start = (datetime.datetime.now(tz_info) - datetime.timedelta(30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = calendar.monthrange(start.year, start.month)[1]
    end = start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    data = list(db.sensor.aggregate([
        {
            "$match": {
                "device_id": {
                    "$nin": sensors
                },
                "startTime": { "$gte": start, "$lte": end}
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "device_id",
                "foreignField": "sensors",
                "as": "user"
            }
        },
        {
            "$unwind": "$user"
        },
        {
            "$addFields": {
                "category": {"$arrayElemAt":[{"$split": ["$device" , "_"]}, 0]}
            }
            
        },
        {
            "$group": {
                "_id": {
                    "user": "$user.username",
                    "category": "$category"
                }, 
                "total_usage": {"$sum": "$sessionUsage"},
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"}
                }
        },
        {
            "$group": {
                "_id": "$_id.category",
                "average_total_usage": {"$avg": "$total_usage"},
                "average_usage": {"$avg": "$average_usage"}, 
                "average_duration": {"$avg": "$average_duration"}
            }
        },
        {
            "$project": {
                "category": "$_id",
                "average_total_usage": {"$round": ["$average_total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "_id": 0
            }
        }
    ]))
    return utils.parse_json(data)

def get_user_prev_month_usage_split_by_categories(sensors):

    start = (datetime.datetime.now(tz_info) - datetime.timedelta(30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = calendar.monthrange(start.year, start.month)[1]
    end = start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

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
                "category": {"$arrayElemAt":[{"$split": ["$device" , "_"]}, 0]}
            }
            
        },
        {
            "$group": {
                "_id": "$category",
                "total_usage": {"$sum": "$sessionUsage"},
                "average_usage": {"$avg": "$sessionUsage"}, 
                "average_duration": {"$avg": "$sessionDuration"},
                }
        },
        {
            "$project": {
                "category": "$_id",
                "total_usage": {"$round": ["$total_usage", 2]},
                "average_usage": {"$round": ["$average_usage", 2]},
                "average_duration": {"$round": ["$average_duration", 2]},
                "_id": 0
            }
        }
    ]))
    return utils.parse_json(data)


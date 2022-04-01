import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config.config as config
import dao.sensor as sensor_db
import dao.user as user_db
from fastapi.responses import JSONResponse
import datetime 
import itertools
import models.models as models
import json
import random

app = FastAPI(docs_url="/swagger")

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["dev"])
async def root():
    return {"message": "hi"}

# Retrieve data organised by sensor category for pie chart and data organised by day/ month/ year for bar chart.
@app.get("/analytics/detailed/{username}", tags=["analytics"])
async def retrieve_user_and_current_trends(username: str):

    # Retrieve user details.r
    user = user_db.get_user(username)
    
    if not user:
        return JSONResponse(content="user not found", status_code=400)

    # Aggregates data by sensor category.
    aggregated_daily_sensor_readings_by_sensor = sensor_db.get_aggregated_data_by_sensor(user["sensors"], day=True)
    aggregated_weekly_sensor_readings_by_sensor = sensor_db.get_aggregated_data_by_sensor(user["sensors"], week=True)
    aggregated_monthy_sensor_readings_by_sensor = sensor_db.get_aggregated_data_by_sensor(user["sensors"])
    

    # Retrieve sensor data by daily, weekly, monthly breakdowns.
    aggregated_sensor_readings_by_hours_in_day = sensor_db.get_aggregated_data_by_hours_in_day(user["sensors"])
    aggregated_sensor_readings_by_days_in_week = sensor_db.get_aggregated_data_by_days_in_week(user["sensors"])
    aggregated_sensor_readings_by_days_in_week = sorted(aggregated_sensor_readings_by_days_in_week, key=lambda d: d["date_parts"]["day"]) 
    aggregated_sensor_readings_by_last_6_months = sensor_db.get_aggregated_data_by_last_6_months(user["sensors"])

    consolidated_data = {**user, 
    "sensor": {
        "daily": aggregated_daily_sensor_readings_by_sensor, 
        "weekly": aggregated_weekly_sensor_readings_by_sensor, 
        "monthly": aggregated_monthy_sensor_readings_by_sensor},
    "dmy": {
        "daily": aggregated_sensor_readings_by_hours_in_day,
        "weekly": aggregated_sensor_readings_by_days_in_week,
        "monthly": aggregated_sensor_readings_by_last_6_months
    }
    }

    return JSONResponse(status_code=200, content=consolidated_data)


@app.get("/leaderboard/{username}", tags=["leaderboard"])
def list_leaderboard_standings(username: str):
    if not user_db.get_user(username):
        return JSONResponse(content="user not found", status_code=400)

    data = sensor_db.get_all_users_current_month_usage()

    user_standing = next((index for (index, d) in enumerate(data) if d["username"] == username), None)
    response = {
        "leaderboard": data[:3],
        "standing": {
            "usage": data[user_standing],
            "position": user_standing + 1
        }
    }
    return JSONResponse(content=response, status_code=200)

@app.post("/goals", tags=["goals"])
def set_goals(goals: models.Goals):
    user = user_db.get_user(goals.username)
    if not user:
        return JSONResponse(content="user not found", status_code=400)

    result = user_db.update_user(goals.username, {"goals": {
        "daily": round(goals.month / 28, 2),
        "monthly": goals.month
    }})
    if (result["matched"] and result["modified"]) or (result["matched"] and not result["modified"]):
        return JSONResponse(content=user_db.get_user(goals.username), status_code=200)
    else:
        return JSONResponse(content="Update failed", status_code=400)

@app.get("/user", tags=["user"])
def get_user(username: str):
    return JSONResponse(content=user_db.get_user(username), status_code=200)

@app.post("/user", tags=["user"])
def create_user(username: str):
    if user_db.get_user(username):
        return JSONResponse(content="User already exists.", status_code=400)

    user = {
        "username": username,
        "sensors": [],
        "goals": {
            "daily": round(390000 / 28, 2),
            "monthly": 390000
        }
    }
    user_db.create_user(user)

    return JSONResponse(content=user_db.get_user(username), status_code=201)

@app.get("/analytics/overview/{username}", tags=["analytics"])
def get_monthly_overview(username: str):
    user = user_db.get_user(username)
    if not user:
        return JSONResponse(content="User not found.", status_code=400)
    result = {}

    month_water_usage = sensor_db.prev_month_water_usage_by_user_sensors(user["sensors"])
    result["prev_month_usage"] = month_water_usage[0]["water_usage"]
    result["prev_month_goal"] = user["goals"]["monthly"]

    result["daily_goal"] = user["goals"]["daily"]
    
    daily_usage_in_prev_month, num_days_in_prev_month = sensor_db.get_aggregated_data_by_days_in_prev_month(user["sensors"])
    num_days_exceeding_daily_goal = [item for item in daily_usage_in_prev_month if item["total_usage"] > user["goals"]["daily"]]
    result["num_days_exceeded"] = len(num_days_exceeding_daily_goal)
    result["num_days_in_prev_month"] = num_days_in_prev_month
    result["data"] = sorted(daily_usage_in_prev_month, key=lambda d: d["date_parts"]["day"]) 

    return JSONResponse(content={**user, **result}, status_code=200)

@app.get("/recommendations/{username}", tags=["recommendations"])
def get_personalised_reccomendations(username: str):
    user = user_db.get_user(username)
    if not user:
        return JSONResponse(content="User not found.", status_code=400)

    # Read in recommendation list.
    with open("static/recommendations.json", "r") as f:
        recommendations = json.load(f)

    results = {}

    # Get prev month data for peers and user.
    peer_data = sensor_db.get_all_other_users_prev_month_usage(user["sensors"])
    user_data = sensor_db.get_user_prev_month_usage_split_by_categories(user["sensors"])

    # Split devices into categories.
    peer_dict = {}
    for i in peer_data:
        peer_dict[i["category"]] = {
            "average_total_usage": i["average_total_usage"], 
            "average_usage": i["average_usage"],
            "average_duration": i["average_duration"]
            }
    
    user_dict = {}
    for i in user_data:
        user_dict[i["category"]] = {
            "total_usage": i["total_usage"],
            "average_usage": i["average_usage"],
            "average_duration": i["average_duration"]
            }

    # Compare user vs peers water usage in each category. Give recommendations based on categories that user performed poorer in.
    peer_reccomendation_list = [category for category in list(peer_dict.keys()) if peer_dict[category]["average_total_usage"] < user_dict[category]["total_usage"]]
    peer_recommendations = {}
    for category in peer_reccomendation_list:
        peer_recommendations[category] = random.choice(recommendations[category])

    user_total_water_usage_in_prev_month = 0
    for item in user_data:
        user_total_water_usage_in_prev_month += item["total_usage"]

    goal_recommendations = {}
    results["monthly_goal_comparison"] = {}
    if user_total_water_usage_in_prev_month > user["goals"]["monthly"]:
        # Read in statistics list.
        # Derived from https://www.singsaver.com.sg/blog/7-practical-ways-you-can-save-water-at-home by calculating % of water usage of average litres of water used per month
        with open("static/statistics.json", "r") as f:
            statistics = json.load(f)
        goal_reccomendation_list = [category for category in list(peer_dict.keys()) if statistics[category]< user_dict[category]["total_usage"]]
        goal_recommendations = {}
        for category in goal_reccomendation_list:
            goal_recommendations[category] = random.choice(recommendations[category])
        
        results["monthly_goal_comparison"]["national_monthly_statistics"] = statistics
        results["monthly_goal_comparison"]["statistics_recommendations"] = goal_recommendations

    # Create response object.
    results["username"] = user
    results["user_usage"] = user_dict
    results["peer_comparison"] = {}
    results["peer_comparison"]["peers"] = peer_dict
    results["peer_comparison"]["peer_recommendations"] = peer_recommendations
    return results


if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


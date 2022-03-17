import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config.config as config
import dao.sensor as sensor_db
import dao.user as user_db
from fastapi.responses import JSONResponse
import datetime 
import itertools

app = FastAPI(docs_url="/swagger")

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "hi"}

@app.get("/getall")
async def root():
    print("/getall: triggered")
    data = sensor_db.get_all()
    return JSONResponse(status_code=200, content=data)

@app.get("/sanitycheck")
def sanity_check():
    users = user_db.get_all()
    results = {}
    for user in users:
        data = sensor_db.count_by_user_sensors(user["sensors"])
        results[user["username"]] = data[0]["water_usage"]
    return JSONResponse(content=results, status_code=200)

# Retrieve data organised by sensor category for pie chart and data organised by day/ month/ year for bar chart.
@app.get("/analytics/user/{username}")
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


@app.get("/leaderboard/{username}")
def list_leaderboard_standings(username: str):
    if not user_db.get_user(username):
        return JSONResponse(content="user not found", status_code=400)
    users = user_db.get_all()

    results = {}
    for user in users:
        data = sensor_db.count_by_user_sensors(user["sensors"])
        results[user["username"]] = data[0]["water_usage"]
    sorted_results = dict(sorted(results.items(), key=lambda item: item[1]))
    user_standing = list(sorted_results.keys()).index(username)

    response = {
        "leaderboard": dict(itertools.islice(sorted_results.items(), 3)),
        "standing": {
            "username": username,
            "usage": sorted_results[list(sorted_results.keys())[user_standing]],
            "position": user_standing + 1
        }
    }
    return JSONResponse(content=response, status_code=200)

if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


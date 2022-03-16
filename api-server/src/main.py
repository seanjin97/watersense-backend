import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config.config as config
import dao.sensor as sensor_db
import dao.user as user_db
from fastapi.responses import JSONResponse
import datetime 

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
    data = sensor_db.count_by_user_sensors()
    return JSONResponse(content=data, status_code=200)

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

if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config.config as config
import dao.sensor as sensor_db
import dao.user as user_db
from fastapi.responses import JSONResponse

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

@app.get("/user/{username}")
async def retrieve_user(username: str):
    user = user_db.get_user(username)
    aggregated_sensor_readings = sensor_db.get_aggregated_data(user["sensors"])

    consolidated_data = {**user, "aggregation": aggregated_sensor_readings}

    return JSONResponse(status_code=200, content=consolidated_data)

if __name__ == "__main__":
    print("Service started!")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


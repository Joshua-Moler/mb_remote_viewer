import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from fastapi.responses import FileResponse
import requests
from requests_oauthlib import OAuth1
import time

import json

import sqlite3
import os


temperatureData = {}

with open('statusServer.json') as statusServer:
    serverJson = json.load(statusServer)
try:
    clientKey = serverJson['Client_Key']
except:
    clientKey = ''
try:
    clientSecret = serverJson['Client_Secret']
except:
    clientSecret = ''
try:
    tokenKey = serverJson['Token_Key']
except:
    tokenKey = ''
try:
    tokenSecret = serverJson['Token_Secret']
except:
    tokenSecret = ''
try:
    restADR = serverJson['Server_Host']
except:
    restADR = "http://localhost:5000/"

statusServerAuth = OAuth1(clientKey, clientSecret, tokenKey, tokenSecret)

app = FastAPI()
logData = []
temperatureData = {
    "PRP": [],
    "RGP": [],
    "CFP": [],
    "STP": [],
    "ICP": [],
    "MXP": [],

}
plotTimes = []


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return {"test": "Hello World"}


@app.get("/Plot/{param}")
async def plot(param):
    return FileResponse("./test.png")


@app.post("/login")
async def token():
    return {"token": 'test123'}


@app.get("/status")
async def status():
    return {

        "v1": False,
        "v2": False,
        "v3": False,
        "v4": False,
        "v5": False,
        "v6": False,
        "v7": False,
        "v8": False,
        "v9": False,
        "v10": False,
        "v11": False,
        "v12": False,
        "v13": False,
        "v14": False,
        "v15": False,
        "v16": False,
        "v17": False,
        "v18": False,
        "v19": False,
        "v20": False,
        "v21": False,
        "v22": False,
        "v23": False,
        "v24": False,
        "PM1": False,
        "PM2": False,
        "PM3": False,
        "PM4": False,
        "PM5": False

    }


@app.get("/values")
async def values():
    DMAP = {
        "MXP": "MXP_RUOX",
        "ICP":  "DHX-T",
        "FLOW": "Flow"
    }
    JSON = {
        'P1': 'N/A',
        'P2': 'N/A',
        'P3': 'N/A',
        'P4': 'N/A',
        'P5': 'N/A',
        'P6': 'N/A',
        'PRP': 'N/A',
        'RGP': 'N/A',
        'CFP': 'N/A',
        'STP': 'N/A',
        'ICP': 'N/A',
        'MXP': 'N/A',
        'SETPOINT': 'N/A (MANUAL)',
        'FLOW': 'N/A',
        'STATUS': 'MANUAL'
    }
    try:
        data = requests.get(restADR+"All", auth=statusServerAuth).json()
    except:
        data = {}
    returnData = {ii.upper() : data[ii] for ii in data}


    if "STATUS" not in returnData: returnData["STATUS"] = {}
    if "TEMPERATURES" not in returnData: returnData["TEMPERATURES"] = {}
    if "PRESSURES" not in returnData: returnData["PRESSURES"] = {}
    if "SETPOINT" not in returnData: returnData["SETPOINT"] = {}
    if "FLOW" not in returnData: returnData["FLOW"] = {}


    print(returnData)
    return returnData


@app.post("/setstate")
async def setState(request: Request):
    body = await request.json()
    print(body)
    return body


@app.on_event("startup")
@repeat_every(seconds=20)
def generatePlot():

    try:

        data = requests.get(restADR+"Temperatures",
                            auth=statusServerAuth).json()

    except:
        return

    dbConnection = sqlite3.connect('logs.db')
    dbCursor = dbConnection.cursor()

    try:
        dbCursor.execute(
            "CREATE TABLE IF NOT EXISTS datalog1(timestamp, PRP, RGP, CFP, STP, ICP, MXP)")
    except sqlite3.OperationalError:
        pass

    DMAP = {
        "PRP": "PRP",
        "RGP": "RGP",
        "CFP": "CFP",
        "STP": "STP",
        "ICP":  "DHX-T",
        "MXP": "MXP_RUOX",
    }
    try:
        dbCursor.execute("INSERT INTO datalog1 VALUES (?, ?, ?, ?, ?, ?, ?)", [

            time.time(),
            data[DMAP["PRP"]],
            data[DMAP["RGP"]],
            data[DMAP["CFP"]],
            data[DMAP["STP"]],
            data[DMAP["ICP"]],
            data[DMAP["MXP"]],

        ])
    except Exception as e:
        print(e)

    dbConnection.commit()
    try:
        print('building')
        os.system("python ./generatePlot.py")
    except:
        print('failed')


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

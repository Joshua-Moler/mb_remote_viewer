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

from core.Valves import init as valvesInit
from core.Valves import valve_toggle, valve_open, valve_close, get_flow, check_state

from core.Pressures import init as pressuresInit
from core.Pressures import check_pressure

from core.Turbos import init as turbosInit
from core.Turbos import turbo_start, turbo_stop, turbo_ping, turbo_query

from core.Temperatures import init as temperaturesInit
from core.Temperatures import check_temperature, check_resistance

from core.ComPorts import getDeviceMap, getTemperatureSensors

deviceMap = getDeviceMap()
print(deviceMap)
if "Valves" in deviceMap:
    print(f'Initialized valve com: {valvesInit(deviceMap["Valves"])}')
if "Pressures" in deviceMap:
    print(f'Initialized pressure com: {pressuresInit(deviceMap["Pressures"])}')
if "PM1" in deviceMap:
    print(f'Initialized turbo com: {turbosInit(["PM1"], deviceMap["PM1"])}')
if "PM2" in deviceMap:
    print(f'Initialized turbo com: {turbosInit(["PM2"], deviceMap["PM2"])}')

temperaturesInit(getTemperatureSensors())


app = FastAPI()

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


@app.post("/login")
async def token():
    return {"token": 'test123'}


@app.post("/valves/toggle/{valve}")
async def valveToggle(valve):
    return valve_toggle(valve)


@app.post("/valves/open/{valve}")
async def valveOpen(valve):
    return valve_open(valve)


@app.post("/valves/close/{valve}")
async def valveClose(valve):
    return valve_close(valve)


@app.get("/valves/state")
async def valveStates():
    return check_state()


@app.get("/valves/state/{valve}")
async def valveState(valve):
    return check_state(valve)


@app.get("/flow")
async def flow():
    return get_flow()


@app.get("/pressures")
async def checkPressures():
    return check_pressure()


@app.get("/pressures/{p}")
async def checkPressure(p):
    return checkPressure(p)


@app.post("/turbos/start/{turbo}")
async def turboStart(turbo):
    return turbo_start(turbo)


@app.post("/turbos/stop/{turbo}")
async def turboStop(turbo):
    return turbo_stop(turbo)


@app.post("/turbos/handshake/{turbo}")
async def turboHandshake(turbo):
    return turbo_ping(turbo)


@app.post("/turbos/query/{turbo}")
async def turboQuery(turbo, request: Request):
    return turbo_query(turbo, request.json())


@app.get("/lakeshore/temperatures/")
async def checkTemperatures():
    return check_temperature()


@app.get("/lakeshore/values")
async def checkLakeshoreValues():
    temperatures = check_temperature()
    resistance = check_resistance()
    return (temperatures[0] and resistance[0],
            {"temperature": temperatures[1], "resistance": resistance[1]})


@app.get("/lakeshore/temperatures/{t}")
async def checkTemperature(t):
    return check_temperature(t)

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
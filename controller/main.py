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

from core.ComPorts import getDeviceMap, getTemperatureSensors, getPressureSensors, getValves

from core.Logs import init as logsInit
from core.Logs import addSensorHeader, startLog, resumeLog, insertRow, writeSensorHeader

from core.Utils.User import UserSession, UserAuth


import socketio


class TurboInfo:
    def __init__(self, id):
        self.id = id
        self.state = False
        self.speed = 0
        self.converter = 0
        self.motor = 0
        self.bearing = 0
        self.setpoint = 0

    def valueDict(self):
        return {"STATE": self.state,
                "SPEED": self.speed,
                "CONVERTER": self.converter,
                "MOTOR": self.motor,
                "BEARING": self.bearing,
                "SETPOINT": self.setpoint}


class Values:
    def fill(self, temperatureSensors, pressureSensors, Valves, Pumps, Turbos):
        self.temperatureSensors = temperatureSensors
        self.temperatures = {s: 1 for s in temperatureSensors}
        self.resistances = {s: 0 for s in temperatureSensors}
        self.pressures = {s: 1 for s in pressureSensors}
        self.flow = 1
        self.valves = {s: False for s in Valves}
        self.Pumps = {s: False for s in Pumps}
        self.Turbos = [TurboInfo(s) for s in Turbos]
        self.status = "INACTIVE"
        self.setpoint = 1

    def displayValues(self):
        return {
            "TEMPERATURES": self.temperatures,
            "PRESSURES": self.pressures,
            "FLOWS": {"": self.flow},
            "STATUS": {"": self.status},
            "SETPOINT": {"": self.setpoint},
            "VALVES": self.valves,
            "PUMPS": self.Pumps,
            "TURBOS": {turbo.id: turbo.valueDict() for turbo in self.Turbos}

        }


def initDevices():
    deviceMap = getDeviceMap()
    print(deviceMap)
    if "Valves" in deviceMap:
        print(f'Initialized valve com: {valvesInit(deviceMap["Valves"])}')
    if "Pressures" in deviceMap:
        print(
            f'Initialized pressure com: {pressuresInit(deviceMap["Pressures"])}')
    if "PM1" in deviceMap:
        print(
            f'Initialized turbo com: {turbosInit(["PM1"], [deviceMap["PM1"]])}')
    if "PM2" in deviceMap:
        print(
            f'Initialized turbo com: {turbosInit(["PM2"], [deviceMap["PM2"]])}')

    temperatureSensors = getTemperatureSensors()
    temperaturesInit(temperatureSensors)

    logsInit(list(temperatureSensors.keys()), ["Temperature", "Resistance"])

    pressureSensors = getPressureSensors()
    addSensorHeader(list(pressureSensors.keys()))
    addSensorHeader(["Flow", "Status", "Setpoint"])


app = FastAPI()

sio = socketio.AsyncServer(
    async_mode='asgi', cors_allowed_origins='http://localhost:3000')
socket_app = socketio.ASGIApp(sio)

LOGGING = False
USER_SESSION = UserSession()
values = Values()


@app.on_event("startup")
async def app_startup():
    initDevices()
    values.fill(temperatureSensors=getTemperatureSensors(),
                pressureSensors=getPressureSensors(),
                Valves=getValves(),
                Pumps={},
                Turbos=["PM1", "PM2"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["Content-Type", "Access-Control-Allow-Origin",
                   "Access-Control-Allow-Headers", "Authorization", "Set-Cookie"]
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
    return check_pressure(p)


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
    data = await request.json()
    return turbo_query(turbo, data)


@app.post("/system/set/all")
async def systemSetAll(request: Request):
    data = await request.json()
    print(data)
    valves = {}
    if 'VALVES' in data:
        valves = data['VALVES']
    pumps = {}
    if 'PUMPS' in data:
        pumps = data['PUMPS']
    turbos = {}
    if 'TURBOS' in data:
        turbos = data['TURBOS']
    returnValves = {}
    success = False
    for valve, state in valves.items():
        success, returnValves[valve] = valve_open(
            valve) if state else valve_close(valve)
        print(f"SUCCESS? {valve} : {success}")
    returnPumps = {}
    for pump, state in pumps.items():
        print(f"SUCCESS? {pump} : Not Implemented")
    returnTurbos = {}
    for turbo, state in turbos.items():
        success, returnTurbos[turbo] = turbo_start(
            turbo) if state else turbo_stop(turbo)
        print(f"SUCCESS? {turbo} : {success}")
    print({"VALVES": returnValves, "PUMPS": returnPumps, "TURBOS": returnTurbos})

    return success, {'VALVES': returnValves, 'PUMPS': returnPumps, 'TURBOS': returnTurbos}


@app.get("/lakeshore/temperatures/")
async def checkTemperatures():
    return check_temperature()


@app.get("/lakeshore/values")
async def checkLakeshoreValues():

    temperatures = check_temperature()
    print(temperatures)
    resistance = check_resistance()
    return (temperatures[0] and resistance[0],
            {"Temperature": temperatures[1], "Resistance": resistance[1]})


@app.get("/lakeshore/temperatures/{t}")
async def checkTemperature(t):
    return check_temperature(t)


@app.post("/remote/set/all")
async def setAll(request: Request):
    data = await request.json()
    valves = {}
    if 'Valves' in data:
        valves = data['Valves']
    pumps = {}
    if 'Pumps' in data:
        pumps = data['Pumps']
    returnValves = {}
    for valve, state in valves.items():
        success, returnValves[valve] = valve_open(
            valve) if state else valve_close(valve)
        print(f"SUCCESS? {valve} : {success}")
    returnPumps = {}
    for turbo, state in pumps.items():
        success, returnPumps[turbo] = turbo_start(
            turbo) if state else turbo_stop(turbo)
        print(f"SUCCESS? {turbo} : {success}")
    print({'Valves': returnValves, 'Pumps': returnPumps})

    return success, {'Valves': returnValves, 'Pumps': returnPumps}


app.mount('/', socket_app)


# values = {"TEMPERATURES":
#           {"t1": 'v2', 't2': 'v20', 't3': 'v19', 't4': 'v51'},
#           "RESISTANCES":
#           {"t1": 100, 't2': 80, 't3': 70, 't4': 60},
#           "PRESSURES":
#           {'p1': 'v3', 'p2': 'p10'},
#           "FLOWS":
#           {"": "N/A"},
#           "STATUS":
#           {"": "MANUAL"},
#           "SETPOINT": {"": "N/A"},
#           "VALVES": {"v1": False,
#                      "v2": False,
#                      "v3": False,
#                      "v4": False,
#                      "v5": False,
#                      "v6": False},
#           "PUMPS":
#           {},
#           "TURBOS": {"PM1":
#                      {"STATE": False,
#                       "SPEED": 0,
#                       "CONVERTER": 25,
#                       "MOTOR": 25,
#                       "BEARING": 25,
#                       "SETPOINT": 1000},
#                      "PM2":
#                      {"STATE": False,
#                       "SPEED": 0,
#                       "CONVERTER": 25,
#                       "MOTOR": 25,
#                       "BEARING": 25,
#                       "SETPOINT": 1000}, }}


@sio.on('connect')
async def connect(sid, env):
    print('connected to ', sid, 'with env: ', env)
    await sio.emit('values', values.displayValues())


@app.on_event('startup')
@repeat_every(seconds=5)
async def emitValues():
    await sio.emit('values', values.displayValues())


@app.on_event('startup')
@repeat_every(seconds=5)
async def pollTurbos():
    pass


@app.on_event('startup')
@repeat_every(seconds=10)
async def pollTemperatures():
    pass


@app.on_event('startup')
@repeat_every(seconds=2)
async def pollPressures():
    pass


@app.on_event('startup')
@repeat_every(seconds=5)
async def pollValves():
    pass


@app.on_event('startup')
@repeat_every(seconds=2)
async def pollFlows():
    pass


@app.on_event('startup')
@repeat_every(seconds=60*10)
async def logValues():
    if not LOGGING:
        return
    thermSuccess, thermValues = checkLakeshoreValues()
    if thermSuccess:
        writeSensorHeader(sensors={
            sensor:
            {"Temperature": values.temperatures[sensor],
             "Resistance": values.resistances[sensor]} for sensor in values.temperatureSensors})
    insertRow()


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)

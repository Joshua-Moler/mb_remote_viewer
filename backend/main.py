import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from fastapi.responses import FileResponse
import requests
from requests_oauthlib import OAuth1
import time
from hashlib import sha1
from base64 import b64encode

import secrets

import json

import sqlite3
import os
import bcrypt


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
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["Content-Type", "Access-Control-Allow-Origin",
                   "Access-Control-Allow-Headers", "Authorization", "Set-Cookie"]
)


@app.get("/")
async def root():
    return {"test": "Hello World"}


@app.get("/Plot/{param}")
async def plot(param):
    return FileResponse("./test.png")


@app.post("/logout")
async def logout(request: Request, response: Response):
    cookie = request.cookies
    print(cookie)
    if 'token' not in cookie:
        return [False]
    requests.post(restADR+"Remote/Logout", auth=getAuthFromToken(cookie))
    response.delete_cookie(key='token')
    return [True]


@app.post("/login")
async def token(request: Request, response: Response):
    data = await request.json()
    if (not 'username' in data) or (not 'password' in data):
        return {"authenticated": False}

    hashedPassword = b64encode(
        sha1(bytes(data['password'], 'utf-8')).digest()).decode()
    hashedUsername = b64encode(
        sha1(bytes(data['username'], 'utf-8')).digest()).decode()

    authRequest = requests.post(restADR+"Remote/Auth",
                                json={'username': hashedUsername,
                                      'password': hashedPassword},
                                auth=statusServerAuth)
    authResponse = authRequest.json()
    print(authResponse)
    if 'authenticated' in authResponse and authResponse['authenticated'] == False:
        return {'authenticated': False}
    if 'tokenKey' and 'tokenSecret' not in authResponse:
        raise HTTPException(500)

    accessToken = secrets.token_hex(32)

    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()

    sqlCursor.execute(
        "SELECT EXISTS(SELECT 1 FROM activeUsers WHERE username=?)", (hashedUsername,)
    )
    if sqlCursor.fetchone()[0]:
        sqlCursor.execute(
            "UPDATE activeUsers SET accessToken = ?, tokenKey = ?, tokenSecret = ?",
            (accessToken, authResponse['tokenKey'],
             authResponse['tokenSecret'])
        )
    else:
        sqlCursor.execute("INSERT INTO activeUsers VALUES(?, ?, ?, ?)",
                          (hashedUsername, accessToken, tokenKey, tokenSecret))
    db_connection.commit()

    print(accessToken)
    response.set_cookie(
        key='token', value=accessToken, samesite='none', httponly=True)

    if authResponse['authenticated']:
        return {"authenticated": True}
    else:
        return {"authenticated": False}


def validateToken(token):
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()

    sqlCursor.execute(
        "SELECT EXISTS(SELECT 1 FROM activeUsers WHERE accessToken = ?)", (token, ))

    return sqlCursor.fetchone()[0]


def getUserTokenKey(token):
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()

    sqlCursor.execute(
        "SELECT tokenKey FROM activeUsers WHERE accessToken = ?", (token,)
    )
    return sqlCursor.fetchone()[0]


def getUserTokenSecret(token):
    db_connection = sqlite3.connect('clients.db')
    sqlCursor = db_connection.cursor()

    sqlCursor.execute(
        "SELECT tokenSecret FROM activeUsers WHERE accessToken = ?", (token,)
    )
    return sqlCursor.fetchone()[0]


def getAuthFromToken(cookie):
    if 'token' not in cookie:
        print('not in cookie')
        raise HTTPException(401)
    token = cookie['token']
    if not validateToken(token):
        print('not validated')
        raise HTTPException(401)
    tokenKey = getUserTokenKey(token)
    tokenSecret = getUserTokenSecret(token)
    print(f"TOKEN KEY: {tokenKey}\nTOKEN SECRET: {tokenSecret}")
    auth = OAuth1(clientKey, clientSecret, tokenKey, tokenSecret)
    return auth


@app.get("/status")
async def status(request: Request):
    cookie = request.cookies
    auth = getAuthFromToken(cookie)
    response = requests.get(restADR+"State", auth=auth)
    try:
        data = response.json()
        print('data', data)
        status = {}
        for valve in data['Valves']:
            status[valve.lower()] = not data["Valves"][valve]
        print('status', status)
        for pump in data["Pumps"]:
            status[pump.upper()] = data["Pumps"][pump]
    except Exception as e:
        print(e)
        status = {}
    print(status)
    return status


@app.get("/values")
async def values(request: Request):
    cookie = request.cookies
    auth = getAuthFromToken(cookie)
    response = requests.get(restADR+"All", auth=auth)
    if response.status_code != 200:
        raise HTTPException(response.status_code)
    try:
        data = response.json()
    except:
        data = {}
    returnData = {ii.upper(): data[ii] for ii in data}

    if "STATUS" not in returnData:
        returnData["STATUS"] = {}
    if "TEMPERATURES" not in returnData:
        returnData["TEMPERATURES"] = {}
    if "PRESSURES" not in returnData:
        returnData["PRESSURES"] = {}
    if "SETPOINT" not in returnData:
        returnData["SETPOINT"] = {}
    if "FLOW" not in returnData:
        returnData["FLOW"] = {}

    print(returnData)
    return returnData


@app.post("/setstate")
async def setState(request: Request):
    cookie = request.cookies
    auth = getAuthFromToken(cookie)
    body = await request.json()
    response = requests.post(
        restADR+"State/Set", auth=auth, json=body)
    if response.status_code != 200:
        raise HTTPException(response.status_code)
    try:
        success, state = response.json()
    except:
        success, state = [False, body]

    print((success, state))

    newState = {}
    if 'valves' in state:
        for valve in state['valves']:
            newState[valve.lower()] = not state['valves'][valve]
    if 'pumps' in state:
        for pump in state['pumps']:
            newState[pump.upper()] = state['pumps'][pump]

    print((success, newState))

    return (success, newState)


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

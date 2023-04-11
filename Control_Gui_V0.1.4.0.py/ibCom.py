import time

from time import sleep
from datetime import datetime
from operator import xor
from copy import copy
import smtplib
import ssl
import traceback
import random

import requests
from requests_oauthlib import OAuth1

import threading

from lakeshore import Model372, generic_instrument, Model372HeaterResistance, Model372HeaterOutputUnits
from lakeshore import Model372SampleHeaterOutputRange as sampleRange

import json

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
    restADR = "http://127.0.0.1:5000/"

statusServerAuth = OAuth1(clientKey, clientSecret, tokenKey, tokenSecret)


def SendToRest(route, data, auth):
    
    try:
        requests.put(restADR+route, json=data, auth=auth, timeout=3)

    except Exception as e:
        print(e)


def SendToRestDaemon(route, data):
    daemon = threading.Thread(target=SendToRest, kwargs={
                              "route": route, "data": data, "auth": statusServerAuth}, daemon=True)
    print(threading.enumerate())
    daemon.start()


# Handes email messaging for status updates


class email:
    def __init__(self, recipients, updateTime):
        self.port = 465
        self.server = 'smtp.gmail.com'
        self.sender = 's1logdata@gmail.com'
        self.password = 'rwsgnvwnjpduipis'
        self.recipients = recipients
        self.context = ssl.create_default_context()
        self.updateTimer = 0
        self.updateTime = updateTime

    def update(self, message):
        if time.perf_counter() - self.updateTimer >= self.updateTime:
            self.updateTimer = time.perf_counter()
            try:
                with smtplib.SMTP_SSL(self.server, self.port, context=self.context) as server:
                    server.login(self.sender, self.password)
                    for reciever in self.recipients:
                        server.sendmail(self.sender, reciever, message)
            except Exception as e:
                print(f'Failed to send email: {e}')


# Handles communication with the pressure gauges
class pressureCom:
    url = "http://127.0.0.1:8080/pressures"

    def __init__(self):
        self.updateTimer = 0
        self.updateTime = 1
        self.pressures = ['0']*6

    def getSensorReadout(self):
        try:
            success, pressures = requests.get(
                "http://127.0.0.1:8080/pressures").json()
            if success:
                self.pressures = pressures
            return success
        except Exception as e:
            print(e)
            return False

    def update(self):
        if time.perf_counter() - self.updateTimer >= self.updateTime:
            self.updateTimer = time.perf_counter()
            if self.getSensorReadout():

                SendToRestDaemon("Pressures", {
                    f"P{ii+1}": jj for ii, jj in enumerate(self.pressures)})
                return True
        return False


# Generates fake data for the temperature sensors. Used to test plotting and logging features
class func:
    def __init__(self, n):
        self.n = n
        self.val = n*300/(1+2**(0.01*(0-80)))+10
        self.iterCount = 0

    def getNext(self):
        self.val = self.n*300/(1+2**(0.05*(self.iterCount-100)))+10
        self.iterCount += 1
        return self.val


class lakeShoreCom:
    def __init__(self, sensors, heaters=None):
        self.updateTimer = time.perf_counter()
        self.updateTime = 3
        self.sensors = sensors
        self.currentTemp = [0] * len(sensors)
        self.currentRes = [0] * len(sensors)
        self.actualSampleHeaterCurrent = 0
        self.actualStillHeaterPercent = 0
        self.actualWarmupHeaterPercent = 0


    def update(self):
        if time.perf_counter() - self.updateTimer >= self.updateTime:
            self.updateTimer = time.perf_counter()
            success = self.pullValues()

            SendToRestDaemon("Temperatures", {
                jj: self.currentTemp[ii] for ii, jj in enumerate(self.sensors)})

            return success
        return False

    def pullValues(self):
        try:
            print('LS request start')
            success, values = requests.get(
                "http://127.0.0.1:8080/lakeshore/values").json()
            print('LS request finish')
            if success:
                for ii, sensor in enumerate(self.sensors):
                    if sensor in values['temperature']:
                        self.currentTemp[ii] = values['temperature'][sensor]
                    if sensor in values['resistance']:
                        self.currentRes[ii] = values['resistance'][sensor]
            return success
        except Exception as e:
            print(e)
            return False

    def setupWarmupHeater(self, resistance: float, max_power: float, max_voltage=None):
        print(f"setupwarmupHeater: {resistance}, {max_power}, {max_voltage}")
        return True

    def setupSampleHeater(self, resistance: float):
        print(f"setupSampleHeater: {resistance}")
        return True

    def setSampleHeaterOutputCurrent(self, current: float):
        print(f"setSampleHeaterOutputCurrent: {current}")
        return True

    def setWarmupHeaterOutputCurrent(self, current: float):
        print(f"setWarmupHeaterOutputCurrent: {current}")
        return True

    def setWarmupHeaterOutputPercent(self, percent: float):
        print(f"setWarmupHeaterOutputPercent: {percent}")
        return True

    def setStillOutput(self, power: float):
        print(f"setStillOutput: {power}")
        return True

    def stopWarmupHeater(self):
        print("stopWarmupHeater")
        return True

    def stopStillHeater(self):
        print("stopStillHeater")
        return True

    def stopSampleHeater(self):
        print("stopSampleHeater")
        return True

    def getSampleHeaterOutputCurrent(self):
        self.actualSampleHeaterCurrent = 0
        return self.actualSampleHeaterCurrent

    def getWarmupHeaterOutput(self):
        self.actualWarmupHeaterPercent = 0
        return self.actualWarmupHeaterPercent

    def getStillHeaterOutput(self):
        self.actualStillHeaterPercent = 0
        return self.actualStillHeaterPercent


class lakeShoreComTest:
    def __init__(self, sensors):
        self.updateTimer = time.perf_counter()
        self.updateTime = 3
        self.sensors = sensors
        self.currentTemp = [0]*len(sensors)
        self.currentRes = [0]*len(sensors)
        self.f = [func(ii+1) for ii in range(len(sensors))]
        self.actualWarmupHeaterPercent = 0
        self.actualSampleHeaterCurrent = 0
        self.actualStillHeaterPercent = 0

    # For non-testing implementation, uncomment lines marked with '>'
    #  and comment lines marked with '<'
    def update(self):
        if time.perf_counter() - self.updateTimer >= self.updateTime:
            self.updateTimer = time.perf_counter()
            self.currentTemp = [self.f[ii].getNext()
                                for ii in range(len(self.sensors))]
            self.currentRes = [self.f[ii].getNext(
            )/100 for ii in range(len(self.sensors))]
            self.getSampleHeaterOutputCurrent()
            self.getWarmupHeaterOutput()
            self.getStillHeaterOutput()
            SendToRestDaemon("Temperatures", {
                jj: self.currentTemp[ii] for ii, jj in enumerate(self.sensors)})

            return True
        return False

    def setupWarmupHeater(self, resistance: float, max_power: float, max_voltage=None):
        print(f"setupwarmupHeater: {resistance}, {max_power}, {max_voltage}")
        return True

    def setupSampleHeater(self, resistance: float):
        print(f"setupSampleHeater: {resistance}")
        return True

    def setSampleHeaterOutputCurrent(self, current: float):
        print(f"setSampleHeaterOutputCurrent: {current}")
        return True

    def setWarmupHeaterOutputCurrent(self, current: float):
        print(f"setWarmupHeaterOutputCurrent: {current}")
        return True

    def setWarmupHeaterOutputPercent(self, percent: float):
        print(f"setWarmupHeaterOutputPercent: {percent}")
        return True

    def setStillOutput(self, power: float):
        print(f"setStillOutput: {power}")
        return True

    def stopWarmupHeater(self):
        print("stopWarmupHeater")
        return True

    def stopStillHeater(self):
        print("stopStillHeater")
        return True

    def stopSampleHeater(self):
        print("stopSampleHeater")
        return True

    def getSampleHeaterOutputCurrent(self):
        self.actualSampleHeaterCurrent = round(random.random(), 3)
        return self.actualSampleHeaterCurrent

    def getWarmupHeaterOutput(self):
        self.actualWarmupHeaterPercent = round(random.random(), 3)
        return self.actualWarmupHeaterPercent

    def getStillHeaterOutput(self):
        self.actualStillHeaterPercent = round(random.random(), 3)
        return self.actualStillHeaterPercent


# Handles communication with the valve board
class valveCom:
    def __init__(self):
        self.valveNum = 27
        self.valveState = []
        self.updateTimer = 0
        self.updateTime = 1

    def toggleValve(self, valve):
        try:

            success, newValue = requests.post(
                f"http://127.0.0.1:8080/valves/toggle/{valve}").json()

            return success
        except Exception as e:
            print(e)
            return False

    def checkState(self):
        try:
            success, state = requests.get(
                "http://127.0.0.1:8080/valves/state").json()
            print('GOT STATE:', success, state)

            if success:
                self.valveState = state
                return state
            return None
        except Exception as e:
            print(e)
            return False

    def setUpdateTime(self, time):
        self.updateTime = 2

    def update(self, checkTimer=True):

        if time.perf_counter() - self.updateTimer >= self.updateTime or (not checkTimer):
            self.checkState()
            self.updateTimer = time.perf_counter()
            SendToRestDaemon("Valves", {
                f"V{ii+1}": jj for ii, jj in enumerate(self.valveState)})
            return True
        return False

    def getValveState(self):
        return copy(self.valveState)

    def getFlowVoltage(self):
        try:
            success, flow = requests.get("http://127.0.0.1:8080/flow").json()
            if success:
                return flow
            return 'N/A'
        except Exception as e:
            print(e)
            return 'N/A'

# Handles communication with the turboVac


class opsManager():
    def __init__(self):
        self.running = False
        self.timers = {'main': 0}
        self.mainTimer = 2

        self.response = {
            "running": False,
            "stator_frequency": "0000",
            "converter_temperature": "0000",
            "motor_current": "0000",
            "bearing_temperature": "0000",
            "circuit_voltage": "0000",
            "type": "0000",
            "number": "0000",
            "index": "0000",
            "value": "0000"
        }

        self.running = self.response["running"]

        self.id = ''

    def sendQuery(self, query: dict):
        try:
            success, response = requests.post(
                f"http://127.0.0.1:8080/turbos/query/{self.id}",json=query).json()

            if success:
                for item in response:
                    self.response[item] = response[item]

            return success

        except Exception as e:
            print(e)
            return False

    def _startOperation_(self):
        try:
            success, response = requests.post(
                f"http://127.0.0.1:8080/turbos/start/{self.id}"
            ).json()

            return success
        except Exception as e:
            print(e)
            return False
    def _stopOperation_(self):
        try:
            print(f"Stopping Turbo: {self.id}")
            success, response = requests.post(
                f"http://127.0.0.1:8080/turbos/stop/{self.id}"
            ).json()

            return success
        except Exception as e:
            print(e)
            return False

    def resetTimer(self, timer='main'):
        if timer in self.timers:
            self.timers[timer] = time.perf_counter()
            return True
        return False

    def pollTimer(self, timer='main', reset=True):
        if timer in self.timers:
            actualDuration = time.perf_counter() - self.timers[timer]
            if reset:
                self.resetTimer(timer)
            return actualDuration
        return -1

    def queryTimer(self, timer='main', duration=None, reset=True):
        if duration == None:
            duration = self.mainTimer
        if timer in self.timers:
            actualDuration = self.pollTimer(timer, reset=False)
            if actualDuration >= duration:
                self.resetTimer(timer)
                return True
        return False

    def newTimer(self, timer):
        self.timers[timer] = time.perf_counter()

    def removeTimer(self, timer):
        if timer in self.timers:
            del self.timers[timer]
            return True
        return False

    def update(self):
        if self.queryTimer():
            try:
                success, response = requests.post(
                    f"http://127.0.0.1:8080/turbos/handshake/{self.id}").json()

                if success:
                    for item in response:
                        self.response[item] = response[item]

                    self.running = self.response["running"]

                SendToRestDaemon("Pumps", {
                    self.id: self.running})

                return success

            except Exception as e:
                print(e)
                return False

import random
from random import choice
import sys
import serial
from time import sleep


def get_random_bool():
    return random.choice([True, False])


def turbo_start(p=None):
    return (get_random_bool(), p)


def turbo_stop(p=None):
    return (get_random_bool(), p)


# Processes and stores serial responses from the turboVac
class Response:

    def __init__(self, b=None):
        self.isRunning = False
        self.tg = bytes(24)
        if b:
            self.tg = b
            self.response = []
            for ii in range(24):
                self.response.append(
                    ((int.from_bytes(b, 'big', signed=False)) >> (8 * ii)) & 255)
            self.response.reverse()
            self.stx = self.response[0]
            self.lge = self.response[1]
            self.adr = self.response[2]
            self.pke = int(
                format(self.response[3], '08b') + format(self.response[4], '08b'), 2)
            self.ind = self.response[6]
            self.pwe = int(format(self.response[7], '08b')+format(self.response[8], '08b') +
                           format(self.response[9], '08b')+format(self.response[10], '08b'), 2)
            self.pzd1 = format(
                self.response[11], '08b') + format(self.response[12], '08b')
            self.pzd2 = int(
                format(self.response[13], '08b')+format(self.response[14], '08b'), 2)
            self.pzd3 = int(
                format(self.response[15], '08b')+format(self.response[16], '08b'), 2)
            self.pzd4 = int(
                format(self.response[17], '08b')+format(self.response[18], '08b'), 2)
            self.pzd5 = int(
                format(self.response[19], '08b')+format(self.response[20], '08b'), 2)
            self.pzd6 = int(
                format(self.response[21], '08b')+format(self.response[22], '08b'), 2)
            self.bcc = self.response[23]
            if self.pzd1[13] == '1':
                self.isRunning = True
                return
            self.isRunning = False
            return

    def getResponse(self, b):
        if b:
            self.tg = b
            self.response = []
            for ii in range(24):
                self.response.append(
                    ((int.from_bytes(b, 'big', signed=False)) >> (8 * ii)) & 255)
            self.response.reverse()
            self.stx = self.response[0]
            self.lge = self.response[1]
            self.adr = self.response[2]
            self.pke = int(
                format(self.response[3], '08b') + format(self.response[4], '08b'), 2)
            self.ind = self.response[6]
            self.pwe = int(format(self.response[7], '08b')+format(self.response[8], '08b') +
                           format(self.response[9], '08b')+format(self.response[10], '08b'), 2)
            self.pzd1 = format(
                self.response[11], '08b') + format(self.response[12], '08b')
            self.pzd2 = int(
                format(self.response[13], '08b')+format(self.response[14], '08b'), 2)
            self.pzd3 = int(
                format(self.response[15], '08b')+format(self.response[16], '08b'), 2)
            self.pzd4 = int(
                format(self.response[17], '08b')+format(self.response[18], '08b'), 2)
            self.pzd5 = int(
                format(self.response[19], '08b')+format(self.response[20], '08b'), 2)
            self.pzd6 = int(
                format(self.response[21], '08b')+format(self.response[22], '08b'), 2)
            self.bcc = self.response[23]
            if self.pzd1[13] == '1':
                self.isRunning = True
                return
            self.isRunning = False
            return

    def printResponse(self):
        pkefill = ''
        for ii in range(16-len(bin(self.pke)[2:])):
            pkefill += '0'
        print(f'Slave Address: {self.adr}')
        print(f'Parameter Access: {(pkefill +bin(self.pke)[2:])[0:4]}')
        print(f'Parameter Number: {self.pke & 4095}')
        print(f'Parameter Index: {self.ind}')
        print(f'Paramter Value: {self.pwe}')
        print(f'Current Stator Frequency: {self.pzd2}')
        print(f'Current Temperature: {self.pzd3}')
        print(f'Current Motor Current {self.pzd4}')
        print(f'Current Bearing Temperature: {self.pzd5}')
        print(f'Current Circuit Voltage: {self.pzd6}')

    def getAddress(self):
        return self.adr

    def getParameterAccess(self):
        pkefill = ''
        for ii in range(16-len(bin(self.pke)[2:])):
            pkefill += '0'
        return (pkefill + bin(self.pke)[2:])[0:4]

    def getParameterNumber(self):
        return self.pke & 4095

    def getParameterIndex(self):
        return self.ind

    def getParameterValue(self):
        return self.pwe

    def getStatorFrequency(self):
        return self.pzd2

    def getCurrentTemperature(self):
        return self.pzd3

    def getMotorCurrent(self):
        return self.pzd4

    def getBearingTemperature(self):
        return self.pzd5

    def getCircuitVoltage(self):
        return self.pzd6

    def getStatusBits(self):
        return self.pzd1

    def verifyBCC(self):
        bcc = 0
        for ii in range(len(self.response)-1):
            bcc = xor(bcc, self.response[ii])
        if self.bcc == bcc:
            return True
        return False


# Processes and stores queries for the turboVac
class Query:
    def __init__(self, stx=2, lge=22):
        self.stx = stx
        self.lge = lge
        self.adr = 0
        self.pke = 0
        self.ind = 0
        self.pwe = 0
        self.pzd1 = 0
        self.pzd2 = 0
        self.bcc = 0
        self.buildTelegram()

    def buildTelegram(self):
        self._updateTelegram_()
        self._buildBCC_()

    def _buildBCC_(self):
        self.bcc = 0
        for ii in range(len(self.tg)-1):
            self.bcc = xor(self.bcc, self.tg[ii])
            self._updateTelegram_()

    def _updateTelegram_(self):
        self.tg = bytes([self.stx, self.lge, self.adr, ((self.pke >> 8) & 255), (self.pke & 255), 0, self.ind, ((self.pwe >> 24) & 255), ((self.pwe >> 16) & 255), ((self.pwe >> 8) & 255), (self.pwe & 255),
                         (self.pzd1 >> 8) & 255, (self.pzd1 & 255), (self.pzd2 >> 8) & 255, (self.pzd2 & 255), 0, 0, 0, 0, 0, 0, 0, 0, self.bcc])

    def setAddress(self, adr):
        self.adr = adr
        self.buildTelegram()

    def setParameterAccess(self, pke=None, des=0, num=0):
        if pke == None:
            self.pke = (num & 2047) | ((des << 12) & 61440)
            self.buildTelegram()
            return
        self.pke = pke
        self.buildTelegram()

    def setParameterIndex(self, ind):
        self.ind = ind
        self.buildTelegram()

    def setParameterValue(self, pwe):
        self.pwe = pwe
        self.buildTelegram()

    def setControlBits(self, pzd1=None, start=0, setSpeed=0, control=0):
        if pzd1 == None:
            self.pzd1 = self.pzd1 | start | (setSpeed << 6) | (control << 10)
            self.buildTelegram()
            return
        self.pzd1 = pzd1
        self.buildTelegram()

    def setTargetFrequency(self, pzd2):
        self.pzd2 = pzd2
        self.buildTelegram()


# Handles communication with the turboVac
class opsManager():
    def __init__(self):
        self.running = False
        self.timers = {'main': 0}
        self.mainTimer = 2
        self.queries = {}
        self.telegramLog = []
        self.telegramCount = 0
        self.elementWithMethod = {}
        self.startOnEvent = []
        self.stopOnEvent = []
        self.startQuery = Query()
        self.startQuery.setControlBits(start=1, control=1)
        self.stopQuery = Query()
        self.stopQuery.setControlBits(start=0, control=1)
        self.response = Response()
        self.serialManager = serial.Serial()
        self.serialManager.baudrate = 19200
        self.serialManager.parity = serial.PARITY_EVEN
        self.serialManager.write_timeout = 0.5
        self.serialManager.timeout = 0.5
        self.initializationMoment = str(datetime.now()).replace(
            ' ', '_').replace(':', '-') + '.txt'

    def _checkRunning_(self):
        self.sendQuery(Query())
        if self.response.isRunning:
            self.running = True
            # print('Pump is Running')
            return True
        self.running = False
        # print('Pump is not Running')
        return False

    def sendQuery(self, query: Query):
        try:
            if self.serialManager.isOpen():
                self.telegramLog.append([])
                self.telegramLog[self.telegramCount].append(
                    str(datetime.now()))
                self.telegramLog[self.telegramCount].append(str(query.tg))
                self.serialManager.write(query.tg)
                sleep(0.01)
                response = self.serialManager.read(24)
                self.telegramLog[self.telegramCount].append(str(response))
                self.telegramCount += 1
                if response:
                    self.response.getResponse(response)
                    return True
                # print('No response')
                return False
        except PermissionError:
            pass
        # print('serial communication is not open.')
        # print('check that the cable is connected and select a port')
        return False

    def _startOperation_(self):
        if not self.running:
            if self.sendQuery(self.startQuery):
                sleep(1)
                self._checkRunning_()
                if self.running:
                    return True
                # print('pump did not start')
                return False
            # print('start query failed')
            return False
        # print('pump is already running')
        return False

    def _maintainOperationState_(self):
        self._checkRunning_()
        if not self.running:
            if self.sendQuery(self.stopQuery):
                if not self.running:
                    return True
                # print('pump changed state unexpectedly')
                return False
            # print('lost communication with pump')
            return False
        if self.running:
            if self.sendQuery(self.startQuery):
                if self.running:
                    return True
                # print('pump changed state unexpectedly')
                return False
            # print('lost communication with pump')
            return False

    def _stopOperation_(self):

        if self.running:
            if self.sendQuery(self.stopQuery):
                sleep(1)
                self._checkRunning_()
                if not self.running:
                    return True
                # print('pump did not stop')
                return False
            # print('stop query failed')
            return False
        # print('pump is not running')
        return False

    def setSerialPort(self, serialPort):
        if self.serialManager.isOpen():
            self.serialManager.close()
        self.serialManager.port = serialPort
        try:
            self.serialManager.open()
        except FileNotFoundError:
            self.serialManager.close()
            self.serialManager.port = None
        except PermissionError:
            self.serialManager.close()
            self.serialManager.port = None
        # print(f'new serial port {serialPort} enabled')

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

    def newQuery(self, query, address=None, parameterAccess=None, parameterIndex=None,
                 parameterValue=None, controlBits=None, targetFrequency=None):
        self.queries[query] = Query()
        if address:
            self.queries[query].setAddress(address)
        if parameterAccess:
            self.queries[query].setParameterAccess(parameterAccess)
        if parameterIndex:
            self.queries[query].setParameterIndex(parameterIndex)
        if parameterValue:
            self.queries[query].setParameterValue(parameterValue)
        if controlBits:
            self.queries[query].setControlBits(controlBits)
        if targetFrequency:
            self.queries[query].setTargetFrequency(targetFrequency)

    def updateQuery(self, query, address=None, parameterAccess=None, parameterIndex=None,
                    parameterValue=None, controlBits=None, targetFrequency=None):
        if query not in self.queries:
            return
        if address:
            self.queries[query].setAddress(address)
        if parameterAccess:
            self.queries[query].setParameterAccess(parameterAccess)
        if parameterIndex:
            self.queries[query].setParameterIndex(parameterIndex)
        if parameterValue:
            self.queries[query].setParameterValue(parameterValue)
        if controlBits:
            self.queries[query].setControlBits(controlBits)
        if targetFrequency:
            self.queries[query].setTargetFrequency(targetFrequency)

    def update(self):
        if self.serialManager.isOpen():
            try:
                if self.serialManager.port not in [listports.comports()[ii].device for ii in range(len(listports.comports()))]:
                    # print('serial port not connected')
                    self.closePort()
            except IndexError:
                pass
            if self.queryTimer():
                self._maintainOperationState_()
                self.running = self.response.isRunning
                return True
        return False

    def getLogs(self):
        out = ''
        for ii in self.telegramLog:
            out += ii[0] + '\n'
            out += 'Query:\n' + ii[1] + '\n'
            out += 'Response:\n' + ii[2] + '\n'
            out += '\n'
        return out

    def closePort(self):
        if self.serialManager.isOpen():
            self.serialManager.close()
            self.serialManager = serial.Serial()
            self.serialManager.baudrate = 19200
            self.serialManager.parity = serial.PARITY_EVEN
            self.serialManager.write_timeout = 0.5
            self.serialManager.timeout = 0.5


_turbo_com = {}


def init(identifiers: list, serialPorts: list):
    for ii, jj in zip(identifiers, serialPorts):
        _turbo_com[ii] = opsManager()
        _turbo_com[ii].setSerialPort(jj)
    ports = {ii: jj.serialManager.port for ii, jj in _turbo_com.items()}

    # Success if all requested com managers have been assigned a port.
    # Returns all com managers and their corresponding ports.
    return (all(ports.values()), ports)


def turbo_start(p=None):
    if p == None:
        success = []
        for ii in _turbo_com.values():
            success.append(ii._startOperation_())

        # Success if all turbos started successfully.
        # Returns the running state of all turbos
        return (all(success), {ii: jj.running for ii, jj in _turbo_com.items()})

    if hasattr(p, '__iter__'):
        success = []
        for ii in p:
            success.append(_turbo_com[ii]._startOperation_()
                           if ii in _turbo_com else False)

        # Success if all requested turbos started successfully.
        # Returns the running state of all turbos
        return (all(success), {ii: jj.running for ii, jj in _turbo_com.items()})

    success = _turbo_com[p]._startOperation_() if p in _turbo_com else False

    # Success if the requested turbo started successfully.
    # Returns the running state of all turbos
    return (success, {ii: jj.running for ii, jj in _turbo_com.items()})


def turbo_stop(p=None):
    if p == None:
        success = []
        for ii in _turbo_com.values():
            success.append(ii._stopOperation_())

        # Success if all turbos stopped successfully.
        # Returns the running state of all turbos
        return (all(success), {ii: jj.running for ii, jj in _turbo_com.items()})

    if hasattr(p, '__iter__'):
        success = []
        for ii in p:
            success.append(_turbo_com[ii]._stopOperation_()
                           if ii in _turbo_com else False)

        # Success if all requested turbos stopped successfully.
        # Returns the running state of all turbos
        return (all(success), {ii: jj.running for ii, jj in _turbo_com.items()})

    success = _turbo_com[p]._stopOperation_() if p in _turbo_com else False

    # Success if the requested turbo stopped successfully.
    # Returns the running state of all turbos
    return (success, {ii: jj.running for ii, jj in _turbo_com.items()})

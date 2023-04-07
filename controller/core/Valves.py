import time
import serial
import serial.tools.list_ports as listports
from time import sleep
from copy import copy
import traceback


# Handles communication with the valve board
valveDict = {'v'+str(ii+1): chr(ord('A') + ii) for ii in range(27)}


class valveCom:
    def __init__(self):
        self.serialManager = serial.Serial()
        self.serialManager.baudrate = 57600
        self.serialManager.write_timeout = 0.5
        self.serialManager.timeout = 0.5
        self.valveNum = 27
        self.valveState = []
        self.updateTimer = 0
        self.updateTime = 1
        self.isInit = False

    def setSerialPort(self, serialPort):
        if self.serialManager.isOpen():
            self.serialManager.close()
        self.serialManager.port = serialPort
        try:
            self.serialManager.open()
            self.updateTimer = time.perf_counter()
        except (FileNotFoundError, PermissionError, serial.serialutil.SerialException) as e:
            print(traceback.format_exc())
            self.serialManager.close()
            self.serialManager.port = None

    def closePort(self):
        if self.serialManager.isOpen():
            self.serialManager.close()
            self.serialManager = serial.Serial()
            self.serialManager.baudrate = 57600
            self.serialManager.write_timeout = 0.5
            self.serialManager.timeout = 0.5

    def toggleValve(self, valve):
        print('t')
        if self.serialManager.isOpen() and self.valveState != []:
            oldValveState = self.valveState[int(valve[1:])-1]
            if valve in valveDict:
                try:
                    self.serialManager.write(bytes(valveDict[valve], 'utf-8'))
                    response = self.serialManager.readline()[:-2]
                    self.valveState = [ii for ii in response]
                    print(self.valveState)
                except PermissionError:
                    print('nah')
                    return None
            return self.valveState[int(valve[1:])-1] != oldValveState
        return None

    def checkState(self):
        print('called')
        if self.serialManager.isOpen():
            print('entered')
            try:
                self.serialManager.write(bytes('1', 'utf-8'))
                time.sleep(0.1)
                response = self.serialManager.readline()[:-2]
                self.valveState = [ii for ii in response]
                self.valveNum = len(self.valveState)
                print('succeeded')
                return self.valveState

            except PermissionError:
                print('permission error')
                return

    def setUpdateTime(self, time):
        self.updateTime = 2

    def update(self, checkTimer=True):

        if time.perf_counter() - self.updateTimer >= self.updateTime or (not checkTimer):
            self.checkState()
            self.updateTimer = time.perf_counter()
            return True
        return False

    def getValveState(self):
        return copy(self.valveState)

    def getFlowVoltage(self):
        if self.serialManager.isOpen():
            try:
                self.serialManager.write(bytes('?', 'utf-8'))
                response = str(
                    round(float(self.serialManager.readline()[:-2])*2/3.3, 2))
                return response
            except PermissionError:
                return 'N/A'

        else:
            return 'N/A'


_valve_com = valveCom()

# Must be called before communications begin. Set's the serial port for serial communication with the valve board.


def init(serialPort):
    _valve_com.setSerialPort(serialPort)
    attemps = 10
    sleep(1)
    while attemps and _valve_com.valveState == []:
        _valve_com.checkState()
        attemps -= 1
        sleep(1)

    # Success if the serial port was set. Returns the current valve states.
    if _valve_com.serialManager.port != None and _valve_com.valveState:
        _valve_com.isInit = True
    return (_valve_com.serialManager.port != None, _valve_com.valveState)


# Opens a single valve


def valve_open(valve):
    if not _valve_com.isInit:
        return (False, False)
    if type(valve) == str:
        valve = int(valve[1:])
    initialState = _valve_com.valveState[valve - 1]
    print(initialState)
    if not initialState:
        _valve_com.toggleValve('v'+str(valve))
    newState = _valve_com.valveState[valve - 1]
    print(newState, initialState)

    # Success if the valve is opened. Returns the final state of the valve.
    return (newState, newState)

# Closes a single valve


def valve_close(valve):
    if not _valve_com.isInit:
        return (False, False)
    if type(valve) == str:
        valve = int(valve[1:])
    initialState = _valve_com.valveState[valve - 1]
    if initialState:
        _valve_com.toggleValve('v'+str(valve))
    newState = _valve_com.valveState[valve - 1]

    # Success if the valve is closed. Returns the final state of the valve.
    return (not newState, newState)


def valve_toggle(valve):
    if not _valve_com.isInit:
        print('calling')
        return (False, False)

    if type(valve) == str:
        valve = int(valve[1:])
    initialState = _valve_com.valveState[valve - 1]
    _valve_com.toggleValve('v'+str(valve))
    newState = _valve_com.valveState[valve - 1]

    return (newState != initialState, newState)


def check_state(valve=None):
    state = _valve_com.checkState()
    success = state != None
    if valve == None:
        return (success, state)

    if type(valve) == str:
        valve = int(valve[1:])

    if state != None:
        state = state[valve - 1]

    return (success, state)


def get_flow():
    if not _valve_com.isInit:
        print('calling')
        return (False, 'N/A')
    flow = _valve_com.getFlowVoltage()
    success = flow != 'N/A'
    return (success, flow)

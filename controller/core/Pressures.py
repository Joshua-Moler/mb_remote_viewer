import random
from random import choice
import sys
import serial
import time
from time import sleep


class pressureCom:
    def __init__(self):
        self.pressures = ['0']*6
        self.serialManager = serial.Serial()
        self.serialManager.baudrate = 9600
        self.serialManager.write_timeout = 0.5
        self.serialManager.timeout = 0.5
        self.serialManager.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.status = ['0']*6

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
            self.serialmanager.close()
            self.serialManager.port = None

    def getSensorReadout(self):
        try:
            self.serialManager.write(bytes('PRX\r\n', encoding='utf-8'))
            response = self.serialManager.readline()
            if response == b'\x06\r\n':
                self.serialManager.write(bytes(chr(5), encoding='utf-8'))
                data = str(self.serialManager.readline())
                temp = data.split(',')
                pressures = [temp[ii] for ii in range(1, len(temp), 2)]
                pressures[-1] = pressures[-1].replace('\\r\\n\'', '')
                status = [temp[ii] for ii in range(0, len(temp), 2)]
                status[0].replace('b\'', '')
                self.pressures = pressures
                self.status = status
                return True
            return False
        except:
            print('Pressure Com Failed')
            return False

    def closePort(self):
        if self.serialManager.isOpen():
            self.serialManager = serial.Serial()
            self.serialManager.baudrate = 9600
            self.serialManager.write_timeout = 0.5
            self.serialManager.timeout = 0.5
            self.serialManager.parity = serial.PARITY_NONE
            self.stopbits = serial.STOPBITS_ONE


_pressure_com = pressureCom()


def init(serialPort):
    _pressure_com.setSerialPort(serialPort)
    sleep(1)
    for ii in range(10):
        if _pressure_com.getSensorReadout():
            break
    # Success if the serial port was set. Returns the current pressure values.
    return (_pressure_com.serialManager.port != None, _pressure_com.pressures)


def check_pressures():
    # Success if the pressures were successfully read. Returns the current pressure values
    return (_pressure_com.getSensorReadout(), _pressure_com.pressures)


def check_pressure(p=None):
    if p == None:

        # Success if the pressures were successfully read. Returns the current pressure values
        return check_pressures()
    success, pressures = check_pressures()
    if hasattr(p, '__iter__'):

        returnPressures = [pressures[ii]
                           for ii in p if ii in range(len(pressures))]
        success = success and (len(returnPressures) == len(p))

        # Success if requested pressures were successfully updated. Returns the current values of the requested pressures.
        return (success, returnPressures)

    try:
        returnPressure = pressures[int(p)]
    except ValueError:
        success = False
        returnPressure = -1
    except IndexError:
        success = False
        returnPressure = -2

    # Success if requested pressure was successfully updated. Returns the requested pressure if the request was valid.
    # Returns an error code if the request was invalid:
    #   -1 if requested pressure is not an int
    #   -2 if requested pressure does not exist
    return (success, returnPressure)

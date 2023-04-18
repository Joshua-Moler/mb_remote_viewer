import serial.tools.list_ports as list_ports
import json


def getDeviceMap():

    ports = list(list_ports.comports())

    with open("./settings.json") as configFile:

        configJSON = json.load(configFile)
        devices = configJSON["Devices"]
        deviceMap = {}
        print(ports)
        for port in ports:
            print(port.description)

            for device in devices:
                deviceData = devices[device]
                if port.serial_number == deviceData['serial_number'] and \
                        port.pid == deviceData['pid'] and \
                        port.vid == deviceData['vid']:
                    deviceMap[device] = port.device
    return deviceMap


def getTemperatureSensors():
    with open("./settings.json") as configFile:

        configJSON = json.load(configFile)
        sensors = configJSON["Sensors"]["Temperature"]

        return sensors


def getPressureSensors():
    with open("./settings.json") as configFile:

        configJSON = json.load(configFile)
        sensors = configJSON["Sensors"]["Pressure"]

        return sensors


def getValves():
    with open('./settings.json') as configFile:
        configJSON = json.load(configFile)
        valves = configJSON["Valves"]

        return valves

from core.Utils.LogSystem import LogSystem


BASEHEADERATTRIBUTES = ["Timestamp", "Datetime", "State Change",
                        "Valve State", "Turbo Speed (PM1)", "Turbo Speed (PM2)", "Events"]

logger = LogSystem('C:/LOGS')
loggerEvents = []
currentRow = {}


class UserEvent:
    def __init__(self, user, eventType, eventValues, valveStateBefore, valveStateAfter, pumpStateBefore, pumpStateAfter):
        self.user = user
        self.eventType = eventType
        self.eventValues = eventValues
        self.valveStateBefore = valveStateBefore
        self.valveStateAfter = valveStateAfter
        self.pumpStateBefore = pumpStateBefore
        self.pumpStateAfter = pumpStateAfter


def doesLog(userEvent):
    def decorator(function):
        def wrapper(*args, **kwargs):
            print(userEvent)
            result = function(*args, **kwargs)
            return result
        return wrapper
    return decorator


def writeSensorHeader(sensors):
    values = {}
    for sensor in sensorList:
        if type(sensors[sensor]) == dict:
            for attribute in sensors[sensor]:
                values[f'{sensor} ({attribute})'] = sensors[sensor][attribute]
        else:
            values[f'{sensor}'] = sensors[sensor]

    for value in values:
        currentRow[value] = values[value]

    return currentRow


def getHeaderFromSensors(sensorList, sensorAttributes=None, withBase=True):
    header = []
    if sensorAttributes != None:
        for sensor in sensorList:
            header += [f'{sensor} ({attribute})' for attribute in sensorAttributes]
    else:
        header = sensorList
    if withBase:
        return BASEHEADERATTRIBUTES + header
    else:
        return header


def init(defaultHeader=None, sensorList=None, sensorAttributes=None):
    if defaultHeader == None:
        defaultHeader = BASEHEADERATTRIBUTES

    if sensorList != None:
        defaultHeader += getHeaderFromSensors(
            sensorList=sensorList, sensorAttributes=sensorAttributes, withBase=False)

    logger.header = [*set(defaultHeader)]


def addSensorHeader(sensorList, sensorAttributes=None):
    defaultHeader = logger.header
    logger.header = [*set(defaultHeader + getHeaderFromSensors(
        sensorList=sensorList, sensorAttributes=sensorAttributes))]


def createLog(logName):
    logger.newLog(logName=logName)


def startLog(logName):
    logger.newLog(logName=logName)
    logger.activeLog = logName


def resumeLog(logName=None):
    if logName == None:
        logName = LogSystem.getLatest()
    logger.activeLog = logName


def insertRow(**kwargs):
    eventHeader = ""
    for event in loggerEvents:
        eventHeader += event + ', '
    if kwargs:
        kwargs["Events"] = eventHeader.rstrip(', ')
        logger.insertRow(**kwargs)
    else:
        values = dict({"Events": eventHeader.rstrip(', ')}, **currentRow)
        logger.insertRow((values))


def setLogEvent(event):
    loggerEvents.append(event)

from Utils.LogSystem import LogSystem


BASEHEADERATTRIBUTES = ["Timestamp", "Datetime", "State Change",
                        "Valve State", "Turbo Speed (PM1)", "Turbo Speed (PM2)", "Events"]

logger = LogSystem('C:/LOGS')


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
    logger.insertRow(**kwargs)

from fs.osfs import OSFS
from fs.path import join
import csv
import time


class LogSystem:

    """
    Class to handle log creation, writing, and general management
    """

    def __init__(self, path='.', header=None):
        """
        Initialize the log system. 

        path: the path to the log filesystem
        header: the default column names for new logs


        """

        self.path = path
        self.header = header
        self.fileSystem = OSFS(path, create=True)
        self.pwdPath = '/'
        self.oldPwd = '/'
        self.activeLog = None

    def newLog(self, logName, header=None):
        """

        Create a new log with the specified log name.

        logName: The name of the log to create. The name can be a single file name, or a path to a file.
                    If the log name includes a path, any necessary directories will be created.
                    If the log name is just a file name, the file will be created in the current working directory

        """

        if header == None:
            if self.header == None:
                raise Exception(
                    "LogSystem cannot create a new log without a header")
            header = self.header

        logName = self.gotoFile(self.forceCSV(logName))
        with self.fileSystem.open(join(self.pwdPath, logName), 'w') as log:
            if header != None:
                writer = csv.writer(log)
                writer.writerow(header)
        self.revertPwd()

    def setPwd(self, newPwd):
        """

        Set the pwd of the log file manager.

        newPwd: The new pwd that will be set. Any necessary directories will be created

        Sets oldPwd to the current pwd (before it is changed)

        """
        self.oldPwd = self.pwdPath
        if newPwd[0] == '/':
            self.pwdPath = newPwd
        else:
            self.pwdPath = join(self.pwdPath, newPwd)
        if not self.fileSystem.isdir(self.pwdPath):
            self.fileSystem.makedirs(self.pwdPath)

    def revertPwd(self):
        """

        reverts the log file manager's pwd to whatever it was before the most recent setPwd call

        """
        self.setPwd(self.oldPwd)

    def gotoFile(self, fileName):
        """

        Changes the log file manager's pwd to the path of the given file name

        fileName: The file to move to. If fileName does not include a path, nothing happend. If fileName includes a path, the log file manager's pwd is set to that path.

        returns: The name of the file without its path.

        """

        if '/' in fileName:
            nameSplit = fileName.split('/')
            dirs = "/".join(nameSplit[:-1])
            self.setPwd(dirs if dirs else '/')
            return nameSplit[-1]
        return fileName

    def getLog(self, logName):
        """

        get a log file by name

        logName: The name of the log file to retrieve

        returns: a python file-like object

        """

        logName = self.gotoFile(logName)

        return self.fileSystem.open(join(self.pwdPath, logName))

    def insertRow(self, logName=None, **kwargs):

        if logName == None and self.activeLog == None:
            raise Exception(
                "LogSystem cannot insert Row without having a log specified")

        logName = self.gotoFile(self.forceCSV(
            logName if logName != None else self.activeLog))

        with self.fileSystem.open(join(self.pwdPath, logName), 'r+') as log:
            header = next(csv.reader(log))
            row = {}
            for arg in kwargs:
                if arg in header:
                    row[arg] = kwargs[arg]
            csv.DictWriter(log, header).writerow(row)

    def getLatest(self):
        latest = 0
        latestpath = None
        for path in self.fileSystem.walk.files():
            modified = self.fileSystem.getmodified(path).timestamp()
            if modified > latest:
                latest = modified
                latestPath = path
        return latestPath

    def setLatestActive(self):
        self.activeLog = self.getLatest()

    def forceCSV(self, logName):
        if logName[-4:] != '.csv':
            logName += '.csv'
        return logName

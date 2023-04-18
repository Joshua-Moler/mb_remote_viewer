import json
import io
import os
from enum import Enum


class Permission(Enum):
    PERMISSION_NONE = 0
    PERMISSION_BASIC = 1
    PERMISSION_ELEVATED = 2
    PERMISSION_ADMIN = 3


permissionMap = {
    "none": Permission.PERMISSION_NONE,
    Permission.PERMISSION_NONE: Permission.PERMISSION_NONE,
    "basic": Permission.PERMISSION_BASIC,
    Permission.PERMISSION_BASIC: Permission.PERMISSION_BASIC,
    "elevated": Permission.PERMISSION_ELEVATED,
    "admin": Permission.PERMISSION_ADMIN,
    Permission.PERMISSION_ELEVATED: Permission.PERMISSION_ELEVATED,
}


class Setting:
    def __init__(self, id, permissions, value):
        permissions = permissionMap.get(permissions, Permission.PERMISSION_NONE)
        self.id = id
        self.permissions = permissions
        self.value = value
        self.type = type(value)


class SettingsCategory:
    def __init__(self, id):
        self.id = id
        self.settings = {}

    def addSetting(self, id, setting):
        if type(setting) == dict:
            self.settings[id] = Setting(
                id=id,
                permissions=setting.get("permissions"),
                value=setting.get("value"),
            )
        else:
            self.settings[id] = setting

    def setSetting(self, id, value, userPermission, save=True):
        pass


class Settings:
    def __init__(self, settingsLocation):
        self.settingsDict = {}
        self.settingsLocation = settingsLocation
        with open(settingsLocation) as settingsJson:
            for category in json.load(settingsJson):
                self.settingsDict[category] = SettingsCategory(category)
                for setting in category:
                    self.settingsDict[category].addSetting(
                        Setting(
                            id=setting,
                            permissions=category[setting].get("permissions"),
                            value=category[setting].get("value"),
                        )
                    )

    def save(self):
        with open(self.settingsLocation, "w") as settingsJson:
            settingsJson.seek(0)

            serialized = json.dumps(self.settingsDict)

            try:
                settingsJson.write(serialized)
            except Exception as e:
                print(e)

            settingsJson.flush()
            os.fsync(settingsJson.fileno())

            settingsJson.truncate()

    def setSetting(self, category, id, value, userPermission, save=True):
        userPermission = permissionMap.get(userPermission, Permission.PERMISSION_NONE)
        if (
            id in self.settingsDict[category].settings
            and userPermission.value >= self.settings[id].permissions.value
        ):
            if type(value) == self.settings[id].type:
                self.settingsDict[id].value = value
            else:
                raise Exception(f"Wrong type while setting {id}")

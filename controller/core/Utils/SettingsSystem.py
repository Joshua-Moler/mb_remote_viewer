import json
import io
import os
from enum import Enum


class Permission(Enum):
    IBP_NONE = 0
    IBP_BASIC = 1
    IBP_ELEVATED = 2
    IBP_ADMIN = 3


class SettingsPermissionException(Exception):
    def __init__(self, id, userPermission):
        super().__init__(
            f"User with permissions {userPermission.name} does not have permission to change setting {id}."
        )


class SettingsUnknownException(Exception):
    def __init__(self, id):
        super().__init__(f"Setting {id} is not a recognized system setting.")


class SettingsTypeException:
    def __init__(self, id, type):
        super().__init__(f"Cannot set setting {id} to a value with type {type}")


permissionMap = {
    "IBP_NONE": Permission.IBP_NONE,
    Permission.IBP_NONE: Permission.IBP_NONE,
    "IBP_BASIC": Permission.IBP_BASIC,
    Permission.IBP_BASIC: Permission.IBP_BASIC,
    "IBP_ELEVATED": Permission.IBP_ELEVATED,
    "IBP_ADMIN": Permission.IBP_ADMIN,
    Permission.IBP_ELEVATED: Permission.IBP_ELEVATED,
}


class Setting:
    def __init__(self, id, permissions, value):
        permissions = permissionMap.get(permissions, Permission.IBP_NONE)
        self.id = id
        self.permissions = permissions
        self.value = value
        self.type = type(value)


class SettingsCategory:
    def __init__(self, id):
        self.id = id
        self.settings = {}

    def addSetting(self, id, userPermission, value):
        self.settings[id] = Setting(id=id, permissions=userPermission, value=value)

        return True

    def setSetting(self, id, value, userPermission: Permission):
        if id not in self.settings:
            raise SettingsUnknownException(id)
        if userPermission.value < self.settings[id].permissions.value:
            raise SettingsPermissionException(id, userPermission)
        if type(value) != self.settings[id].type:
            raise SettingsTypeException(id, type(value))
        self.settings[id].value = value
        return True

    def get(self, id):
        return self.settings.get(id)


class SettingsSystem:
    def __init__(self, settingsLocation):
        self.settingsCategories = {}
        self.settingsLocation = settingsLocation
        with open(settingsLocation) as settingsJson:
            for category, settings in json.load(settingsJson).items():
                self.settingsCategories[category] = SettingsCategory(category)
                for setting in settings:
                    self.settingsCategories[category].addSetting(
                        id=setting,
                        userPermission=settings[setting].get("permissions"),
                        value=settings[setting].get("value"),
                    )

    def asDict(self):
        return {
            category: {
                setting: {"value": values.value, "permissions": values.permissions.name}
                for setting, values in settings.settings.items()
            }
            for category, settings in self.settingsCategories.items()
        }

    def save(self):
        with open(self.settingsLocation, "w") as settingsJson:
            settingsJson.seek(0)

            serialized = json.dumps(self.asDict())

            try:
                settingsJson.write(serialized)
            except Exception as e:
                print(e)

            settingsJson.flush()
            os.fsync(settingsJson.fileno())

            settingsJson.truncate()

    def setSetting(self, category, id, value, userPermission, save=True):
        userPermission = permissionMap.get(userPermission, Permission.IBP_NONE)
        if category in self.settingsCategories:
            if not self.settingsCategories[category].setSetting(
                id=id, value=value, userPermission=userPermission
            ):
                raise Exception(
                    f"Failed to set setting {category}:{id} to value {value} with user permission {userPermission}"
                )

            if save:
                self.save()
            return True

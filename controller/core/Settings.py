from core.Utils.SettingsSystem import SettingsSystem, SettingsPermissionException

settings = SettingsSystem("./settings.json")


def getSettingsDict():
    return settings.asDict()


def setSetting(category, id, newValue, userPermission):
    try:
        result = settings.setSetting(
            category=category, id=id, value=newValue, userPermission=userPermission
        )
        return result, newValue
    except SettingsPermissionException:
        return False, "Access Denied"

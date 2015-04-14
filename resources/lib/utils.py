import xbmc
import xbmcgui
import xbmcaddon
import sys
import subprocess

__addon_id__ = 'script.couch_ripper'
__Addon = xbmcaddon.Addon(__addon_id__)


def data_dir():
    return __Addon.getAddonInfo('profile')


def addon_dir():
    return __Addon.getAddonInfo('path')


def openSettings():
    __Addon.openSettings()


def log(message, loglevel=xbmc.LOGNOTICE):
    xbmc.log(encode('{couchripper}-{version} : {message}'.format(
            couchripper = __addon_id__,
            version = __Addon.getAddonInfo('version'),
            message= message)),
            level=loglevel)

def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    Backported from Python 2.7 as it's implemented as pure python on stdlib.

    >>> check_output(['/usr/bin/python', '--version'])
    Python 2.6.2
	from https://gist.github.com/edufelipe/1027906
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output


def logDebug(message, loglevel=xbmc.LOGDEBUG):
    xbmc.log(encode('{couchripper}-{version} : {message}'.format(
            couchripper = __addon_id__,
            version = __Addon.getAddonInfo('version'),
            message= message)),
            level=loglevel)


def showNotification(message):
    # 30010 == Couch Ripper
    xbmcgui.Dialog().notification(
            encode(getString(30010)),
            encode(message),
            time=4000,
            icon=xbmc.translatePath('{addonpath}/icon.png'.format(
            addonpath = __Addon.getAddonInfo('path'))))


def showOK(message):
    return xbmcgui.Dialog().ok(
            encode(__Addon.getAddonInfo('name')),
            encode(message))


def showSelectDialog(heading, selections):
    return xbmcgui.Dialog().select(encode(heading), selections)


def settingsError(message):
    log('{message} {pleasecheckyoursettings}'.format(
        message = message,
        pleasecheckyoursettings = getString(30053)),
        xbmc.LOGERROR)
    return message


def getSetting(name):
    return __Addon.getSetting(name)


def getSettingLow(name):
    return __Addon.getSetting(name).lower()


def setSetting(name, value):
    __Addon.setSetting(name, value)


def getString(string_id):
    return __Addon.getLocalizedString(string_id)


def getStringLow(string_id):
    return __Addon.getLocalizedString(string_id).lower()


def exitFailed(message, error):
    log(encode(message), loglevel=xbmc.LOGERROR)
    log(encode(error), loglevel=xbmc.LOGERROR)
    # 30010 == Couch Ripper
    xbmcgui.Dialog().notification(
        encode(getString(30010)),
        encode(message),
        time=4000,
        icon=xbmcgui.NOTIFICATION_ERROR)
    sys.exit(1)


def encode(string):
    result = ''

    try:
        result = string.encode('UTF-8', 'replace')
    except UnicodeDecodeError:
        result = 'Unicode Error'

    return result

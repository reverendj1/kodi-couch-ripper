import urlparse
import xbmc
import os
import sys
import glob
import resources.lib.utils as utils
import platform
import subprocess
import re


def main(argv):

    params = getParams(argv)

    defaultsettings = getDefaults()

    if 'profile' in params:
        profilenum = params['profile']
    else:
        profilenum = ''

    profiledict = getProfile(defaultsettings, profilenum)

    verifyProfile(profiledict)

    # Let's see if we just want to show the commands in a Kodi
    # notification. This is useful if you want to verify settings or
    # cron them up manually.
    if 'getcommand' in params:
        if params['getcommand'] == 'makemkvcon':
            utils.showOK(buildMakeMKVConCommand(profiledict))
            return 0
        elif params['getcommand'] == 'handbrakecli':
            utils.showOK(buildHandBrakeCLICommand(
                    profiledict, profiledict['tempfolder']))
            return 0

    utils.logDebug(profiledict)
    command = buildMakeMKVConCommand(profiledict)

    # TODO (??) user might want to specify a disc name in case the disc name
    # is shortened or changed in a way that metadata libraries don't understand 
    # what movie this is. many times though, the below will give you what you want
    discName = getDiscName(profiledict)

    # Beginning Rip. Command:
    utils.log('{beginning} {rip}. {commandstr}: {command}'.format(
            beginning = utils.getString(30070),
            rip = utils.getString(30027),
            commandstr = utils.getString(30071),
            command = command))
    try:
        if sys.version_info[:2] == (2,7):
            ripoutput = subprocess.check_output(
                    command, stderr=subprocess.STDOUT, shell=True)
        elif sys.version_info[:2] == (2,6):
            ripoutput = utils.check_output(
                    command, stderr=subprocess.STDOUT, shell=True)
    # For some reason, it seems that this always exits with a non-zero
    # status, so I'm just checking the output for success.
    except subprocess.CalledProcessError, e:
        if 'Copy complete.' in e.output:
            # We'll check for an error which denote using FAT32 for the temp
            # filesystem.
            fatcheck = re.search( r"The size of output file '(.*)' may reach "
                    "as much as (.*) while target filesystem has a file size "
                    "limit of (.*)", output)
            if fatcheck:
                # 30083 = Temp folder cannot handle large files
                # 30084 = This is usually caused by using FAT32 for storage.
                utils.exitFailed(utils.getstring(30083),
                        utils.getString(30083) + ' ' + utils.getString(30084))
            if ('The source file' in e.output and
                    ' is corrupt or invalid at offset' in e.output and
                    ', attempting to work around' in e.output):
                # 30087 = MakeMKV Had Trouble Reading the Disc. Try Cleaning it
                # if the Correct Title Wasn't Ripped.
                utils.log(utils.getString(30087))
        else:
            if 'Your temporary key has expired and was removed' in e.output:
                # 30074 = Your temporary MakeMKV key has expired. Please update
                # it
                utils.exitFailed(utils.getString(30074),
                        utils.getString(30074))
            if 'This application version is too old' in e.output:
                # 30075 = Your version of MakeMKV is too old. Please update it.
                utils.exitFailed(utils.getString(30075),
                        utils.getString(30075))
            if 'Failed to open disc' in e.output:
                # 30085 = Failed to Open Disc
                utils.exitFailed(utils.getString(30085),
                        utils.getString(30085))
            if ('The source file' in e.output and
                    ' is corrupt or invalid at offset' in e.output and
                    ', attempting to work around' in e.output):
                # 30086 = MakeMKV Had Trouble Reading the Disc. Try Cleaning it
                utils.exitFailed(utils.getString(30086),
                        utils.getString(30086))
            utils.exitFailed('MakeMKV {failed}'.format(
                    failed = utils.getString(30059)), e.output)
    utils.logDebug(ripoutput)

    # Eject if we need to
    # 30027 == Rip
    if profiledict['ejectafter'] == utils.getStringLow(30027):
        xbmc.executebuiltin('EjectTray()')

    # Display notification/dialog if we need to. A notification is a
    # toast that auto-dismisses after a few seconds, whereas a dialog
    # requires the user to press ok.
    # 30065 == Notification
    if profiledict['notifyafterrip'] == utils.getStringLow(30065):
        utils.showNotification('{rip} {completedsuccessfully}'.format(
                rip = utils.getString(30027),
                completedsuccessfully = utils.getString(30058)))
    # 30066 == Dialog
    elif profiledict['notifyafterrip'] == utils.getStringLow(30066):
        utils.showOK('{rip} {completedsuccessfully}'.format(
                rip = utils.getString(30027),
                completedsuccessfully = utils.getString(30058)))

    # Some people may want to just rip movies, and not encode them.
    # If that's the case, we are done here.
    if profiledict['encodeafterrip'] == 'false':
        return 0

    filestoencode = glob.glob(os.path.join(profiledict['tempfolder'], '*.mkv'))
    for f in filestoencode:
        # makemkvcon doesn't allow to customize the output filename
        # but handbrake does, so pass it in to customize output filename option
        command = buildHandBrakeCLICommand(profiledict, f, discName)
        utils.log('{beginning} {encode}. {commandstr}: {command}'.format(
                beginning = utils.getString(30070),
                encode = utils.getString(30028),
                commandstr = utils.getString(30071),
                command = command))
        try:
            if sys.version_info[:2] == (2,7):
                encodeoutput = subprocess.check_output(
                        command, stderr=subprocess.STDOUT, shell=True)
            elif sys.version_info[:2] == (2,6):
                encodeoutput = utils.check_output(
                        command, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError, e:
            if 'Encode done!' not in e.output:
                utils.exitFailed('HandBrake {failed}'.format(
                        failed = utils.getString(30059)), e.output)
        utils.logDebug(encodeoutput)
        if profiledict['cleanuptempdir'] == 'true':
            os.remove(f)

    # 30028 == Encode
    if profiledict['ejectafter'] == utils.getStringLow(30028):
        xbmc.executebuiltin('EjectTray()')

    # 30065 == Notification
    if profiledict['notifyafterencode'] == utils.getStringLow(30065):
        utils.showNotification('{encode} {completedsuccessfully}'.format(
                encode = utils.getString(30028),
                completedsuccessfully = utils.getString(30058)))
    elif profiledict['notifyafterencode'] == utils.getStringLow(30066):
        utils.showOK('{encode} {completedsuccessfully}'.format(
                encode = utils.getString(30028),
                completedsuccessfully = utils.getString(30058)))

    # if we have a name, the scan could pull in the metadata automatically for us
    if discName != None:
       xbmc.executebuiltin('UpdateLibrary("video")')

    return 0


def getDefaults():
    # Get all the profile's settings. I know there has to be a better
    # way to do profiles, but this should work.
    defaultsettings = {
        'defaultmakemkvpath': utils.getSetting('defaultmakemkvpath'),
        'defaulthandbrakeclipath': utils.getSetting('defaulthandbrakeclipath'),
        'defaulttempfolder': utils.getSetting('defaulttempfolder'),
        'defaultdestinationfolder':
        utils.getSetting('defaultdestinationfolder'),
        'defaultniceness': utils.getSettingLow('defaultniceness'),
        'defaultresolution': utils.getSetting('defaultresolution'),
        'defaultquality': utils.getSettingLow('defaultquality'),
        'defaultmintitlelength': utils.getSetting('defaultmintitlelength'),
        'defaultnativelanguage': utils.getSettingLow('defaultnativelanguage'),
        'defaultforeignaudio': utils.getSettingLow('defaultforeignaudio'),
        'defaultencodeafterrip': utils.getSettingLow('defaultencodeafterrip'),
        'defaultejectafter': utils.getSettingLow('defaultejectafter'),
        'defaultnotifyafterrip': utils.getSettingLow('defaultnotifyafterrip'),
        'defaultnotifyafterencode':
        utils.getSettingLow('defaultnotifyafterencode'),
        'defaultcleanuptempdir': utils.getSettingLow('defaultcleanuptempdir'),
        'defaultblackandwhite': utils.getSettingLow('defaultblackandwhite'),
        'defaultdriveid': utils.getSetting('defaultdriveid'),
        'defaultenablecustomripcommand':
        utils.getSetting('defaultenablecustomripcommand'),
        'defaultcustomripcommand': utils.getSetting('defaultcustomripcommand'),
        'defaultenablecustomencodecommand':
        utils.getSetting('defaultenablecustomencodecommand'),
        'defaultcustomencodecommand':
        utils.getSetting('defaultcustomencodecommand'),
        'defaultadditionalhandbrakeargs':
        utils.getSetting('defaultadditionalhandbrakeargs')}
    # Parse the 3 letter language code from selection
    languagesearch = re.search( r"(.*\()(.*)\)",
            defaultsettings['defaultnativelanguage'])
    if languagesearch:
        defaultsettings['defaultnativelanguage'] = languagesearch.group(2)
    return defaultsettings


def getProfile(defaultsettings, profilenum):
    if profilenum == '':
        validprofiles = []
        for profile in ['profile1', 'profile2', 'profile3', 'profile4',
                'profile5', 'profile6', 'profile7', 'profile8', 'profile9',
                'profile10']:
            if utils.getSetting(profile + 'enabled') == 'true':
                validprofiles.append(utils.getSetting(profile + 'prettyname'))
        if validprofiles == []:
            utils.exitFailed(utils.getString(30080), utils.getString(30080))
        profilenum = utils.showSelectDialog(
                '{couchripper} - {profilestr}'.format(
                couchripper = utils.getString(30010),
                profilestr = utils.getString(30051)),
                validprofiles)
        profilename = validprofiles[profilenum]
    else:
        profilename = utils.getSetting(profilenum + 'prettyname')
    if profilenum == -1:
        # 30081 == Rip Cancelled
        utils.exitFailed(utils.getString(30081), utils.getString(30081))
    profiledict = []
    for profile in ['profile1', 'profile2', 'profile3', 'profile4', 'profile5',
            'profile6', 'profile7', 'profile8', 'profile9', 'profile10']:
        if utils.getSetting(profile + 'prettyname') == profilename:
            profiledict = {
                    'makemkvpath':
                    utils.getSetting(profile + 'makemkvpath'),
                    'handbrakeclipath':
                    utils.getSetting(profile + 'handbrakeclipath'),
                    'tempfolder':
                    utils.getSetting(profile + 'tempfolder'),
                    'destinationfolder':
                    utils.getSetting(profile + 'destinationfolder'),
                    'niceness':
                    utils.getSettingLow(profile + 'niceness'),
                    'resolution':
                    utils.getSettingLow(profile + 'resolution'),
                    'quality':
                    utils.getSettingLow(profile + 'quality'),
                    'mintitlelength':
                    utils.getSettingLow(profile + 'mintitlelength'),
                    'nativelanguage':
                    utils.getSettingLow(profile + 'nativelanguage'),
                    'foreignaudio':
                    utils.getSettingLow(profile + 'foreignaudio'),
                    'encodeafterrip':
                    utils.getSettingLow(profile + 'encodeafterrip'),
                    'ejectafter':
                    utils.getSettingLow(profile + 'ejectafter'),
                    'notifyafterrip':
                    utils.getSettingLow(profile + 'notifyafterrip'),
                    'notifyafterencode':
                    utils.getSettingLow(profile + 'notifyafterencode'),
                    'cleanuptempdir':
                    utils.getSettingLow(profile + 'cleanuptempdir'),
                    'blackandwhite':
                    utils.getSettingLow(profile + 'blackandwhite'),
                    'driveid':
                    utils.getSetting(profile + 'driveid'),
                    'enablecustomripcommand':
                    utils.getSetting(profile + 'enablecustomripcommand'),
                    'customripcommand':
                    utils.getSetting(profile + 'customripcommand'),
                    'enablecustomencodecommand':
                    utils.getSetting(profile + 'enablecustomencodecommand'),
                    'customencodecommand':
                    utils.getSetting(profile + 'customencodecommand'),
                    'additionalhandbrakeargs':
                    utils.getSetting(profile + 'additionalhandbrakeargs')}
            # Parse the 3 letter language code from selection
            languagesearch = re.search( r"(.*\()(.*)\)",
                    profiledict['nativelanguage'])
            if languagesearch:
                profiledict['nativelanguage'] = languagesearch.group(2)
            for key, value in profiledict.iteritems():
                if (value == 'default' or value == ''):
                    profiledict[key] = defaultsettings['default' + key]
    return profiledict


def verifyProfile(profiledict):
    # Let's verify all of our settings.
    errors = ''
    # 30013 == High, 30015 == Low, 30019 == Normal
    if (profiledict['niceness'] != utils.getStringLow(30013) and
            profiledict['niceness'] != utils.getStringLow(30015) and
            profiledict['niceness'] != utils.getStringLow(30019)):
        errors = errors + utils.settingsError(
                '{invalid} {niceness}. '.format(
                invalid = utils.getString(30056),
                niceness = utils.getString(30018)))
    if (profiledict['encodeafterrip'] != 'true' and
            profiledict['encodeafterrip'] != 'false'):
        errors = errors + utils.settingsError(
                '{invalid} {encodeafterrip}. '.format(
                invalid = utils.getString(30056),
                encodeafterrip = utils.getString(30025)))
    # 30027 == Rip, 30028 == Encode, 30029 == Never
    if (profiledict['ejectafter'] != utils.getStringLow(30027) and
            profiledict['ejectafter'] != utils.getStringLow(30028) and
            profiledict['ejectafter'] != utils.getStringLow(30029)):
        errors = errors + utils.settingsError(
                '{invalid} {ejectafter}. '.format(
                invalid = utils.getString(30056),
                ejectafter = utils.getString(30026)))
    # 30065 == Notification,
    if (profiledict['notifyafterrip'] != utils.getStringLow(30065) and
            profiledict['notifyafterrip'] != utils.getStringLow(30066) and
            profiledict['notifyafterrip'] != utils.getStringLow(30067)):
        errors = errors + utils.settingsError(
                '{invalid} {notifyafterrip}. '.format(
                invalid = utils.getString(30056),
                notifyafterrip = utils.getString(30049)))
    if (profiledict['notifyafterencode'] != utils.getStringLow(30065) and
            profiledict['notifyafterencode'] != utils.getStringLow(30066) and
            profiledict['notifyafterencode'] != utils.getStringLow(30067)):
        errors = errors + utils.settingsError(
                '{invalid} {notifyafterencode}. '.format(
                invalid = utils.getString(30056),
                notifyafterencode = utils.getString(30061)))
    if (profiledict['enablecustomripcommand'] != 'true' and
            profiledict['enablecustomripcommand'] != 'false'):
        errors = errors + utils.settingsError(
                '{invalid} {enablecustomripcommand}. '.format(
                invalid = utils.getString(30056),
                enablecustomripcommand = utils.getString(30078)))
    if (profiledict['enablecustomencodecommand'] != 'true' and
            profiledict['enablecustomencodecommand'] != 'false'):
        errors = errors + utils.settingsError(
                '{invalid} {enablecustomencodecommand}. '.format(
                invalid = utils.getString(30056),
                enablecustomencodecommand = utils.getString(30079)))

    if (profiledict['enablecustomripcommand'] == 'false' and
            profiledict['enablecustomencodecommand'] == 'false'):
        if os.path.isdir(profiledict['tempfolder']):
            if not os.access(profiledict['tempfolder'], os.W_OK):
                errors = errors + utils.settingsError(
                    '{couldnotwriteto} {tempfolder}. '.format(
                    couldnotwriteto = utils.getString(30082),
                    tempfolder = profiledict['tempfolder']))
        else:
            errors = errors + utils.settingsError(
                '{couldnotfind} {tempfolder}. '.format(
                couldnotfind = utils.getString(30052),
                tempfolder = profiledict['tempfolder']))
    if profiledict['enablecustomripcommand'] == 'false':
        if not os.path.isfile(profiledict['makemkvpath']):
            errors = errors + utils.settingsError(
                    '{couldnotfind} makemkvcon. '.format(
                    couldnotfind = utils.getString(30052)))
        if not profiledict['mintitlelength'].isdigit():
            errors = errors + utils.settingsError(
                    '{invalid} {mintitlelength}. '.format(
                    invalid = utils.getString(30056),
                    mintitlelength = utils.getString(30022)))
        if not profiledict['driveid'].isdigit():
            errors = errors + utils.settingsError(
                    '{invalid} {driveid}. '.format(
                    invalid = utils.getString(30056),
                    driveid = utils.getString(30068)))
    else:
        if profiledict['customripcommand'] == '':
            errors = errors + utils.settingsError(
                    '{invalid} {customripcommand}. '.format(
                    invalid = utils.getString(30056),
                    customripcommand = utils.getString(30076)))
    if (profiledict['enablecustomencodecommand'] == 'true' and
            profiledict['customencodecommand'] == ''):
        errors = errors + utils.settingsError(
                '{invalid} {customencodecommand}. '.format(
                invalid = utils.getString(30056),
                customencodecommand = utils.getString(30077)))
    if (profiledict['enablecustomencodecommand'] == 'false' and
            profiledict['encodeafterrip'] == 'true'):
        if not os.path.isfile(profiledict['handbrakeclipath']):
            errors = errors + utils.settingsError(
                    '{couldnotfind} HandBrakeCLI. '.format(
                    couldnotfind = utils.getString(30052)))
        if os.path.isdir(profiledict['destinationfolder']):
            if not os.access(profiledict['destinationfolder'], os.W_OK):
                errors = errors + utils.settingsError(
                    '{couldnotwriteto} {destinationfolder}. '.format(
                    couldnotwriteto = utils.getString(30082),
                    destinationfolder = profiledict['destinationfolder']))
        else:
            errors = errors + utils.settingsError(
                    '{couldnotfind} {destinationfolder}. '.format(
                    couldnotfind = utils.getString(30052),
                    destinationfolder = profiledict['destinationfolder']))
        # 30042 == 1080, 30043 == 720, 30044 == 480
        if (profiledict['resolution'] != utils.getStringLow(30042) and
                profiledict['resolution'] != utils.getStringLow(30043) and
                profiledict['resolution'] != utils.getStringLow(30044)):
            errors = errors + utils.settingsError(
                    '{invalid} {resolution}. '.format(
                    invalid = utils.getString(30056),
                    resolution = utils.getString(30011)))
        # 30013 == High, 30015 == Low, 30014 == Medium
        if (profiledict['quality'] != utils.getStringLow(30013) and
                profiledict['quality'] != utils.getStringLow(30014) and
                profiledict['quality'] != utils.getStringLow(30015)):
            errors = errors + utils.settingsError(
                    '{invalid} {quality}. '.format(
                    invalid = utils.getString(30056),
                    quality = utils.getString(30012)))
        # List of valid ISO-639.2 language names.
        # From http://www.loc.gov/standards/iso639-2/ISO-639-2_8859-1.txt This
        # is the format that HandBrake requires language arguments to be in.
        validlanguages = [
                'all', 'aar', 'abk', 'ace', 'ach', 'ada', 'ady', 'afa', 'afh',
                'afr', 'ain', 'aka', 'akk', 'alb', 'ale', 'alg', 'alt', 'amh',
                'ang', 'anp', 'apa', 'ara', 'arc', 'arg', 'arm', 'arn', 'arp',
                'art', 'arw', 'asm', 'ast', 'ath', 'aus', 'ava', 'ave', 'awa',
                'aym', 'aze', 'bad', 'bai', 'bak', 'bal', 'bam', 'ban', 'baq',
                'bas', 'bat', 'bej', 'bel', 'bem', 'ben', 'ber', 'bho', 'bih',
                'bik', 'bin', 'bis', 'bla', 'bnt', 'bos', 'bra', 'bre', 'btk',
                'bua', 'bug', 'bul', 'bur', 'byn', 'cad', 'cai', 'car', 'cat',
                'cau', 'ceb', 'cel', 'cha', 'chb', 'che', 'chg', 'chi', 'chk',
                'chm', 'chn', 'cho', 'chp', 'chr', 'chu', 'chv', 'chy', 'cmc',
                'cop', 'cor', 'cos', 'cpe', 'cpf', 'cpp', 'cre', 'crh', 'crp',
                'csb', 'cus', 'cze', 'dak', 'dan', 'dar', 'day', 'del', 'den',
                'dgr', 'din', 'div', 'doi', 'dra', 'dsb', 'dua', 'dum', 'dut',
                'dyu', 'dzo', 'efi', 'egy', 'eka', 'elx', 'eng', 'enm', 'epo',
                'est', 'ewe', 'ewo', 'fan', 'fao', 'fat', 'fij', 'fil', 'fin',
                'fiu', 'fon', 'fre', 'frm', 'fro', 'frr', 'frs', 'fry', 'ful',
                'fur', 'gaa', 'gay', 'gba', 'gem', 'geo', 'ger', 'gez', 'gil',
                'gla', 'gle', 'glg', 'glv', 'gmh', 'goh', 'gon', 'gor', 'got',
                'grb', 'grc', 'gre', 'grn', 'gsw', 'guj', 'gwi', 'hai', 'hat',
                'hau', 'haw', 'heb', 'her', 'hil', 'him', 'hin', 'hit', 'hmn',
                'hmo', 'hrv', 'hsb', 'hun', 'hup', 'iba', 'ibo', 'ice', 'ido',
                'iii', 'ijo', 'iku', 'ile', 'ilo', 'ina', 'inc', 'ind', 'ine',
                'inh', 'ipk', 'ira', 'iro', 'ita', 'jav', 'jbo', 'jpn', 'jpr',
                'jrb', 'kaa', 'kab', 'kac', 'kal', 'kam', 'kan', 'kar', 'kas',
                'kau', 'kaw', 'kaz', 'kbd', 'kha', 'khi', 'khm', 'kho', 'kik',
                'kin', 'kir', 'kmb', 'kok', 'kom', 'kon', 'kor', 'kos', 'kpe',
                'krc', 'krl', 'kro', 'kru', 'kua', 'kum', 'kur', 'kut', 'lad',
                'lah', 'lam', 'lao', 'lat', 'lav', 'lez', 'lim', 'lin', 'lit',
                'lol', 'loz', 'ltz', 'lua', 'lub', 'lug', 'lui', 'lun', 'luo',
                'lus', 'mac', 'mad', 'mag', 'mah', 'mai', 'mak', 'mal', 'man',
                'mao', 'map', 'mar', 'mas', 'may', 'mdf', 'mdr', 'men', 'mga',
                'mic', 'min', 'mis', 'mkh', 'mlg', 'mlt', 'mnc', 'mni', 'mno',
                'moh', 'mon', 'mos', 'mul', 'mun', 'mus', 'mwl', 'mwr', 'myn',
                'myv', 'nah', 'nai', 'nap', 'nau', 'nav', 'nbl', 'nde', 'ndo',
                'nds', 'nep', 'new', 'nia', 'nic', 'niu', 'nno', 'nob', 'nog',
                'non', 'nor', 'nqo', 'nso', 'nub', 'nwc', 'nya', 'nym', 'nyn',
                'nyo', 'nzi', 'oci', 'oji', 'ori', 'orm', 'osa', 'oss', 'ota',
                'oto', 'paa', 'pag', 'pal', 'pam', 'pan', 'pap', 'pau', 'peo',
                'per', 'phi', 'phn', 'pli', 'pol', 'pon', 'por', 'pra', 'pro',
                'pus', 'qaa-qtz', 'que', 'raj', 'rap', 'rar', 'roa', 'roh',
                'rom', 'rum', 'run', 'rup', 'rus', 'sad', 'sag', 'sah', 'sai',
                'sal', 'sam', 'san', 'sas', 'sat', 'scn', 'sco', 'sel', 'sem',
                'sga', 'sgn', 'shn', 'sid', 'sin', 'sio', 'sit', 'sla', 'slo',
                'slv', 'sma', 'sme', 'smi', 'smj', 'smn', 'smo', 'sms', 'sna',
                'snd', 'snk', 'sog', 'som', 'son', 'sot', 'spa', 'srd', 'srn',
                'srp', 'srr', 'ssa', 'ssw', 'suk', 'sun', 'sus', 'sux', 'swa',
                'swe', 'syc', 'syr', 'tah', 'tai', 'tam', 'tat', 'tel', 'tem',
                'ter', 'tet', 'tgk', 'tgl', 'tha', 'tib', 'tig', 'tir', 'tiv',
                'tkl', 'tlh', 'tli', 'tmh', 'tog', 'ton', 'tpi', 'tsi', 'tsn',
                'tso', 'tuk', 'tum', 'tup', 'tur', 'tut', 'tvl', 'twi', 'tyv',
                'udm', 'uga', 'uig', 'ukr', 'umb', 'und', 'urd', 'uzb', 'vai',
                'ven', 'vie', 'vol', 'vot', 'wak', 'wal', 'war', 'was', 'wel',
                'wen', 'wln', 'wol', 'xal', 'xho', 'yao', 'yap', 'yid', 'yor',
                'ypk', 'zap', 'zbl', 'zen', 'zgh', 'zha', 'znd', 'zul', 'zun',
                'zxx', 'zza']

        if profiledict['nativelanguage'] not in validlanguages:
            errors = errors + utils.settingsError(
                    '{invalid} {nativelanguage}. '.format(
                    invalid = utils.getString(30056),
                    nativelanguage = utils.getString(30023)))
        if (profiledict['foreignaudio'] != 'true' and
                profiledict['foreignaudio'] != 'false'):
            errors = errors + utils.settingsError(
                    '{invalid} {foreignaudio}. '.format(
                    invalid = utils.getString(30056),
                    foreignaudio = utils.getString(30024)))
        if (profiledict['cleanuptempdir'] != 'true' and
                profiledict['cleanuptempdir'] != 'false'):
            errors = errors + utils.settingsError(
                    '{invalid} {cleanuptempdir}. '.format(
                    invalid = utils.getString(30056),
                    cleanuptempdir = utils.getString(30030)))
        if (profiledict['blackandwhite'] != 'true' and
                profiledict['blackandwhite'] != 'false'):
            errors = errors + utils.settingsError(
                    '{invalid} {blackandwhite}. '.format(
                    invalid = utils.getString(30056),
                    blackandwhite = utils.getString(30060)))

    if errors:
        utils.exitFailed(errors, errors)


def buildMakeMKVConCommand(profiledict):
    niceness = ''
    # 30013 == High, 30015 == Low
    if (profiledict['niceness'] == utils.getString(30013).lower() or
            profiledict['niceness'] == utils.getString(30015).lower()):
        if (platform.system() == 'Windows'):
            if (profiledict['niceness'] == utils.getStringLow(30013)):
                # If you pass quoted text to the Windows "start" command
                # as the first argument, it treats this as the name of the
                # program you want to run, not the command you want to run,
                # so I just add an empty set of double-quotes to prevent
                # issues.
                niceness = 'start /wait /b /high "" '
            else:
                niceness = 'start /wait /b /low "" '
        else:
            if (profiledict['niceness'] == utils.getStringLow(30013)):
                niceness = 'nice -n -19 '
            else:
                niceness = 'nice -n 19 '
    if profiledict['enablecustomripcommand'] == 'true':
        command = '{niceness} {customripcommand}'.format(niceness = niceness,
                customripcommand = profiledict['customripcommand'])
    else:
        mintitlelength = str(int(profiledict['mintitlelength']) * 60)

        command = ('{niceness} "{makemkvpath}" mkv --decrypt disc:{driveid} '
                'all --minlength={mintitlelength} "{tempfolder}"'.format(
                niceness = niceness,
                makemkvpath = profiledict['makemkvpath'],
                driveid = profiledict['driveid'],
                mintitlelength = mintitlelength,
                # MakeMKV will add a forward slash at the end of a folder if it
                # has a backslash. This is bad for Windows, so we strip the
                # trailing slash.
                tempfolder = profiledict['tempfolder'].rstrip('\\')))
    return command


def buildHandBrakeCLICommand(profiledict, f, discName):
    niceness = ''
    # 30013 == High, 30015 == Low, 30014 == Medium
    if (profiledict['niceness'] == utils.getString(30013).lower()
            or profiledict['niceness'] == utils.getString(30015).lower()):
        if (platform.system() == 'Windows'):
            if (profiledict['niceness'] == utils.getStringLow(30013)):
                # If you pass quoted text to the Windows "start" command
                # as the first argument, it treats this as the name of the
                # program you want to run, not the command you want to run,
                # so I just add an empty set of double-quotes to prevent
                # issues.
                niceness = 'start /wait /b /high "" '
            else:
                niceness = 'start /wait /b /low "" '
        else:
            if (profiledict['niceness'] == utils.getStringLow(30013)):
                niceness = 'nice -n -19 '
            else:
                niceness = 'nice -n 19 '
    if profiledict['enablecustomencodecommand'] == 'true':
        command = '{niceness} {customencodecommand}'.format(niceness = niceness,
                customencodecommand = profiledict['customencodecommand'])
    else:
        if profiledict['resolution'] == '1080':
            maxwidth = ' --maxWidth 1920'
        elif profiledict['resolution'] == '720':
            maxwidth = ' --maxWidth 1280'
        elif profiledict['resolution'] == '480':
            maxwidth = ' --maxWidth 720'

        if profiledict['quality'] == utils.getStringLow(30013):
            quality = ''
        elif profiledict['quality'] == utils.getStringLow(30014):
            quality = ' -q 25 '
        elif profiledict['quality'] == utils.getStringLow(30015):
            quality = ' -q 26 '

        if profiledict['blackandwhite'] == 'true':
            blackandwhite = ' --grayscale '
        else:
            blackandwhite = ''

        additionalhandbrakeargs = ' {additionalhandbrakeargs}'.format(
                additionalhandbrakeargs =
                profiledict['additionalhandbrakeargs'])

        # To make things easier when we rip foreign films, we just grab all
        # the audio tracks. Otherwise it can be hard to grab just the
        # native language of the movie and the native language of the user.
        # Since grabbing all audio tracks doesn't appear to be an option
        # with HandBrake, I just grab the first ten tracks. When you list
        # audio tracks here that don't exist, it doesn't seem to error out
        # or anything.
        if profiledict['foreignaudio'] == 'true':
            audiotracks = ' -a 1,2,3,4,5,6,7,8,9,10 '
        else:
            audiotracks = ''
	
	if discName != None:
	    if os.path.basename(f) in ['title00.mkv', 'title0.mkv', 'title.mkv']:
	        destination = os.path.join(profiledict['destinationfolder'], os.path.basename(discName).replace('_', ' '))
            else:
	        destination = os.path.join(profiledict['destinationfolder'], os.path.basename(discName + '-' + f).replace('_', ' '))
        else:
            destination  = os.path.join(profiledict['destinationfolder'], os.path.basename(f).replace('_', ' '))

        command = ('{niceness}"{handbrakeclipath}" -i "{filename}" -o '
                '"{destination}" -f mkv -d slower -N {nativelanguage} '
                '--native-dub -m -Z "High Profile" -s 1{audiotracks}{quality}'
                '{blackandwhite}{maxwidth}{additionalhandbrakeargs}'.format(
                niceness = niceness,
                handbrakeclipath = profiledict['handbrakeclipath'],
                filename = f,
                destination = destination,
                nativelanguage = profiledict['nativelanguage'],
                audiotracks = audiotracks,
                quality = quality,
                blackandwhite = blackandwhite,
                maxwidth = maxwidth,
                additionalhandbrakeargs = additionalhandbrakeargs))

    return command

def getDiscName(profiledict):
    makemkvpath = profiledict['makemkvpath']
    drive_id = int(profiledict['driveid'])
    command = '"{makemkvpath}" info list -r'.format(makemkvpath=makemkvpath)
    try:
        if sys.version_info[:2] == (2,7):
            output = subprocess.check_output(
                    command, stderr=subprocess.STDOUT, shell=True)
        elif sys.version_info[:2] == (2,6):
            output = utils.check_output(
                    command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError, e:
        output = e.output
    gooddrives = ''
    # Iterate through the output, it should look like this:
    #MSG:1005,0,1,"MakeMKV v1.9.0 linux(x64-release) started","%1 started","MakeMKV v1.9.0 linux(x64-release)"
    #DRV:0,2,999,0,"BD-RE HL-DT-ST BD-RE  WH14NS40 1.03","SquirrelWresting","/dev/sr0"
    #DRV:1,256,999,0,"","",""
    #DRV:2,256,999,0,"","",""

    lines = iter(output.splitlines())
    for line in lines:
        drive = line.split(',')
        if len(drive) >= 7:
            if drive[5] != '""' and int(drive[0].split(':')[1]) == drive_id:
                return drive[5].replace('"', '')

    return None

def getParams(argv):
    param = {}
    if(len(argv) > 1):
        for i in argv:
            args = i
            if(args.startswith('?')):
                args = args[1:]
            param.update(dict(urlparse.parse_qsl(args)))

    return param

if __name__ == '__main__':
    sys.exit(main(sys.argv))

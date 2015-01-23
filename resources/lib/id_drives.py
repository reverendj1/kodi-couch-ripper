import utils as utils
import subprocess
import urlparse
import sys


def main(argv):

    params = getParams(argv)

    if 'profile' in params:
        profilenum = params['profile']

    makemkvpath = utils.getSetting(profilenum + 'makemkvpath')
    if not makemkvpath:
        makemkvpath = utils.getSetting('defaultmakemkvpath')
    if not makemkvpath:
        # Please Set MakeMKVCon Path
        utils.exitFailed('{pleaseset} {pathtomakemkvcon}'.format(
                pleaseset = utils.getString(30072),
                pathtomakemkvcon = utils.getString(30016)),
                '{pleaseset} {pathtomakemkvcon}'.format(
                pleaseset = utils.getString(30072),
                pathtomakemkvcon = utils.getString(30016)))
    command = makemkvpath + ' info list -r'
    try:
        output = subprocess.check_output(
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
            if drive[5] != '""':
                gooddrives = '{gooddrives} {drivenum}: {discname} '.format(
                        drivenum = drive[0].split(':')[1],
                        discname = drive[5].replace('"', ''))

    if gooddrives == '':
        # 30073 == Please Put a Disc in the Drive to Identify
        utils.exitFailed(utils.getString(30073), utils.getString(30073))
    else:
        utils.showOK(gooddrives)
    return 0


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

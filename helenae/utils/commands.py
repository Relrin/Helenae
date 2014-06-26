"""
    This module contains basics commands, which [user/file server] can using
"""
from math import log
from json import dumps
from hashlib import sha256

# available commands and handlers
commands_user = {"AUTH": "autorization with server",
                 "READ": "read some file from storage",
                 "WRTE": "write file into storage",
                 "DELT": "delete file from storage",
                 "RNME": "rename file",
                 "LIST": "get list of all files from storage with this user",
                 "SYNC": "synchronize files with storage on the server",
                 "EXIT": "disconnect from server or end session"}

commands_handlers_user   = dict((key, None) for key in commands_user.keys())
commands_handlers_server = dict((key, None) for key in commands_user.keys() if key not in ('AUTH', 'EXIT'))

unit_list = zip(['bytes', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb'], [0, 0, 1, 2, 2, 2])
def convertSize(num):
    """
        Converting file size in bytes to Kb/Mb /etc.
    """
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

def constructBasicJSON():
    """
        Create basic JSON for operations
    """
    data = {}
    data['cmd'] = None
    data['user'] = None
    data['password'] = None
    data['auth'] = None
    data['error'] = []
    return data


def constructDataClient(cmd, user, hash_password, auth, error='', **kwargs):
    """
        Create JSON for server from Client
    """
    data = constructBasicJSON()
    data['cmd'] = cmd
    data['user'] = user
    data['password'] = hash_password
    data['auth'] = auth
    if error:
        data['error'].append(error)
    for item in kwargs.iterkeys():
        data[item] = kwargs[item]
    return dumps(data)


def AUTH(result, data):
    error_msg = "[AUTH] User=%s successfully logged..." % data['user']
    # user not found at DB
    if result is None:
        data['cmd'] = 'RAUT'
        data['error'].append('\nWARNING: User not found')
        error_msg = "[AUTH] User=%s not found" % data['user']
    else:
        if result['name'] == data['user']:
            # correct users info --> real user
            hash_psw = str(sha256(data['password']+str(result['id'])).hexdigest())
            if result['password'] == str(hash_psw):
                data['auth'] = True
            # incorrect password --> fake user
            else:
                data['cmd'] = 'RAUT'
                data['error'].append('\nERROR: Incorrect password. Try again...')
                error_msg = "[AUTH] Incorrect password for user=%s" % data['user']
    return data, error_msg

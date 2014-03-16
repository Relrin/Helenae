"""
    This module contains basics commands, which [user/file server] can using
"""
from json import dumps
from hashlib import sha256

# available commands and handlers
commands_user = {"AUTH": "autorization with server",
                 "READ": "read some file from storage",
                 "WRTE": "write file into storage",
                 "DELT": "delete file from storage",
                 "RNME": "rename file",
                 "LIST": "get list of all files from storage with this user",
                 "SYNC": "synchronize all files with storage on the server",
                 "EXIT": "disconnect from server or end session"}

commands_handlers_user   = dict((key, None) for key in commands_user.keys())
commands_handlers_server = dict((key, None) for key in commands_user.keys() if key not in ('AUTH', 'EXIT'))

def constructBasicJSON():
    """
        Create basic JSON for operations
    """
    data = {}
    data['cmd'] = None
    data['user'] = None
    data['password'] = None
    data['auth'] = None
    data['error'] = None
    return data


def constructDataClient(cmd, user, hash_password, auth, error=''):
    """
        Create JSON for server from Client
    """
    data = constructBasicJSON()
    data['cmd'] = cmd
    data['user'] = user
    data['password'] = hash_password
    data['auth'] = auth
    data['error'] = error
    return dumps(data)


def constructInfoFileServer(cmd, user, hash_password, auth, error='', server_info=()):
    """
        Create JSON, which contains useful information about server for client
    """
    data = constructBasicJSON()
    data['cmd'] = cmd
    data['user'] = user
    data['password'] = hash_password
    data['auth'] = auth
    data['error'] = error
    data['server'] = server_info
    return dumps(data)


def AUTH(result, data):
    error_msg = "[AUTH] User=%s successfully logged..." % data['user']
    # user not found at DB
    if result is None:
        data['cmd'] = 'RAUT'
        data['error'] = 'User not found'
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
                data['error'] = 'Incorrect password. Try again...'
                error_msg = "[AUTH] Incorrect password for user=%s" % data['user']
    return data, error_msg
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
    data['error'] = []
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
    if error:
        data['error'].append(error)
    return dumps(data)


def constructFileDataByClient(cmd, user, hash_password, auth, file_path, file_size, file_hash, error=''):
    """
        Create JSON for WRTE, DELT, READ operations
    """
    data = constructBasicJSON()
    data['cmd'] = cmd
    data['user'] = user
    data['password'] = hash_password
    data['auth'] = auth
    data['file_path'] = file_path
    data['file_hash'] = file_hash
    data['file_size'] = file_size
    if error:
        data['error'].append(error)
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
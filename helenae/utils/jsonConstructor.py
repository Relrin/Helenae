from json import dumps, dump


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


def dumpConfigToJSON(json_file, cmd, user_id, file_id, src_file, key, algorithm='AES-256'):
    """
        Write config to JSON file
    """
    with open(json_file, 'w+') as f:
        dict_json = {"cmd": cmd, "user": user_id, "file_id": file_id, "src_file": src_file, "password": key,
        "algorithm": algorithm}
        dump(dict_json, f)

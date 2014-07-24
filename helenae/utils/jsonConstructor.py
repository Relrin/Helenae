from json import dumps


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
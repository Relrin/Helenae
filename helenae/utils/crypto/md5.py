import os
from hashlib import md5


def md5_for_file(file_path, block_size=8192):
    """
        Calculating MD5 hash for file
    """
    size = 0
    md5_hash = md5()
    try:
        size = os.path.getsize(file_path)
        f = open(file_path, 'rb')
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5_hash.update(data)
        f.close()
    except IOError:
        print 'ERROR: No such file or directory'
    return md5_hash.hexdigest(), size
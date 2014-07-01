"""
    Wrapper for AES 128/192/256 encryption

    Example of using:
        import os
        password = os.urandom(16).encode('hex')
        with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
            funct = encrypt(in_file, password, key_length=16)
            for chunk in func:
                out_file.write(chunk)
        with open(in_filename, 'rb') as in_file, open(out_filename, 'wb') as out_file:
            for chunk in decrypt(in_file, out_file, password, key_length=16):
                out_file.write(chunk)
"""

# TODO: create test, bases on http://www.inconteam.com/software-development/41-encryption/55-aes-test-vectors

from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random


def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]


def encrypt(in_file, password, key_length=32):
    """
        Encrypt file

        :param in_file: file descriptor to file
        :param password: its your secret key
        :param key_length: length of secret key
        :return: encrypted chunks
    """
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    yield ('Salted__' + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
        yield cipher.encrypt(chunk)


def decrypt(in_file, password, key_length=32):
    """
        Decrypt file

        :param in_file: file descriptor to encrypted file
        :param password: its your secret key
        :param key_length: length of secret key
        :return: decrypted chunks
    """
    bs = AES.block_size
    salt = in_file.read(bs)[len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        yield chunk
"""
    Wrapper for Twofish encryption

    Example of using:
        import os
        password = os.urandom(16).encode('hex')
        crypto_object = Twofish_wrapper()
        in_filename = "test.txt"
        enc_filename = "enc.txt"
        decoded_filename = "dec.txt"

        with open(in_filename, 'rb') as in_file, open(enc_filename, 'wb') as out_file:
            for chunk in crypto_object.encrypt(in_file, password, key_length=32):
                out_file.write(chunk)

        with open(enc_filename, 'rb') as in_file:
            text = in_file.read()
            with open(decoded_filename, 'wb') as out_file:
                for chunk in crypto_object.decrypt(text, password, key_length=32):
                    out_file.write(chunk)
"""

from CryptoPlus.Cipher.python_Twofish import Twofish


class Twofish_wrapper:

    obj = None
    block_size = 16

    def get_Twofish_cls(self, password):
        if not self.obj:
            self.obj = Twofish(password)
        return self.obj

    def encrypt(self, in_file, password, key_length=32):
        """
            Encrypt file

            :param in_file: file descriptor to file
            :param password: its your secret key
            :param key_length: length of secret key
            :return: encrypted chunks
        """
        cryptographer = self.get_Twofish_cls(password)
        while True:
            chunk = in_file.read(self.block_size)
            if not chunk:
                break
            chunk = chunk.ljust(self.block_size, '\x00')
            yield cryptographer.encrypt(chunk)

    def decrypt(self, text, password, key_length=32):
        """
            Decrypt file

            :param in_file: file descriptor to encrypted file
            :param password: its your secret key
            :param key_length: length of secret key
            :return: decrypted chunks
        """
        cryptographer = self.get_Twofish_cls(password)
        next_chunk = ''
        counter_block = 1
        while True:
            start = (counter_block - 1) * self.block_size
            end = counter_block * self.block_size
            enc_txt = text[start:end]
            if not enc_txt:
                yield next_chunk.replace('\x00', '')
                break
            chunk, next_chunk = next_chunk, cryptographer.decrypt(enc_txt)
            counter_block += 1
            yield chunk.replace('\x00', '')

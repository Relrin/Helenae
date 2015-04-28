"""
    Wrapper for Serpent encryption

    Example of using:
        import os
        password = os.urandom(32).encode('hex')
        crypto_object = Serpent_wrapper()
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

from CryptoPlus.Cipher.python_Serpent import Serpent


class Serpent_wrapper():

    obj = None
    block_size = 16

    def get_Serpent_cls(self, password):
        if not self.obj:
            self.obj = Serpent(password)
        return self.obj

    def encrypt(self, in_file, password, key_length=32):
        cryptographer = self.get_Serpent_cls(password)
        finished = False
        while not finished:
            chunk = in_file.read(self.block_size)
            if not chunk:
                break
            if len(chunk) % self.block_size != 0:
                finished = True
            yield cryptographer.encrypt(chunk)

    def decrypt(self, text, password, key_length=32):
        cryptographer = self.get_Serpent_cls(password)
        finished = False
        next_chunk = ''
        counter_block = 1
        while not finished:
            start = (counter_block - 1) * self.block_size
            end = counter_block * self.block_size
            enc_txt = text[start:end]
            if not enc_txt:
                finished = True
                yield next_chunk.replace('\x00', '')
                break
            chunk, next_chunk = next_chunk, cryptographer.decrypt(enc_txt)
            if len(next_chunk) == 0:
                finished = True
            counter_block += 1
            yield chunk.replace('\x00', '')

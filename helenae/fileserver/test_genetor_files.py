import random
import string


def generate_file(count, min_len=128, max_len=512):
    for i in xrange(0, count):
        msg_length = random.randint(min_len, max_len)
        message = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                          for x in xrange(msg_length))
        file_name = str(i).rjust(3, '0')
        f = open('text-%s.txt' % file_name, 'w')
        f.write(message)
        f.close()
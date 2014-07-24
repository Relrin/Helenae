from math import log

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
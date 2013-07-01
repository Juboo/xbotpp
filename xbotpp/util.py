# vim: noai:ts=4:sw=4:expandtab:syntax=python

import string
import random


def random_string(size=10, chars=None):
    '''\
    Returns a random string of the given size and character set.

    The default character set is ``string.ascii_lowercase + 
    string.ascii_uppercase + string.digits``.
    '''

    chars = chars or string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))

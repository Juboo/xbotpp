__xbotpp_module__ = "text"

import re
import xbotpp
import argparse
import xbotpp.debug
import xbotpp.modules


def _tr(str, inAlphabet='aeioubcdfghjklmnpqrstvwxyz', outAlphabet='iouaenpqrstvwxyzbcdfghjklm'):
    buffer = ""
    for value in str:
        if value.lower() in inAlphabet:
            if value in inAlphabet:
                index = inAlphabet.index(value)
            else:
                index = inAlphabet.index(value.lower())

            c = outAlphabet[index] if (value in outAlphabet or value.lower() in outAlphabet) else value
            buffer += c.upper() if re.search("[A-Z]", value) else c
        else:
            buffer += value
    return buffer


@xbotpp.modules.on_command('tr')
def tr(info, args, buf):
    """\
    FIXME: docs
    """

    default_in = "abcdefghijklmnopqrstuvwxyz"
    default_out = "nopqrstuvwxyzabcdefghijklm"

    h = '<command> | tr [input-alphabet] [output-alphabet]\nDefault input alphabet: "%s"\nDefault output alphabet: "%s"' % (default_in, default_out)

    parser = argparse.ArgumentParser(prog='tr', add_help=False)
    parser.add_argument('-h', '--help', action='store_true', dest='help')
    parser.add_argument('a_in', nargs='?', type=str, action="store", default=default_in)
    parser.add_argument('a_out', nargs='?', type=str, action="store", default=default_out)

    try:
        options = parser.parse_args(args)
    except SystemExit:
        # assume that a SystemExit on parse is a 'invalid arguments', so print help
        return h

    if options.help or buf == "":
        return h

    return _tr(buf, options.a_in, options.a_out)


@xbotpp.modules.on_command('lolcrypt')
def lolcrypt(info, args, buf):
    """\
    Lolcrypt the given arguments, or the buffer (if present)

    Pass "-d" as the first parameter to de-lolcrypt.
    """

    if len(args) is 0 and buf == "":
        return "{0}lolcrypt [-d] <text> or {0}command | lolcrypt [-d]".format(xbotpp.config['bot']['prefix'])

    delol = (len(args) != 0 and args[0] == "-d")
    text = buf if buf != "" else " ".join(args[1:]) if delol else " ".join(args)

    if delol:
        # de-lolcrypt
        return _tr(text, 'iouaenpqrstvwxyzbcdfghjklm', 'aeioubcdfghjklmnpqrstvwxyz')
    else:
        # en-lolcrypt
        return _tr(text, 'aeioubcdfghjklmnpqrstvwxyz', 'iouaenpqrstvwxyzbcdfghjklm')

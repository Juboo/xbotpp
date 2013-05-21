# vim: noai:ts=4:sw=4:expandtab:syntax=python 

import re
import argparse
from xbotpp.modules import Module


class text(Module):
    """\
    Text manipulation commands.
    """

    def __init__(self):
        self.bind_command("lolcrypt", self.lolcrypt)
        self.bind_command("tr", self.tr)
        Module.__init__(self)
    
    def _tr(self, str, inAlphabet='aeioubcdfghjklmnpqrstvwxyz', outAlphabet='iouaenpqrstvwxyzbcdfghjklm'):
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

    def tr(self, bot, event, args, buf):
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

        return self._tr(buf, options.a_in, options.a_out) 

    def lolcrypt(self, bot, event, args, buf):
        """\
        Lolcrypt the given arguments, or the buffer (if present)

        Pass "-d" as the first parameter to de-lolcrypt.
        """

        if len(args) is 0 and buf == "":
            return "%slolcrypt [-d] <text> or %scommand | lolcrypt [-d]" % (self.bot.prefix, self.bot.prefix)

        delol = (len(args) != 0 and args[0] == "-d")
        text = buf if buf != "" else " ".join(args[1:]) if delol else " ".join(args[0:])

        if delol:
            # de-lolcrypt
            return self._tr(text, 'iouaenpqrstvwxyzbcdfghjklm', 'aeioubcdfghjklmnpqrstvwxyz')
        else:
            # en-lolcrypt
            return self._tr(text, 'aeioubcdfghjklmnpqrstvwxyz', 'iouaenpqrstvwxyzbcdfghjklm')


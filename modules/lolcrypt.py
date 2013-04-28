# vim: noai:ts=4:sw=4:expandtab:syntax=python

import re
from xbotpp.modules import Module


class lolcrypt(Module):
    """\
    Provide lolcryption.
    """

    def __init__(self):
        Module.__init__(self)

    def action(self, bot, event, args, buf):
        """\
        Lolcrypt the given arguments, or the buffer (if present)

        Pass "-d" as the first parameter to de-lolcrypt.
        """

        if len(args) is 0 and buf == "":
            return "%slolcrypt [-d] <text> or %scommand | lolcrypt [-d]" % (self.bot.prefix, self.bot.prefix)

        delol = (len(args) != 0 and args[0] == "-d")
        cipher = list("aeioubcdfghjklmnpqrstvwxyz")
        text = buf if buf != "" else " ".join(args[1:]) if delol else " ".join(args[0:])
        mod = lambda a, n: ((a%n)+n)%n
        buf = "" 

        for char in text:
            if not char in cipher:
                buf += char
                continue

            caps = re.match("[A-Z]", char)
            char = char.lower()
            i = cipher.index(char)
            if re.match("[" + "".join(cipher[0:5]) + "]", char):
                if delol:
                    char = cipher[mod(i-2,5)]
                else:
                    char = cipher[(i+2)%5]
            else:
                if delol:
                    char = cipher[mod(i-15,21)+5]
                else:
                    char = cipher[(i+5)%21+5]

            buf += char.upper() if caps else char

        return buf


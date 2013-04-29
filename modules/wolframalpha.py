# vim: noai:ts=4:sw=4:expandtab:syntax=python

import lxml.etree
import urllib.parse
import urllib.request
from xbotpp.modules import Module

class wolframalpha(Module):
    """\
    WolframAlpha module.
    """

    def __init__(self):
        self.bind = [
            ["command", "calc", self.calc, "common"],
        ]
        Module.__init__(self)

    def load(self):
        self.apikey = self.bot.config.get("module: wolframalpha", "apikey")

    def parse_result(self, result):
        acceptable = [
            'Result',
            'Results',
            'Solution',
            'Value',
            'Name',
            'Derivative',
            'Indefinite integral',
            'Distance',
            'Current result*',
            'Scientific notation',
            'Truth table',
            'Differential equation solution',
            'Decimal form',
            'Decimal approximation',
            'Exact result',
            'Rational approximation',
            'Geometric figure',
            'Definition',
            'Basic definition',
            'Result for *',
            'Number length',
            'Definitions',
            'Unit conversions',
            'Electromagnetic frequency range',
            'IP address registrant',
            'Address properties',
            'Web hosting information',
            'Current age',
            'Basic information',
            'Latest result',
            'Response',
            'Names and airport codes',
            'Latest recorded weather *',
            'Series information',
            'Latest trade',
            'Definitions of *',
            'Possible interpretation*',
            'Lifespan',
            'Cipher text',
            'Statement',
            'Events on *',
            'Time span',
            'Unicode block',
            'Eclipse date',
            'Total eclipse*',
            'Solar wind',
            'Weather forecast for *',
            'Notable events in *',
            'Events on *',
            'Possible sequence identification',
            'Length of data',
            'Properties',
            'Approximate results',
            'Summary',
            'Nearest named HTML colors',
        ]

        for title in acceptable:
            try:
                if '*' in title:
                    x = result.xpath("/queryresult[@success='true']/pod[contains(@title, '%s')]/subpod/plaintext/text()" % title.replace("*", ""))
                else:
                    x = result.xpath("/queryresult[@success='true']/pod[@title='%s']/subpod/plaintext/text()" % title)
            except:
                pass

            if x:
                return x

        if result.xpath("/queryresult[@success='false']"):
            try:
                alternatives = result.xpath("/queryresult/relatedexamples/relatedexample[@input]")
            except:
                alternatives = False

            if alternatives:
                return ["Query not understood, suggestion%s: %s" % ('s' if len(alternatives) > 1 else '', ' | '.join([alt.values()[0].strip() for alt in alternatives]))]
            else:
                return ["Query not understood."]
        else:
            return ["No acceptable mathematical result."]

    def get_result(self, query):
        """\
        Query WolframAlpha for `query`.

        :param query: str
        :rtype: str
        """

        isinstance(query, str), "Query must be a string"

        url = "http://api.wolframalpha.com/v2/query?appid=%s&input=%s&format=plaintext" % (self.apikey, urllib.parse.quote(query))

        response = urllib.request.urlopen(url, timeout=10)
        result = self.parse_result(lxml.etree.parse(response))
        result = "\n".join(result).strip()
        result = result.replace('\\:', '\\u')
        result = result.replace("Wolfram|Alpha", self.bot.connection.get_nickname())
        result = result.replace("Stephen Wolfram", "Zarek Jenkinson")

        return result

    def calc(self, bot, event, args, buf):
        query = ""

        if buf != "":
            query = buf
        elif len(args) >= 1:
            query = " ".join(args)
        else:
            return "%scalc <args> or %scommand | calc" % (bot.prefix, bot.prefix)

        return self.get_result(query)
    

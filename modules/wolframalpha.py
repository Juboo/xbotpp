# vim: noai:ts=4:sw=4:expandtab:syntax=python
__xbotpp_module__ = "wolframalpha"

import lxml.etree
import urllib.parse
import urllib.request
import xbotpp
import xbotpp.modules


def parse_result(result):
    """\
    Search the WolframAlpha API data for a sane data value from a predefined set of
    "good" data (ie. data that is formatted well enough to be piped into an IRC channel)
    """

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


def get_result(query):
    """\
    Query WolframAlpha for `query`.

    :param query: str
    :rtype: str
    """

    isinstance(query, str), "Query must be a string"
    apikey = xbotpp.config['modules']['wolframalpha']['apikey']

    url = "http://api.wolframalpha.com/v2/query?appid=%s&input=%s&format=plaintext" % (apikey, urllib.parse.quote(query))

    response = urllib.request.urlopen(url, timeout=10)
    result = parse_result(lxml.etree.parse(response))
    result = "\n".join(result).strip()
    result = result.replace('\\:', '\\u')
    result = result.replace("Wolfram|Alpha", xbotpp.state.connection.get_nickname())
    result = result.replace("Stephen Wolfram", "Aki Jenkinson")

    return result


@xbotpp.modules.on_command('calc')
def calc(info, args, buf):
    """\
    Call the :py:func:`get_result` function with the arguments or the input buffer
    (if present) and return the result. If no input is specified, return basic help
    on the command.
    """

    query = ""

    if buf != "":
        query = buf
    elif len(args) >= 1:
        query = " ".join(args)
    else:
        return "{prefix}calc <args> or {prefix}command | calc".format(prefix=xbotpp.config['bot']['prefix'])

    return get_result(query)

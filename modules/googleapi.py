__xbotpp_module__ = "googleapi"

import json
import xbotpp
import xbotpp.debug
import xbotpp.modules
import urllib.request

def setup_extras():
    '''\
    Initialize the 'extra' search commands specified in the settings.

    This function runs when the module is imported.

    The configration for this is as follows:

    .. code-block:: json

       {
           "modules": {
               "googleapi": {
                   "extras": {
                       "archwiki": "site:wiki.archlinux.org",
                       "aur": "site:aur.archlinux.org"
                   }
               }
           }
       }

    '''

    if 'googleapi' in xbotpp.config['modules'] and 'extras' in xbotpp.config['modules']['googleapi']:
        for _name in xbotpp.config['modules']['googleapi']['extras'].keys():
            @xbotpp.modules.on_command(_name)
            @xbotpp.util.change_name(_name)
            def extra_search(info, args, buf):
                name = info['command_name']
                try:
                    terms = xbotpp.config['modules']['googleapi']['extras'][name]
                    xbotpp.debug.write("name: {0}; terms: {1}".format(name, terms))
                    r = search([terms] + args)
                    if r != False:
                        return r
                    else:
                        return "{p}{s} <query>".format(p=xbotpp.config['bot']['prefix'],s=s)
                except Exception as e:
                    xbotpp.debug.exception('Error in extra_search [name: {}]'.format(name), e)

@xbotpp.modules.on_command('go')
def do_search(info, args, buf):
    '''\
    Initiate a search with the given arguments.
    '''

    r = search(args)
    if r != False:
        return r
    else:
        return "{p}go [cr=<2-letter country code>] <query>".format(p=xbotpp.config['bot']['prefix'])

def search(args):
    if len(args) >= 2:
        title = ""
        
        if args[0].startswith("cr="):
            expr = __import__('re').search('cr=([a-zA-Z]{2})$', args[1])
            if expr:
                country = expr.group(1).upper()
                if country == "CN":
                    return "google.cn? hah."
            else:
                return "Invalid country code."
            terms = ' '.join(args[1:])
        else:
            country = ""
            terms = ' '.join(args)

        url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&safe=off&q=%s&gl=%s" % (urllib.request.quote(terms), country)
        result = str(urllib.request.urlopen(url, timeout=5).read(), 'utf-8')
        jsondata = json.loads(result)

        try:
            url = jsondata['responseData']['results'][0]['unescapedUrl']
            if country:
                return "From %s only: %s" % (country, url)
            else:
                return url
        except IndexError:
            return "Your search did not return any results."
    else:
        return False

setup_extras()

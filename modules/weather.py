__xbotpp_module__ = "weather"

import os
import json
import urllib.request
import urllib.parse
import xbotpp
import xbotpp.modules

def save_user(nick, location):
    xbotpp.state.modules.moddata['weather'][nick] = location

@xbotpp.modules.on_command('we')
def weather(info, args, buf):
    '''\
    Get the weather. Saves the last location that a user requested and uses
    that for their next request if that request didn't have a location.
    '''

    users = xbotpp.state.modules.moddata['weather']

    location = ""

    if len(args) >= 1:
        location = " ".join(args)
        save_user(info['source'], location)
    elif info['source'] in users:
        location = users[info['source']]
    elif info['source'] not in users and len(args) is 0:
        return "I don't know where you are, %s (use ^we <location> to set your location)" % info['source']

    return getweather(location)

def getweather(location):
    '''\
    Actually get the weather.
    '''

    if 'weather' in xbotpp.config['modules'] and 'apikey' in xbotpp.config['modules']['weather']:
        apikey = xbotpp.config['modules']['weather']['apikey']
    else:
        return "weather: Not configured."

    location = location.replace(' ', '+')
    url = "https://api.wunderground.com/api/%s/geolookup/conditions/q/%s.json" % (apikey, urllib.parse.quote(location))
    xbotpp.debug.write("URL: %s" % url)
    data = json.loads(str(urllib.request.urlopen(url).read(), 'utf-8'))

    if 'current_observation' in data:
        fm = {
            'location': data['current_observation']['display_location']['full'],
            'condition': data['current_observation']['weather'],
            'temp_c': "{}°C".format(str(data['current_observation']['temp_c'])),
            'temp_f': "{}°F".format(str(data['current_observation']['temp_f'])),
            'humidity': data['current_observation']['relative_humidity'],
        }

        return "{location}: {condition} | {temp_c} ({temp_f}) | {humidity} humidity".format(**fm)

    else:
        return "weather: Data for given location not found."

# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import json
import urllib.request
import urllib.parse
from xbotpp.modules import Module


class weather(Module):
    """\
    Get weather from wunderground.
    """

    def __init__(self):
        self.bind_command("we", self.weather)
        Module.__init__(self)

    def load(self):
        self.configpath = os.path.join(self.bot.modules.configpath, "weather.users.json")
        if not os.path.exists(self.configpath):
            with open(self.configpath, "w+") as f:
                f.write("{}")

    def save(self, nick, location):
        """\
        Save an IRC nick paired with a location to the config.
        """
        
        users = json.load(open(self.configpath))
        users[nick] = location
        with open(self.configpath, "w+") as f:
            f.write(json.dumps(users))

    def weather(self, bot, event, args, buf):
        """\
        Get the weather. Saves the last location that a user requested and uses
        that for their next request if that request didn't have a location.
        """

        users = json.load(open(self.configpath))
        location = ""

        if len(args) >= 1:
            location = " ".join(args)
            self.save(event.source.nick, location)
        elif event.source.nick in users:
            location = users[event.source.nick]
        elif event.source.nick not in users and len(args) is 0:
            return "I don't know where you are, %s (use ^we <location> to set your location)" % event.source.nick

        return self.getweather(location)
        
    def getweather(self, location):
        """\
        Actually get the weather.
        """

        if self.bot.config.has_option("module: weather", "apikey"):
            apikey = self.bot.config.get("module: weather", "apikey")
        else:
            return "weather: Not configured."

        location = location.replace(' ', '+')
        url = "https://api.wunderground.com/api/%s/geolookup/conditions/q/%s.json" % (apikey, urllib.parse.quote(location))
        self.bot._debug("URL: %s" % url)
        data = json.loads(str(urllib.request.urlopen(url).read(), 'utf-8'))

        if 'current_observation' in data:
            location = data['current_observation']['display_location']['full']
            condition = data['current_observation']['weather']
            temperature = data['current_observation']['temperature_string']
            humidity = data['current_observation']['relative_humidity']

            return "Weather for %s: %s, %s, Humidity: %s" % (location, condition, temperature, humidity)
        else:
            return "weather: Data for given location not found."


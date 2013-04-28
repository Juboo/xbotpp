# vim: noai:ts=4:sw=4:expandtab:syntax=python

import json
import urllib.request
import urllib.parse
from xbotpp.modules import Module


class lastfm(Module):
    """\
    Get users' now playing information from last.fm.

    Requires a [module: lastfm] configuration section with an "apikey"
    parameter, which is a last.fm application API key.
    """

    def __init__(self):
        self.bind = [
            ["command", "np", self.nowplaying, "common"],
        ] 
        self.users = json.load(open("lastfm.users.json"))
        Module.__init__(self)

    def save(self, nick, lastfmuser):
        """\
        Save an IRC nick paired with a last.fm username to the config.
        """
        
        self.users[nick] = lastfmuser
        with open("lastfm.users.json", "wt") as f:
            f.write(json.dumps(self.users))

    def nowplaying(self, bot, event, args, buf):
        """\
        Get a user's currently playing track.

        If the user is recognized (ie, has set their last.fm username),
        ^np will tell the channel their now playing track.

        For a user to set their last.fm username, they can use ^np <username>.

        To get the now playing track of another user, ^np @<nick> can be used.
        """

        if len(args) >= 1 and args[0].startswith("@"):
            if args[1:] in self.users:
                user = self.users[args[1:]]
            else:
                return "Who?"
        elif event.source.nick not in self.users and len(args) is 0:
            return "I don't know what your last.fm username is, %s (use %snp <username> to set it)" % (event.source.nick, self.bot.prefix)
        elif len(args) >= 1 and not args[0].startswith("@"):
            user = args[0]
            self.save(event.source.nick, user)
        elif event.source.nick in self.users:
            user = self.users[event.source.nick]
        else:
            return "What?"

        try:
            url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json" % (urllib.parse.quote(user), self.bot.config.get("module: lastfm", "apikey"))
            data = json.loads(str(urllib.request.urlopen(url).read(), 'utf-8'))
            track = data["recenttracks"]["track"][0]
            if "@attr" in track:
                status = "is now listening to" if track["@attr"]["nowplaying"] == "true" else "was previously listening to"
            else:
                status = "was previously listening to"
            title = track["name"]
            artist = "by %s" % track["artist"]["#text"] if track["artist"]["#text"] else ""
            album = "from %s" % track["album"]["#text"] if track["album"]["#text"] else ""
            
            return "%s %s %s %s %s" % (user, status, title, artist, album)

        except:
            raise

    

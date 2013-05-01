# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
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
        Module.__init__(self)

    def load(self):
        self.configpath = os.path.join(self.bot.modules.configpath, "lastfm.users.json")
        if not os.path.exists(self.configpath):
            with open(self.configpath, "w+") as f:
                f.write("{}")

    def save(self, nick, lastfmuser):
        """\
        Save an IRC nick paired with a last.fm username to the config.
        """
        
        users = json.load(open(self.configpath))
        users[nick] = lastfmuser
        with open(self.configpath, "w+") as f:
            f.write(json.dumps(users))

    def nowplaying(self, bot, event, args, buf):
        """\
        Get a user's currently playing track.

        If the user is recognized (ie, has set their last.fm username),
        ^np will tell the channel their now playing track.

        For a user to set their last.fm username, they can use ^np <username>.

        To get the now playing track of another user, ^np @<nick> can be used.

        ^np * will also get the new playing tracks of every person in the channel
        who has set their last.fm username.
        """

        users = json.load(open(self.configpath))
        searchusers = {}

        if buf != "":
            args = buf.split()

        if len(args) is 1 and args[0] == "*":
            for user in self.bot.channels[event.target].users():
                if user in users:
                    searchusers[user] = users[user]
        elif len(args) >= 1 and args[0].startswith("@"):
            if args[0][1:] in users:
                searchusers[args[0][1:]] = users[args[0][1:]]
            else:
                return "Who?"
        elif event.source.nick not in users and len(args) is 0:
            return "I don't know what your last.fm username is, %s (use %snp <username> to set it)" % (event.source.nick, self.bot.prefix)
        elif len(args) >= 1 and not args[0].startswith("@"):
            searchusers[event.source.nick] = args[0]
            self.save(event.source.nick, args[0])
        elif event.source.nick in users:
            searchusers[event.source.nick] = users[event.source.nick]
        else:
            return "What?"

        ret = []

        for obj in searchusers:
            res = self.getlastfm(searchusers[obj])
            if res != None:
                if len(searchusers) is 1:
                    ret.append(res)
                else:
                    ret.append("%s: %s" % (obj, res))
            else:
                if len(searchusers) is 1:
                    ret.append("I couldn't get the last.fm info for %s (try setting your username again?)" % obj)
                else:
                    pass

        return "\n".join(ret)

    def getlastfm(self, user):
        """\
        Query last.fm for information on the given user.
        Used internally by the :py:func:`nowplaying` function.

        :param user: str
        """

        try:
            url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json" % (urllib.parse.quote(user), self.bot.config.get("module: lastfm", "apikey"))
            print(url)
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
            return None
 

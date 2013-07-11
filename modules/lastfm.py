# vim: noai:ts=4:sw=4:expandtab:syntax=python
__xbotpp_module__ = "lastfm"

import os
import json
import urllib.request
import urllib.parse
import xbotpp
import xbotpp.modules

def save_user(nick, lastfmuser):
    xbotpp.state.modules.moddata['lastfm'][nick] = lastfmuser

@xbotpp.modules.on_command('np')
def nowplaying(info, args, buf):
    """\
    Get a user's currently playing track.

    If the user is recognized (ie, has set their last.fm username),
    ^np will tell the channel their now playing track.

    For a user to set their last.fm username, they can use ^np <username>.

    To get the now playing track of another user, ^np @<nick> can be used.
    """

    users = xbotpp.state.modules.moddata['lastfm']
    xbotpp.debug.write(repr(users))
    searchusers = {}

    if buf != "":
        args = buf.split()

    if len(args) >= 1 and args[0].startswith("@"):
        if args[0][1:] in users:
            searchusers[args[0][1:]] = users[args[0][1:]]
        else:
            return "Who?"
    elif info['source'] not in users and len(args) is 0:
        return "I don't know what your last.fm username is, %s (use %snp <username> to set it)" % (info['source'], xbotpp.config['bot']['prefix'])
    elif len(args) >= 1 and not args[0].startswith("@"):
        searchusers[info['source']] = args[0]
        save_user(info['source'], args[0])
    elif info['source'] in users:
        searchusers[info['source']] = users[info['source']]
    else:
        return "What?"

    ret = []

    for obj in searchusers.keys():
        res = getlastfm(searchusers[obj])
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

def getlastfm(user):
    """\
    Query last.fm for information on the given user.
    Used internally by the :py:func:`nowplaying` function.

    :param user: str
    """

    try:
        apikey = xbotpp.config['modules']['lastfm']['apikey']
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user=%s&api_key=%s&format=json" % (urllib.parse.quote(user), apikey)
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


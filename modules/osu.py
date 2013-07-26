__xbotpp_module__ = "osu"

import json
import urllib.parse
import urllib.request
import xbotpp
import xbotpp.modules


#: Available osu! gamemodes.
gamemodes = {
    0: 'osu!',
    1: 'Taiko',
    2: 'CtB',
    3: 'osu!mania',
}

def save_user(nick, username):
    xbotpp.state.modules.moddata['osu'][nick] = username

def get_stats(user, mode=0):
    '''\
    Get statistics for a given user from the osu! API.

    `mode` is an integer, representing the gamemode to retrieve the statistics
    for:

    - 0: osu! (the default)
    - 1: Taiko
    - 2: CtB
    - 3: osu!mania

    Raises a :exc:`KeyError` if the mode is not valid, (re-)raises a urllib
    exception if there was an error retrieving the data, returns None if the
    module is not configured (no API key present), or returns the user's info
    as a dictionary, in the same format presented by the osu! API. For the API
    documentation, see '<https://github.com/peppy/osu-api/wiki#apiget_user>`_.
    '''

    if not 'osu' in xbotpp.config['modules'] or not 'apikey' in xbotpp.config['modules']['osu']:
        xbotpp.debug.write("osu! API key not in config file, bailing")
        return None

    if mode > 3 or mode < 0:
        # made has to be 0-3
        raise KeyError('mode')

    try:
        postdata = urllib.parse.urlencode({
            'k': xbotpp.config['modules']['osu']['apikey'],
            'u': user,
            'm': mode,
        })
        xbotpp.debug.write('postdata: {}'.format(repr(postdata)))

        request = urllib.request.Request('http://osu.ppy.sh/api/get_user', bytes(postdata.encode('utf-8')))
        xbotpp.debug.write("request: {}".format(repr(request)))
        data = json.loads(str(urllib.request.urlopen(request).read(), 'utf-8').strip())[0]
        return data

    except Exception as e:
        xbotpp.debug.exception("Exception retrieving osu! user data for {}".format(user), e)
        xbotpp.debug.write(repr(e))
        raise

@xbotpp.modules.on_command('osu')
def osu_command(info, args, buf):
    # mode number to get info for. default is 0 which is osu!, and this will be
    # changed by the arguments if-block below if it needs to be
    gamemode = 0

    if len(args) > 1 and args[0].startswith('-'):
        # assume starting with '-' means it's a switch, so handle it as one
        if args[0] == '-t':
            gamemode = 1
            args = args[1:]
        elif args[0] == '-c':
            gamemode = 2
            args = args[1:]
        elif args[0] == '-m':
            gamemode = 3
            args = args[1:]

    xbotpp.debug.write('osu! gamemode: {}'.format(gamemodes[gamemode]))

    # determine username
    if len(args) is not 0:
        user = ' '.join(args)
        xbotpp.debug.write('User: {0} (saving for nick {1})'.format(user, repr(info['source'])))
        save_user(info['source'], user)
    elif info['source'] in xbotpp.state.modules.moddata['osu']:
        user = xbotpp.state.modules.moddata['osu'][info['source']]
        xbotpp.debug.write('User: {0} from users[{1}]'.format(user, repr(info['source'])))
    elif not info['source'] in xbotpp.state.modules.moddata['osu'] and len(args) is 0:
        xbotpp.debug.write('No stored username for nick {}'.format(repr(info['source'])))
        return "I don't know your osu! username, {}!".format(info['source'])

    # get the info
    try:
        data = get_stats(user, gamemode)
    except KeyError:
        return "osu: Invalid mode."
    except IndexError:
        return "No data for user {}.".format(user)
    except:
        # send this up the chain if something weird happened
        raise

    if not data:
        return "osu: Not configured."

    formatstr = "{mode} stats for {user}: #{rank}, Level {level} ({level_percent}%), ranked score {ranked}, {plays} plays, {accuracy}% accuracy"
    formatdata = {
        'mode': gamemodes[gamemode],
        'user': data['username'],
        'rank': data['pp_rank'],
        'level': int(float(data['level'])),
        'level_percent': "{0:.2f}".format(float('0.{}'.format(data['level'].split('.')[1])) * 100),
        'ranked': data['ranked_score'],
        'plays': data['playcount'],
        'accuracy': "{0:.2f}".format(float(data['accuracy'])),
    }

    return formatstr.format(**formatdata)

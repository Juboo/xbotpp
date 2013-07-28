import xbotpp
import xbotpp.debug
import xbotpp.modules
__xbotpp_module__ = "badwords"

import re

@xbotpp.modules.on_event('message')
def badwords(event):
    '''\
    Kick people who say a bad word in a channel.
    '''
    if event.target in xbotpp.config['modules']['badwords']:
        for word in xbotpp.config['modules']['badwords'][event.target]:
            if re.match(word, event.message):
                xbotpp.state.connection.connection.kick(event.target, event.source, "You said a bad word.")
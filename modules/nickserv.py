import xbotpp
import xbotpp.debug
import xbotpp.modules
__xbotpp_module__ = "nickserv"

@xbotpp.modules.on_event('message')
def nickserv_auth(event):
    '''\
    Automatically authenticate with NickServ when an authentication request is received.
    '''

    if 'nickserv_password' in xbotpp.config['networks'][xbotpp.state.network]:
        if "this nickname is registered" in event.message.lower():
            xbotpp.debug.write("Sending NickServ authentication...", xbotpp.debug.levels.Info)
            password = xbotpp.config['networks'][xbotpp.state.network]['nickserv_password']
            xbotpp.state.connection.send_message("nickserv", "identify {}".format(password))
        

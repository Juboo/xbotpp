# vim: noai:ts=4:sw=4:expandtab:syntax=python

import xbotpp
import irc.client as irclib_client
import irc.dict as irclib_dict
import irc.bot as irclib_bot
from xbotpp import debug
from xbotpp import handler


class ServerSpec:
    '''\
    An IRC server specification.
    '''

    def __init__(self, host, port=6667, password=None):
        self.host = host
        self.port = port
        self.password = password

    def __str__(self):
        return '%s:%d' % (self.host, self.port)

class irc(irclib_client.SimpleIRCClient):
    '''\
    Our IRC client class.
    '''

    def __init__(self, config, state):
        self.network = config['networks'][state['network']]
        self.channels = irclib_dict.IRCDict()
        self._nickname = network['nick']
        self._realname = config['bot']['owner']
        self.handlers = handler.handlers()

        # Get hosts from the config and transform them into ServerSpec objects
        self.hosts = []
        serverpass = self.network['server_password'] if 'server_password' in self.network else None
        for host in [s.strip() for s in self.network['servers'].split(',')]:
            host = host.split(":")
            self.hosts.append(self.ServerSpec(host[0], int(host[1]), serverpass))

    def _on_event(self, events):
        def decorator(f):
            if isinstance(events, str):
                events = [events]
            for event_name in events:
                self.connection.add_global_handler(event_name, f, 0)
            return f
        return decorator

    def _connect(self):
        server = self.hosts[0]
        try:
            debug.write('Connecting to %s...' % server, debug.levels.Info)
            self.connect(server.host, server.port, self._nickname, server.password, ircname=self._realname)
        except irclib_client.ServerConnectionError:
            debug.write('Error connecting to %s' % server, debug.levels.Info)

    @_on_event('disconnect')
    def _on_disconnect(self, client, event):
        debug.write('Disconnected.', debug.levels.Info)
        self.channels = IRCDict()

    @_on_event('join')
    def _on_join(self, client, event):
        channel = event.target
        nick = event.source.nick

        if nick == client.get_nickname():
            self.channels[channel] = irclib_bot.Channel()

        self.channels[channel].add_user(nick)

    @_on_event('kick')
    def _on_kick(self, client, event):
        nick = event.arguments[0]
        channel = event.target

        if nick == client.get_nickname():
            del self.channels[channel]
        else:
            self.channels[channel].remove_user(nick)

    @_on_event('mode')
    def _on_mode(self, client, event):
        modes = irclib_modes.parse_channel_modes(" ".join(event.arguments))
        target = event.target
        if irc.client.is_channel(target):
            channel = self.channels[target]
            for mode in modes:
                if mode[0] == "+":
                    f = channel.set_mode
                else:
                    f = channel.clear_mode
                f(mode[1], mode[2])
        else:
            pass

    @_on_event('namreply')
    def _on_namreply(self, client, event):
        channel = event.arguments[1]
        for nick in event.arguments[2].split():
            nick_modes = []

            if nick[0] in self.connection.features.prefix:
                nick_modes.append(self.connection.features.prefix[nick[0]])
                nick = nick[1:]

            for mode in nick_modes:
                self.channels[channel].set_mode(mode, nick)

            self.channels[channel].add_user(nick)

    @_on_event('nick')
    def _on_nick(self, client, event):
        before = event.source.nick
        after = event.target
        for channel in self.channels.values():
            if channel.has_user(before):
                channel.change_nick(before, after)

    @_on_event('part')
    def _on_part(self, client, event):
        nick = event.source.nick
        channel = event.target

        if nick == client.get_nickname():
            del self.channels[channel]
        else:
            self.channels[channel].remove_user(nick)

    @_on_event('quit')
    def _on_quit(self, client, event):
        nick = event.source.nick
        for channel in self.channels.values():
            if channel.has_user(nick):
                channel.remove_user(nick)

    @_on_event('nicknameinuse')
    def _on_nicknameinuse(self, client, event):
        client.nick(client.get_nickname() + "_")

    @_on_event('welcome')
    def _on_welcome(self, client, event):
        for channel in [s.strip() for s in self.network['channels'].split(",")]:
            client.join(channel)

    @_on_event(['pubmsg', 'privmsg', 'notice'])
    def generic_message(self, client, event):
        '''\
        Generic IRC message handler.
        '''

        h = handler.event.message(event.source.nick, event.target, event.arguments[0])
        self.handlers.on_message(h)

    def disconnect(self, message="See ya~"):
        self.connection.disconnect(msg)

    def get_version(self):
        return 'xbotpp %s' % xbotpp.__version__

    def start(self):
        '''\
        Start the bot, waiting for messages and calling the handler as necessary.
        '''

        self._connect()
        self.ircobj.process_forever()

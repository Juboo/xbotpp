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
        super(irc, self).__init__()

        debug.write('Initialized IRC protocol library.', debug.levels.Info)

        self.config = config
        self.state = state
        self.network = self.config['networks'][self.state['network']]
        self.channels = irclib_dict.IRCDict()
        self._nickname = self.network['nick']
        self._realname = self.config['bot']['owner']

        debug.write('Nickname: %s' % self._nickname, debug.levels.Info)
        debug.write('Realname: %s' % self._realname, debug.levels.Info)

        # Get hosts from the config and transform them into ServerSpec objects
        self.hosts = []
        serverpass = self.network['server_password'] if 'server_password' in self.network else None
        for host in [s.strip() for s in self.network['servers']]:
            host = host.split(":")
            self.hosts.append(ServerSpec(host[0], int(host[1]), serverpass))

        # add events
        _on_events = [
            'disconnect', 'join', 'kick', 'mode', 'namreply', 
            'nick', 'part', 'quit', 'nicknameinuse', 'welcome',
        ]

        for event in _on_events:
            self.connection.add_global_handler(event, getattr(self, '_on_' + event, None), -20)

        for event in ['privmsg', 'pubmsg', 'notice']:
            self.connection.add_global_handler(event, self.generic_message, -20)

    def _connect(self):
        server = self.hosts[0]
        try:
            debug.write('Connecting to %s...' % server, debug.levels.Info)
            self.connect(server.host, server.port, self._nickname, server.password, ircname=self._realname)
        except irclib_client.ServerConnectionError:
            debug.write('Error connecting to %s' % server, debug.levels.Info)

    def _on_disconnect(self, client, event):
        debug.write('Disconnected.', debug.levels.Info)
        self.channels = irclib_dict.IRCDict()

    def _on_join(self, client, event):
        channel = event.target
        nick = event.source.nick

        if nick == client.get_nickname():
            self.channels[channel] = irclib_bot.Channel()

        self.channels[channel].add_user(nick)
        handler.handlers.on_user_join(handler.event.user_join(nick))

    def _on_kick(self, client, event):
        nick = event.arguments[0]
        channel = event.target

        if nick == client.get_nickname():
            del self.channels[channel]
        else:
            self.channels[channel].remove_user(nick)

    def _on_mode(self, client, event):
        modes = irclib_modes.parse_channel_modes(" ".join(event.arguments))
        target = event.target
        if irclib_client.is_channel(target):
            channel = self.channels[target]
            for mode in modes:
                if mode[0] == "+":
                    f = channel.set_mode
                else:
                    f = channel.clear_mode
                f(mode[1], mode[2])
        else:
            pass

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

    def _on_nick(self, client, event):
        before = event.source.nick
        after = event.target
        for channel in self.channels.values():
            if channel.has_user(before):
                channel.change_nick(before, after)
        handler.handlers.on_user_change_nick(handler.event.user_change_nick(before, after))

    def _on_part(self, client, event):
        nick = event.source.nick
        channel = event.target

        if nick == client.get_nickname():
            del self.channels[channel]
        else:
            self.channels[channel].remove_user(nick)
            handler.handlers.on_user_part(handler.event.user_part(nick))

    def _on_quit(self, client, event):
        nick = event.source.nick
        for channel in self.channels.values():
            if channel.has_user(nick):
                channel.remove_user(nick)
        handler.handlers.on_user_part(handler.event.user_part(nick))

    def _on_nicknameinuse(self, client, event):
        debug.write('Nickname in use, appending an underscore.', debug.levels.Info)
        client.nick(client.get_nickname() + "_")

    def _on_welcome(self, client, event):
        debug.write('Connected, joining channels.', debug.levels.Info)
        for channel in [s.strip() for s in self.network['channels']]:
            client.join(channel)

    def generic_message(self, client, event):
        '''\
        Generic IRC message handler.
        '''

        h = handler.event.message(event.source.nick, event.target, event.arguments[0], event.type)
        handler.handlers.on_message(h)

    def disconnect(self, message="See ya~"):
        debug.write('Disconnecting: %s' % message, debug.levels.Info)
        self.connection.disconnect(message)

    def get_version(self):
        return 'xbot++ %s' % xbotpp.__version__

    def start(self):
        '''\
        Start the bot, waiting for messages and calling the handler as necessary.
        '''

        self._connect()
        self.ircobj.process_forever()

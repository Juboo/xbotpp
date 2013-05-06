# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import irc.bot
import irc.client
import datetime
import re
import signal
import traceback

from . import modules
from . import botio


class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        """\
        Initialize the bot, reading the configuration from `config`.

        :param config: bot configuration
        :type config: :py:class:`configparser.ConfigParser`
        """

        self.config = config
        self.prefix = config.get('bot', 'prefix')
        self.debug = False
        self.version = "v0.2.2"
        self.modules = modules.Modules(self)
        self.botio = botio.BotIO(self)

        if os.environ.get('READTHEDOCS', None) == 'True':
            self.config.set("bot", "skip_load", "True")

        if self.config.has_option("bot", "skip_load"):
            return None

        signal.signal(signal.SIGINT, self._goodbye)
        signal.signal(signal.SIGTERM, self._goodbye)

        self.modules.load_init(config.module_path)
        self._debug("Loaded commands: %s" % ". ".join(self.modules.modules['command']))

        hosts = []
        _hosts = [s.strip() for s in self.config.get(self.config.active_network, "servers").split(',')]

        for host in _hosts:
            host = host.split(":")
            hosts.append((host[0], int(host[1])))

        nick = self.config.get(self.config.active_network, "nick")
        realname = self.config.get("bot", "owner") if self.config.has_option("bot", "owner") else nick

        self._debug("Network: %s" % re.sub("network: ", "", self.config.active_network))
        self._debug("Servers: %s" % ", ".join(_hosts))
        self._debug("Nick: %s" % nick)
        self._debug("Realname: %s" % realname)

        irc.bot.SingleServerIRCBot.__init__(self, hosts, nick, realname)
        self.connection.add_global_handler('pubnotice', self.on_notice)
        self.connection.add_global_handler('privnotice', self.on_notice)

        LineBuffer = irc.buffer.DecodingLineBuffer
        LineBuffer.errors = 'replace'
        self.connection.buffer_class = LineBuffer

    def _log(self, buffer, mode=""):
        """\
        Log data to the bot's stdout.

        Log entries look like this::

            May 02 2013 05:50:46 <<< PING :wright.freenode.net

        The ``>>>`` in the text is determined by the `mode` parameter:

        - ``mode="out"`` makes this indicator ``>>>```
        - ``mode="in"`` makes this indicator ``<<<```
        - Any other mode makes this indicator ``---```

        The indicator is only shown on the first line of each log entry.

        The `buffer` argument can either be a string or a list of lines.
        """

        log = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")

        if mode == "out":
            _pad = ">>>"
        elif mode == "in":
            _pad = "<<<"
        else:
            _pad = "---"

        if isinstance(buffer, str):
            buffer = buffer.split("\n")

        for index, line in enumerate(buffer):
            print("%s %s %s" % (log, _pad if index == 0 else "   ", line))

    def _debug(self, message, event=None):
        """\
        Logs debug information to stdout, and if the `bot.debug` flag is enabled,
        sends it to the event source from the given event.
        """

        if self.debug and event:
            self.connection.notice(event.source, message)
        self._log(message)

    def get_version(self):
        """\
        Return the bot version.

        :rtype: str
        """

        return "xbotpp %s" % str(self.version)

    def on_nicknameinuse(self, client, event):
        client.nick(client.get_nickname() + "_")

    def on_welcome(self, client, event):
        for channel in [s.strip() for s in self.config.get(self.config.active_network, "channels").split(",")]:
            client.join(channel)

    def on_pubmsg(self, client, event):
        self._read(client, event)

    def on_privmsg(self, client, event):
        self._read(client, event)

    def on_notice(self, client, event):
        self._read(client, event)

    def on_all_raw_messages(self, client, event):
        self._log(event.arguments[0], "in")

    def _read(self, client, event):
        """\
        Call :py:func:`xbotpp.botio.BotIO.read` for any messages received,
        and handle exceptions that may be raised.
        """

        try:
            self.botio.read(client, event)
        except:
            error_message = "Traceback (most recent call last):\n" + '\n'.join(traceback.format_exc().split("\n")[-4:-1])
            self._debug(error_message, event=event)

    def _action(self, event):
        self._debug("Action: %s" % event.arguments[0], event=event)

    def _goodbye(self):
        self.die("See ya~")

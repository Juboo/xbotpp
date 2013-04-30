import io
import os
import sys
import inspect
from xbotpp.modules import Modules
from xbotpp.botio import BotIO
from configparser import ConfigParser


class Bot:
    def __init__(self):
        self.modules = Modules(self)
        self.modules.load_init(os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), "testmodules"))

        self.botio = BotIO(self)
        self.config = ConfigParser()
        self.config.readfp(self.defaultconfig())
        self.prefix = self.config.get("bot", "prefix")

    def defaultconfig(self):
        return io.StringIO("[bot]\nprefix=!")    

    def _debug(self, msg, event=None):
        #print("DEBUG: %s (event=%s)" % (msg, type(event)), file=sys.stderr)
        pass

    def _log(self, msg, event=None):
        self._debug(msg, event)

class IrcClient:
    def __init__(self):
        self.messagebuffer = []

    def privmsg(self, target, msg):
        self.messagebuffer.append((target, msg))

class IrcEventSource:
    def __init__(self):
        self.nick = ""

class IrcEvent:
    def __init__(self):
        self.arguments = []
        self.target = ""
        self.source = IrcEventSource()


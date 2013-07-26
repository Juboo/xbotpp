__xbotpp_module__ = "core"

import sys
import platform
import xbotpp.debug
import xbotpp.modules


@xbotpp.modules.on_command('echo')
def echo(info, args, buf):
    if buf != "":
        r = buf.split()
    else:
        r = args

    if r[0] == '/me':
        return '\x01ACTION {}\x01'.format(' '.join(r[1:]))
    else:
        return ' '.join(r)

@xbotpp.modules.on_command('info')
def info(info, args, buf):
    """Return information on the bot.
    """

    infostr = " ".join([
        "I'm {nick}, running xbot++ {version} on {platform} under",
        "Python {pyver}, with {num_modules} module{module_plural} and",
        "{num_event_handlers} event handler{event_plural} registered."
    ])

    # Count event handlers
    ev = 0
    for b in xbotpp.handler.handlers.dispatch:
        ev += len(xbotpp.handler.handlers.dispatch[b])

    formatters = {
        'nick': xbotpp.state.connection.get_nickname(),
        'version': xbotpp.__version__,
        'platform': platform.platform(terse=True),
        'num_modules': len(xbotpp.state.modules.loaded),
        'module_plural': '' if len(xbotpp.state.modules.loaded) is 1 else 's',
        'num_event_handlers': ev,
        'event_plural': '' if ev is 1 else 's',
        'pyver': '{0} {1}'.format(".".join([str(s) for s in platform.python_version_tuple()]), sys.version_info[3]),
    }

    return infostr.format(**formatters)


@xbotpp.modules.on_command('list')
def command_list(info, args, buf):
    """Return a list of commands.
    """

    if len(args) >= 1:
        level = int(args[0])
    else:
        level = 0

    b = []
    for s in xbotpp.state.modules.commands:
        if xbotpp.state.modules.commands[s]['privlevel'] <= level:
            b.append(s)

    return "Available commands: {}".format(", ".join(b))

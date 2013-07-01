# vim: noai:ts=4:sw=4:expandtab:syntax=python
__xbotpp_module__ = "core"

import sys
import xbotpp.debug
import xbotpp.modules


@xbotpp.modules.on_event('message')
def test_event_handler(event):
    xbotpp.debug.write(repr(event))

@xbotpp.modules.on_command('info')
def info(info, args, buf):
    """Return information on the bot.
    """
    
    infostr = " ".join([
        "I'm {nick}, running xbot++ {version} on Python {pyver}, ",
        "with {num_modules} module{module_plural} and {num_event_handlers} event handler{event_plural} registered."
    ])

    # Count event handlers
    ev = 0
    for b in xbotpp.handler.handlers.dispatch:
        ev += len(xbotpp.handler.handlers.dispatch[b])

    formatters = {
        'nick': xbotpp.state['connection'].get_nickname(),
        'version': xbotpp.__version__,
        'num_modules': len(xbotpp.state['modules_monitor'].loaded),
        'module_plural': '' if len(xbotpp.state['modules_monitor'].loaded) is 1 else 's',
        'num_event_handlers': ev,
        'event_plural': '' if ev is 1 else 's',
        'pyver': ".".join([str(s) for s in sys.version_info[0:3]]),
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
    for s in xbotpp.state['modules_monitor'].commands:
        if xbotpp.state['modules_monitor'].commands[s]['privlevel'] <= level:
            b.append(s)

    return "Available commands: {}".format(", ".join(b))


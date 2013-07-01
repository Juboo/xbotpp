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
    '''\
    Return information on the bot.
    '''
    
    infostr = " ".join([s.strip() for s in '''\
    I'm {nick}, running xbot++ {version} on Python {pyver}, 
    with {num_modules} module{module_plural} and {num_event_handlers} event handler{event_plural} registered.
    '''.split('\n')])

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
    '''\
    Return a list of commands.
    '''

    return "Available commands: {}".format(", ".join([s for s in xbotpp.state['modules_monitor'].commands]))

@xbotpp.modules.on_command('reload', 1)
def reload_command(info, args, buf):
    loaded = 0
    failed = []

    for module in args:
        try:
            if module in xbotpp.state['modules_monitor'].loaded:
                xbotpp.state['modules_monitor'].loaded[module]['reload'] = True
            xbotpp.state['modules_monitor'].load(module)
            loaded += 1
        except xbotpp.modules.error.ModuleLoadingException:
            failed.append(module)

    failstr = "Failed: " + ", ".join(failed)
    return "Reloaded {0} of {1} modules. {2}".format(loaded, len(args), failstr if failed != [] else '')

@xbotpp.modules.on_command('unload', 1)
def unload_command(info, args, buf):
    loaded = 0
    failed = []

    for module in args:
        try:
            xbotpp.state['modules_monitor'].unload(module)
            loaded += 1
        except:
            failed.append(module)

    failstr = "Failed: " + ", ".join(failed)
    return "Unloaded {0} of {1} modules. {2}".format(loaded, len(args), failstr if failed != [] else '')

@xbotpp.modules.on_command('modlist', 1)
def modlist_command(info, args, buf):
    '''\
    Return a list of loaded modules, their event handlers and their registered commands.
    '''

    b = []
    for mod in xbotpp.state['modules_monitor'].loaded:
        sidlist = []
        for sid in xbotpp.state['modules_monitor'].loaded[mod]['events']:
            event = getattr(xbotpp.state['modules_monitor'].loaded[mod]['events'][sid][1], '__xbotpp_event__', None)
            sidlist.append("{0} [{1}, {2}]".format(sid, xbotpp.state['modules_monitor'].loaded[mod]['events'][sid][0], event))

        commandlist = []
        for command in xbotpp.state['modules_monitor'].commands:
            if xbotpp.state['modules_monitor'].commands[command]['module'] == mod:
                commandlist.append(command)

        sid = ", ".join(sidlist) if sidlist != [] else 'none'
        cmd = ", ".join(commandlist) if commandlist != [] else 'none'
        b.append("{0} - events: {1}; commands: {2}".format(mod, sid, cmd))

    del mod
    return "\n".join(b)


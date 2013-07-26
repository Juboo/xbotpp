__xbotpp_module__ = "admin"

import xbotpp.debug
import xbotpp.modules


@xbotpp.modules.on_command('rehash', 1)
def rehash_command(info, args, buf):
    xbotpp.load_config()
    return "Done."

@xbotpp.modules.on_command('saveconf', 1)
def saveconf_command(info, args, buf):
    xbotpp.save_config()
    return "Done."

@xbotpp.modules.on_command('reload', 1)
def reload_command(info, args, buf):
    loaded = 0
    failed = []
    returnbuffer = []

    for module in args:
        try:
            if module in xbotpp.state.modules.loaded:
                xbotpp.state.modules.loaded[module]['reload'] = True
            xbotpp.state.modules.load(module)
            loaded += 1
        except xbotpp.modules.error.ModuleLoadingException as e:
            failed.append(module)
            returnbuffer.append("Loading {m}: {e}".format(m=module, e=e))

    failstr = "Failed: " + ", ".join(failed)
    returnbuffer.insert(0, "Reloaded {0} of {1} modules. {2}".format(loaded, len(args), failstr if failed != [] else ''))
    return '\n'.join(returnbuffer)


@xbotpp.modules.on_command('unload', 1)
def unload_command(info, args, buf):
    """Unload the modules given as arguments.
    """

    loaded = 0
    failed = []

    for module in args:
        try:
            xbotpp.state.modules.unload(module)
            loaded += 1
        except:
            failed.append(module)

    failstr = "Failed: " + ", ".join(failed)
    return "Unloaded {0} of {1} modules. {2}".format(loaded, len(args), failstr if failed != [] else '')


@xbotpp.modules.on_command('modlist', 1)
def modlist_command(info, args, buf):
    """ Return a list of loaded modules, their event handlers and their registered commands.
    """

    b = []
    for mod in xbotpp.state.modules.loaded:
        sidlist = []
        for sid in xbotpp.state.modules.loaded[mod]['events']:
            event = getattr(xbotpp.state.modules.loaded[mod]['events'][sid][1], '__xbotpp_event__', None)
            sidlist.append("{0} [{1}, {2}]".format(sid, xbotpp.state.modules.loaded[mod]['events'][sid][0], event))

        commandlist = []
        for command in xbotpp.state.modules.commands:
            if xbotpp.state.modules.commands[command]['module'] == mod:
                commandlist.append(command)

        sid = ", ".join(sidlist) if sidlist != [] else 'none'
        cmd = ", ".join(commandlist) if commandlist != [] else 'none'
        b.append("{0} - events: {1}; commands: {2}".format(mod, sid, cmd))

    del mod
    return "\n".join(b)


@xbotpp.modules.on_command('eval', 1)
def eval_command(info, args, buf):
    """Evaluate a given Python string.
    """
    return str(eval(" ".join(args)))

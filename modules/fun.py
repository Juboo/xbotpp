# vim: noai:ts=4:sw=4:expandtab:syntax=python
__xbotpp_module__ = "fun"

import xbotpp
import xbotpp.modules


@xbotpp.modules.on_command('choose')
def choose(info, args, buf):
    import random
    args_ = list(set(' '.join([arg.lower() if arg.lower() == 'or' else arg for arg in args[1:]]).split(' or ')))
    args__ = list(set([arg.lower() for arg in args_]))
    if len(args_) > 1 and len(args_) == len(args__):
        ans = random.choice([
            'Defs', 'Totes', 'I reckon', 'Why not', 'I like *', 'DEFINITELY',
            'Without a doubt', 'Always', 'A must-choose: *', 'You could ^',
            'I recommend *', 'Perhaps', 'Blimey,', 'How about *', 'HAHA,',
            'I say', 'Something tells me', 'Try *', 'Go with *', 'I highly recommend *'
        ])
        choice = random.choice(args_)
        intermediary = "choose " if random.random() > 0.5 else ''
        if '*' in ans:
            intermediary = ''
            ans = ans[:-2]
        elif '^' in ans:
            intermediary = "choose "
            ans = ans[:-2]
        if choice.endswith("?") and len(choice) > 1:
            choice = choice[:-1]
        return "%s %s%s." % (ans, intermediary, choice)
    else:
        return "{0}choose <item 1> or <item 2> [or <item n>] where 1 != 2 != n".format(xbotpp.config['bot']['prefix'])


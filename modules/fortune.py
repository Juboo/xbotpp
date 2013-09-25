__xbotpp_module__ = "fortune"

# Requires BSD's fortune-mod

import xbotpp
import xbotpp.modules

@xbotpp.modules.on_command('fortune')
def fortune(info, args, buf):
  import subprocess
  if len(args) > 0:
    if args[0] == 'nsfw' or args[0] == 'n':
      x = subprocess.check_output(["fortune", "-o"])  # An offensive fortune
      return x
    elif args[0] == 'any' or args[0] == 'a':
      x = subprocess.check_output(["fortune", "-a"])  # Any fortune
      return x
    else:
      return "{0}fortune [(h)elp | (a)ny | (n)sfw]"
  else:
    x = subprocess.check_output("fortune")
    return x

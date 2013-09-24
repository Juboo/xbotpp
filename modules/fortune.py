__xbotpp_module__ = "fortune"

# Do it: yaourt -S fortune-mod

import xbotpp
import xbotpp.modules

@xbotpp.modules.on_command('fortune')
def fortune(info, args, buf):
  import subprocess
  args_ = list(set([arg.lower()]))
  if len(args_) > 1:                                                                 # If any arguments are present it
    x = subprocess.Popen(["fortune", "-o"], stdout=subprocess.PIPE).communicate()[0] # prints an offensive fortune! >:D
    return x
  else:
    x = subprocess.Popen("fortune", stdout=subprocess.PIPE).communicate()[0]
    return x

# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import xbotpp.handler
from xbotpp.ptr import ptr

class botio:
    def __init__(self, config, state):
        self.config = config
        self.state = state

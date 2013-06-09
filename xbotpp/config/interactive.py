# vim: noai:ts=4:sw=4:expandtab:syntax=python

import os
import re
import sys
import json
import argparse

'''Interactive utility to create an xbot++ config.'''

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Interactive utility to create an xbot++ config.')
    parser.add_argument('-f', '--file', metavar='OUTPUT', help='file to write config to, default config.json', default='config.json')
    return parser.parse_args(args)

def main(options=None):
    options = options or parse_args()
    print("Not done yet.")

if __name__ == "__main__":
    main()
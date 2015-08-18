#!/usr/bin/python

import argparse
import logging
import os
import yaml
import tty
import sys
import termios
import datetime

global config

def merge(x,y):
    # store a copy of x, but overwrite with y's values where applicable
    merged = dict(x,**y)

    xkeys = x.keys()

    # if the value of merged[key] was overwritten with y[key]'s value
    # then we need to put back any missing x[key] values
    for key in xkeys:
        # if this key is a dictionary, recurse
        if isinstance(x[key],dict) and y.has_key(key):
            merged[key] = merge(x[key],y[key])

    return merged

class Menu(object):
    def __init__(self):
        self.title = ""
        self.options = {}
        self.quitting = False

    def render(self):
        while not self.quitting:
            print ""

            # Render title
            print self.title
            print "=" * len(self.title)

            # Render options
            for key, value in self.options.iteritems():
                print "(%s) %s" % (
                    key.upper(),
                    str(value),
                )

            # Render common options
            print "(Q) Quit"

            self.prompt()

    def prompt(self, getch = True, title = '', prompt = '>', prefill = ''):
        # Read input
        print prompt,
        print " ",
        if getch:
            selection = self.getch()
            print "\n"
            return self.handle_input(selection)
        else:
            selection = raw_input("%s [%s] %s " % (
                title,
                prefill,
                prompt
            )) or prefill
            return selection

    def handle_input(self, selection):
        if selection in ['q','Q']:
            self.quitting = True
        elif selection.lower() in [k.lower() for k in self.options.keys()]:
            if self.options[selection.lower()] in globals().keys():
                globals()[self.options[selection.lower()]]().render()
            else:
                print "%s not implemented..." % str(self.options[selection.lower()])

    def getch(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__()
        self.title = "Main Menu"
        self.options = {
            'b': 'BodyMenu',
            'l': 'LiftingMenu',
        }

class BodyMenu(Menu):
    def __init__(self):
        super(BodyMenu, self).__init__()
        self.title = "Body"
        self.options = {
            'w': 'WeightEntry',
            'f': 'FatEntry',
        }

class Entry(Menu):
    def __init__(self):
        super(Entry, self).__init__()
        self.title = "Entry"
        self.url_base = "http://localhost:5000"
        self.url = ""
        self.items = {}

    def render(self):
        print self.title
        print '=' * len(self.title)
        data = {}
        for item, default in self.items.iteritems():
            data[item] = super(Entry, self).prompt(getch = False,title = item,prefill = default)
        self.submit(data)

    def submit(self, data = {}):
        print "Submitting %s to %s..." % (
            str(data),
            str(self.url_base) + str(self.url),
        )

class WeightEntry(Entry):
    def __init__(self):
        super(WeightEntry, self).__init__()
        self.title = "Weight Entry"
        self.url = "/body/weight"
        self.items = {
            'weight': '',
            'datetime': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        }

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process command line options.')
    parser.add_argument('-d','--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-c','--config', help='Specify a config file to use',
                        type=str, default='config.yaml')
    parser.add_argument('--version', action='version', version='0')
    args = parser.parse_args()

    # Setup logging options
    log_level = logging.DEBUG if args.debug else logging.INFO
    log = logging.getLogger(os.path.basename(__file__))
    log.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(funcName)s(%(lineno)i):%(message)s')

    ## Console Logging
    if args.debug:
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        log.addHandler(ch)

    ## File Logging
    fh = logging.FileHandler(os.path.basename(__file__) + '.log')
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    log.info("Initializing...")

    log.info("Loading configuration...")
    # Load Config
    global config
    defaults = {
        "url": "http://localhost:5000",
    }
    if os.path.isfile(args.config):
        log.debug("Loading config file %s" % args.config)
        config = yaml.load(file(args.config))
        if config:
            # config contains items
            config = merge(defaults,yaml.load(file(args.config)))
            log.debug("Config merged with defaults")
        else:
            # config is empty, just use defaults
            config = defaults
            log.debug("Config file was empty, loaded config from defaults")
    else:
        log.debug("Config file does not exist, creating a default config...")
        config = defaults

    log.debug("Config loaded as:\n%s, saving this to disk" % str(config))
    with open(args.config, 'w') as outfile:
        outfile.write( yaml.dump(config, default_flow_style=False) )
    log.debug("Config loaded as:\n%s" % str(config))

    log.info("Initialization complete")

    MainMenu().render()

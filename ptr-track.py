#!/usr/bin/python

import argparse
import logging
import os
import yaml
import tty
import sys
import termios

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

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

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

    quitting = False

    while not quitting:
        # Render menu
        print "\nMain"
        print "===="
        print "(B)ody"
        print "(L)ifting"
        print "> ",

        user_input = getch().lower()
        
        if user_input in ['b']:
            print "\nBody"
            print "===="
            print "(W)eight"
            print "(F)at"
            print "> ",
            user_input = getch().lower()

            if user_input in ['w']:
                print "\n"
            elif user_input in ['f']:
                print "\n"
        elif user_input in ['l']:
            print "\n"

        quitting = True


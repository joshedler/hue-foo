#! /usr/bin/env python3

import re
import sys
import os

from colorama import init
from termcolor import colored

import argparse
import json

from socket import gaierror, error as socket_error
from phue import Bridge, PhueRequestTimeout, PhueRegistrationException

def bright(msg, color):
    return colored(msg, color, attrs=['bold'])
def bright_red(msg):
    return bright(msg, 'red')
def bright_yellow(msg):
    return bright(msg, 'yellow')
def bright_cyan(msg):
    return bright(msg, 'cyan')
def bright_green(msg):
    return bright(msg, 'green')

# Define a context manager to suppress stdout and stderr.
# SOURCE: https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in 
    Python, i.e. will suppress all print, even if the print originates in a 
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).      

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)

# initialize colorama
init()

print()
print(bright_red('=== Hue Foo Setup ==='))
print()

user_settings_file = os.path.join(os.path.expanduser('~'), ".python_hue")

hue_bridge = None

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--hue', help='The hostname or IP address of your Hue Bridge.' )
args = arg_parser.parse_args()

if args.hue:
    hue_bridge = args.hue
    print(bright_cyan('User specified Hue Bridge address: {}'.format(hue_bridge)))

if hue_bridge is None:    
    if not os.path.isfile(user_settings_file):
        print(bright_yellow('User settings file not found. Entering interactive mode for new settings.'))
        hue_bridge = input('Enter the hostname or IP address of your Hue Bridge: ')
    else:
        print(bright_cyan('Loading user settings...'))

        # the phue config file (~/.python-hue) is a bit wonky and not easy for use via straight JSON
        # TODO: this only grabs the first configured address; need to handle multiples!
        with open(user_settings_file, 'r') as f:
            s = f.read()        # read the whole file into s

        m = re.search('{"([^"]+)"', s)

        if m:
            hue_bridge = m.group(1)

try:
    with suppress_stdout_stderr():
        b = Bridge(hue_bridge)
except (gaierror, socket_error, PhueRequestTimeout):
    print(bright_red('ERROR: An error occurred connecting to the Hue Bridge at address "{}". Please ensure this value is correct.'.format(hue_bridge)))
    print(bright_red('Run "{} --setup" to re-run setup.'.format(sys.argv[0])))
    exit(1)
except PhueRegistrationException:
    print(bright_red('ERROR: The link button of the Hue Bridge at address {} has not been pressed in the last 30 seconds.'.format(hue_bridge)))
    print(bright_red('Press the button and run "{} --hue {}" again.'.format(sys.argv[0], hue_bridge)))
    exit(1)

print()
print(bright_green('SUCCESS!'))
print(bright_green('You are setup to interact with the Hue Bridge at address {} with the hue-foo scripts!'.format(hue_bridge)))
print()


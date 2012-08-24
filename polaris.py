#!/usr/bin/env python
"""
polaris.py
"""

import sys
import os
import fcntl
import argparse
#import signal
#import atexit
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop


def find_polaris():
    for include_dir in [os.environ.get('POLARIS_HOME', None), '', os.path.dirname(__file__)]:
        if include_dir is not None and os.path.isfile(os.path.realpath(os.path.join(include_dir, 'polaris', '__init__.py'))):
            sys.path.insert(0, include_dir)
            return True
    return False

if not find_polaris():
    raise Exception("Cannot find 'polaris' source.")


from polaris import PolarisManager
from polaris.dzen import Dzen2
from polaris.util import import_file, dict_sum


DEFAULT_CONFIG = {
    'dzen2': {
        'path': '/usr/bin/dzen2',
        'args': '-ta l -h 12',
        'font': 'droid sans:bold:size=10',
    },
    'General': {},
    'Workspaces': {},
    'Clock': {},
    'Tasks': {},
}


if __name__ == "__main__":
    config = DEFAULT_CONFIG.copy()
    for config_dir in [os.path.expanduser('~/.polaris/'),
                       os.path.join(os.path.dirname(__file__), os.path.pardir)]:
        config_file = os.path.join(config_dir, 'config.py')
        try:
            polaris_config = import_file(config_file)
            config = dict_sum(config, getattr(polaris_config, 'config'))
            config['loaded'] = True
            break
        except:
            pass
    if not config.get('loaded'):
        raise Exception("Could not find config file. Please copy the" +
                        " example config to '~/.polaris/config.py")

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", nargs="+", dest="toggled_window")
    parser.add_argument("-w", nargs="+", dest="workspace")
    args = parser.parse_args()

    if args.toggled_window or args.workspace:
        try:
            polarisservice = dbus.SessionBus().get_object('org.polaris.service', '/org/polaris/service')
        except:
            print "polaris: dbus service not found"
            sys.exit(0)
        if args.toggled_window is not None:
            toggle_window = polarisservice.get_dbus_method('toggle_window', 'org.polaris.service')
            returnval = toggle_window(str(args.toggled_window[0]))
            sys.exit(returnval)
        elif args.workspace is not None:
            switch_workspace = polarisservice.get_dbus_method('switch_workspace', 'org.polaris.service')
            returnval = switch_workspace(str(args.workspace[0]))
            sys.exit(returnval)

    pid_file = config.get('pid_file', "/tmp/polaris.pid")
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except:
        sys.exit(0)

    #atexit.register(cleanup)

    dzen_args = config['dzen2']['args'].split()
    dzen = Dzen2(*dzen_args, **config['dzen2'])

    DBusGMainLoop(set_as_default=True)
    PolarisManager(config, dzen.pipe)
    loop = gobject.MainLoop()
    loop.run()

##
## Polaris config file
##   This is a python file, so you have a bit of responsibility to not put junk
##   in here.
##

import os

config = {
    'General': {
        'dzen2_args': '-ta l -h 12',
        'seperator': {'fg': '#808080'},
    },
    'Workspaces': {
        'normal': {'bg': '#000000', 'fg': '#707070'},
        'active': {'bg': '#202020', 'fg': '#0095ff'},
    },
    'Tasks': {
        'active': {'bg': '#050505', 'fg': '#eeeeee'},
        'normal': {'bg': '#000000', 'fg': '#808080'},
        'iconiz': {'bg': '#000000', 'fg': '#606060'},
    },
    'Clock': {
        'strftime': '%H:%M',
        'clock_fg': 'ffffff',
    },
}

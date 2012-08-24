##
## Polaris config file
##   This is a python file, so you have a bit of responsibility to not put junk
##   in here.
##
import os

config = {
    'dzen2': {
        'path': os.path.expanduser('~/.bin/dzen2.real'),
        'args': '-ta l -expand n -h 13 -w 600 -x 400 -y 0',
        'font': 'Droid Sans:bold:size=10',
        'font_p': 'Envy Code R for Powerline:bold:size=10'
    },

    'General': {
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
        'strftime': '%I:%M%P',
        'fg': '#ffffff',
    },
}

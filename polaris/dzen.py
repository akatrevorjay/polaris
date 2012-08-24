
import sys
import os
import subprocess

#self.DZEN2_FONT_EMBED = '{name}:{weight}:size={size}' % config['dzen2']['font']

class Dzen2(object):
    pid = 0
    def __init__(self, *args, **kwargs):
        invocation = [kwargs['path'],
                             '-p', '-fn', kwargs['font'],
                             ]
        invocation.extend(args)
        invocation = [str(x) for x in invocation]
        self.pipe = subprocess.Popen(invocation,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     close_fds=True)
        self.pid = self.pipe.pid

    def is_running(self):
        """ Checks if this instance is still running """
        print "PID:", self.pid
        if not os.path.exists("/proc/"+str(self.pid)):
            sys.exit(0)
        return True

    def __exit__(self):
        if self.is_running():
            os.kill(self.pid, 15)

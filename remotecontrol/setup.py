from __future__ import absolute_import

import atexit
import functools

from . import server
from . import interpreter


def setup(app_name, atexit_register=atexit.register, **kwargs):

    """Non-standalone user setup."""
    
    import os
    import sys

    base = '/var/tmp/rc.%s.%s' % (app_name, os.getpid())

    sock1 = base + '.cmdsock'
    if os.path.exists(sock1):
        os.unlink(sock1)
    sock2 = base + '.pysock'
    if os.path.exists(sock2):
        os.unlink(sock2)

    server.spawn(sock1, **kwargs)

    # Run the interpreter in the main Python namespace, so you get the same
    # experience as using the Python console in the GUI app itself.
    import __main__
    interpreter.spawn(sock2, __main__.__dict__, **kwargs)

    @atexit_register
    def shutdown_remotecontrol():
        if os.path.exists(sock1):
            os.unlink(sock1)
        if os.path.exists(sock2):
            os.unlink(sock2)


def setup_maya():
    # atexit doesn't work, so we hook onto Maya's shutdown
    from maya import cmds
    setup('maya', lambda func: cmds.scriptJob(event=('quitApplication', func)))

def setup_houdini():
    setup('houdini')
    return

    # This *might* be required.
    import hdefereval
    def call_in_main_thread(func, *args, **kwargs):
        return hdefereval.executeInMainThreadWithResult(functools.partial(func, *args, **kwargs))
    setup('houdini', call_in_main_thread=hdefereval.call_in_main_thread)

def setup_nuke():
    setup('nuke')

def setup_rv():
    setup('rv')

def setup_mari():
    setup('mari')


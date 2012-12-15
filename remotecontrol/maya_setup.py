from __future__ import absolute_import

# All imports should be in a function so that they do not polute the global
# namespace, except for `from maya import cmds` because we want that everywhere.
from maya import cmds, mel, OpenMaya


def standard_setup():
    """Non-standalone user setup."""
    
    import os
    import tempfile
    import datetime
    import sys

    base = '/var/tmp/maya.%s' % os.getpid()

    sock1 = base + '.cmdsock'
    try:
        import remotecontrol.server
    except ImportError:
        cmds.warning('Could not import remotecontrol.server.')
    else:
        if os.path.exists(sock1):
            os.unlink(sock1)

        # Do not pass in namespaces so that each command connection is
        # clean.
        remotecontrol.server.spawn(sock1)

    sock2 = base + '.pysock'
    try:
        import remotecontrol.interpreter
    except ImportError:
        cmds.warning('Could not import remotecontrol.interpreter.')
    else:
        if os.path.exists(sock2):
            os.unlink(sock2)

        # Pass globals() so it runs in the main Python namespace.
        remotecontrol.interpreter.spawn(sock2, globals())


    # Tear it down later. (This only seems to work in 2013.)
    def close_command_port():

        try:
            if os.path.exists(sock1):
                os.unlink(sock1)
        except Exception as e:
            sys.__stdout__.write('%s while unlinking %s: %s\n' % (e.__class__.__name__, sock1, e))

        try:
            if os.path.exists(sock2):
                os.unlink(sock2)
        except Exception as e:
            sys.__stdout__.write('%s while unlinking %s: %s\n' % (e.__class__.__name__, sock2, e))
    
    cmds.scriptJob(event=('quitApplication', close_command_port))


# Block from running the production userSetup if the dev one already ran.
if not globals().get('__remotecontrol_usersetup__'):
    __remotecontrol_usersetup__ = True

    # Most things should not run in batch mode.
    if not cmds.about(batch=True):
        standard_setup()


# Cleanup the namespace.
del standard_setup

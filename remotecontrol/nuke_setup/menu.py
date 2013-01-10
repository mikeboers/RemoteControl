from __future__ import absolute_import

# All imports should be in a function so that they do not polute the global namespace.


def standard_setup():
    """Non-standalone user setup."""
    
    import os
    import sys
    import atexit

    import nuke
    
    base = '/var/tmp/nuke.%s' % os.getpid()

    sock1 = base + '.cmdsock'
    try:
        import remotecontrol.server
    except ImportError:
        nuke.warning('Could not import remotecontrol.server.')
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
        nuke.warning('Could not import remotecontrol.interpreter.')
    else:
        if os.path.exists(sock2):
            os.unlink(sock2)

        # Pass globals() so it runs in the main Python namespace.
        remotecontrol.interpreter.spawn(sock2, globals())


    # Tear it down later.
    @atexit.register
    def close_remote_controls():

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
    


# Block from running the production init if the dev one already ran.
if not globals().get('__remotecontrol_menu__'):
    __remotecontrol_menu__ = True
    standard_setup()


# Cleanup the namespace.
del standard_setup

import atexit


def setup():
    """Non-standalone user setup."""
    
    import os
    import sys

    base = '/var/tmp/mari.%s' % os.getpid()

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
    @atexit.register
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
    

- Have another thread just watching for when the socket closes, and then force the execution to stop.

- Use a Python thread and socket server to handle our command ports.
    - Then we can carry it straight to Nuke.

- Unify the various (mari, nuke, houdini, rv, maya) setup scripts as much as
  possible.

- Convert the remotecontrol bin into an entry_point console_script(s).

- Use argparse instead of optparse

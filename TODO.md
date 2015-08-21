- Rewrite for co-operative multitasking.
    - could use a greenlet and replace sock.recv with something that
      does not block, insteads yields control
    - OR, since we can almost trivially write our own readline and write
      wrapper which is co-operative
    - OR hook our sockets into the event loop via QSocketNotifier

- Make stdio wrapper check the current thread id to make sure it is the one
  that should be captured

- Have another thread just watching for when the socket closes, and then force the execution to stop.

- Use a Python thread and socket server to handle our command ports.
    - Then we can carry it straight to Nuke.

- Unify the various (mari, nuke, houdini, rv, maya) setup scripts as much as
  possible.

- Convert the remotecontrol bin into an entry_point console_script(s).

- Use argparse instead of optparse

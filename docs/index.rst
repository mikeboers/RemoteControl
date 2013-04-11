.. _index:

remotecontrol
=============

This Python package allows you to embed an interactive interpreter, or REPL_, into your Python programs.

It was initially conceived to allow for remote access to long running processes such as web servers, but was adapted to work with long running GUI processes that have a Python API (e.g. Maya_ and Nuke_). It was further expanded to have an API for other processes to interact with directly.

.. _repl: http://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop
.. _maya: http://www.autodesk.com/products/autodesk-maya/overview
.. _nuke: http://www.thefoundry.co.uk/products/nuke/

.. warning:: This does not have any access controls whatsoever, and allows the
    user to execute arbitrary code.


Quickstart
----------

Spawn an interpreter to listen on a socket::

    >>> import remotecontrol.interpreter
    >>> thread = remotecontrol.interpreter.spawn(('', 12345))

There is a now an interactive interpreter server listening to port 12345, and ``thread`` contains the :class:`~python:threading.Thread` that it is running in.

You can connect to it and use it like a the standard Python prompt, via::

    $ ./bin/remotecontrol localhost 12345
    Python 2.7.2 (default, Oct 11 2012, 20:14:37) 
    <snip>
    >>> print "I am remote!"
    I am remote!

In this setup, multiple clients can connect simultaneously and each will operate in an isolated (and temporary) namespace.


Contents
-------------

.. toctree::
    :maxdepth: 2

..
    interpreter
    command_port

.. todo:: Write more docs.
    

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


import logging
import sys

try:
    from uitools.threads import call_in_main_thread

except ImportError:

    def call_in_main_thread(func, *args, **kwargs):
        if not call_in_main_thread._warned:
            call_in_main_thread._warned = True
            print >> sys.stderr, 'uitools not installed; naively running code'
        return func(*args, **kwargs)

    call_in_main_thread._warned = False

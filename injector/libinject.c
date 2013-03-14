// #include <Python.h>
#include <stdio.h>
#include <stdlib.h>

void remotecontrol_py_init(void) {

    fprintf(stderr, "Hello\n");
    fprintf(stdout, "Hello\n");
    exit(123);
    return;

    // This is safe to call several times.
    // Py_Initialize();

    // PyRun_SimpleString(
    //     "from time import time,ctime\n"
    //     "print 'Today is',ctime(time())\n"
    // );

}


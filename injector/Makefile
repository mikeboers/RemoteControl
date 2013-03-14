.PHONY: default build clean

default: build

build: libinject.so

%.o: %.c
	gcc -c -o $@ $<

libinject.so: libinject.o
	gcc -o $@ -shared $<

clean:
	-rm *.so *.o

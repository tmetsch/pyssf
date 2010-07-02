
CC = gcc
LSF_LIBDIR = /opt/lsf/7.0/linux2.6-glibc2.3-x86_64/lib
PYTHON_LIBDIR = /usr/include/python2.6

PROJECT = _lsf.so
OBJECTS = lsf_wrap.o

CFLAGS  = -fPIC -I$(PYTHON_LIBDIR)
LDFLAGS = $(LSF_LIBDIR)/liblsf.a $(LSF_LIBDIR)/libbat.a $(LSF_LIBDIR)/libfairshareadjust.so $(LSF_LIBDIR)/liblsbstream.so -lc -lnsl

all: $(PROJECT)

.c.o:
	$(CC) $(CFLAGS) -c $<

$(PROJECT): swig $(OBJECTS)
	ld -shared $(OBJECTS) -o $(PROJECT) $(LDFLAGS)

swig:
	swig -python lsf.i

clean:
	rm -rf _lsf.so lsf.py lsf.pyc lsf_wrap.c lsf_wrap.o

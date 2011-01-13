# 
# Copyright (C) 2010-2011 Platform Computing
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
# 

CC = gcc
LSF_LIBDIR = /opt/lsf/7.0/linux2.6-glibc2.3-x86/lib
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

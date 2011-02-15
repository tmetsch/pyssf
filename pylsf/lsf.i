/*
 * 
 * Copyright (C) 2010-2011 Platform Computing
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
 * 
 */


/* File: lsf.i */
%module lsf

%{
#define SWIG_FILE_WITH_INIT
#include "/opt/platform/lsf/8.0/include/lsf/lsf.h"
#include "/opt/platform/lsf/8.0/include/lsf/lsbatch.h"
%}

%ignore ls_placeoftype;
%ignore ls_loadoftype;
%ignore ls_lostconnection;
%ignore ls_gethostrespriority;
%ignore ls_verrlog;
%ignore getBEtime;
%ignore ls_nioinit;
%ignore ls_nioselect;
%ignore ls_nioctl;
%ignore ls_nionewtask;
%ignore ls_nioremovetask;
%ignore ls_niowrite;
%ignore ls_nioclose;
%ignore ls_nioread;
%ignore ls_niotasks;
%ignore ls_niostatus;
%ignore ls_niokill;
%ignore ls_niosetdebug;
%ignore ls_niodump;
%ignore ls_readrexlog;

// howto handle char **
%typemap(in) char ** {
    int size = PyList_Size($input);
    int i = 0;
    $1 = (char **) malloc((size+1)*sizeof(char *));
    for (i = 0; i < size; i++) {
      PyObject *o = PyList_GetItem($input,i);
      $1[i] = PyBytes_AsString(PyUnicode_AsUTF8String(PyList_GetItem($input,i)));
    }
    $1[i] = 0;
}

// cleanup of char **
%typemap(freearg) char ** {
  free((char *) $1);
}

// typemap for time_t
%typemap(in) time_t {
    $1 = (time_t) PyLong_AsLong($input);
}

%typemap(out) time_t {
    $result = PyLong_FromLong((long)$1);
}

%typemap(freearg) time_t {
    free((time_t *) $1);
}

// handle int arrays in struct...
%typemap(in) int [ANY] (int temp[$1_dim0]) {
  int i;
  for (i = 0; i < $1_dim0; i++) {
    PyObject *o = PySequence_GetItem($input,i);
      temp[i] = (int) PyInt_AsLong(o);
  }
  $1 = temp;
}
// allow to set members of int array
%typemap(memberin) int [ANY] {
  int i;
  for (i = 0; i < $1_dim0; i++) {
      $1[i] = $input[i];
  }
}
// access int arrays
%typemap(out) int [ANY] {
  int i;
  $result = PyList_New($1_dim0);
  for (i = 0; i < $1_dim0; i++) {
    PyObject *o = PyLong_FromDouble((int) $1[i]);
    PyList_SetItem($result,i,o);
  }
}

//
%include "/opt/platform/lsf/8.0/include/lsf/lsf.h"
%include "/opt/platform/lsf/8.0/include/lsf/lsbatch.h"

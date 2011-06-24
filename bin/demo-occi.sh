#!/bin/bash

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

case "$1" in
  keys)
    export PYOCCI_STYLE_SHEET=`pwd`/misc/style.css
    export PYTHONPATH=`pwd`
    python pyocci/examples/keyvalue_main.py
    ;;

  vms)
    export PYOCCI_STYLE_SHEET=`pwd`/misc/style.css
    export PYTHONPATH=`pwd`
    python pyocci/examples/vms_main.py
    ;;

  jobs)
    export PYOCCI_STYLE_SHEET=`pwd`/misc/style.css
    export PYTHONPATH=`pwd`
    python pyocci/examples/drmaa_main.py
    ;;
  *)
    echo "Demoes the pyocci framework - will start service on localhost on port"
    echo "8888. Feel free to test the service using the URL http://localhost:8888"
    echo ""
    echo "Usage: $N {keys,vms,jobs}"
    exit 1
    ;;
esac

exit 0

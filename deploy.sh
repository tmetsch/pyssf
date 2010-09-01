#/bin/zsh

# 
# Copyright (C) 2010 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 

case "$1" in
  clean)
    python setup.py clean --all
    ;;

  build)
    $0 clean
    python setup.py build
    rc=$?
    if [[ $rc != 0 ]] ; then
        exit $rc
    fi 
    ;;

  coverage)
    export DRMAA_LIBRARY_PATH=/opt/lsf/7.0/linux2.6-glibc2.3-x86_64/lib/libdrmaa.so
    export PYTHONPATH=build/lib.linux-x86_64-2.6/pylsf
    nosetests --with-coverage --cover-html --cover-html-dir=docs/_build/html/cover --cover-erase --cover-package=pydrmaa,pyssf,pyrest
    rc=$?
    if [[ $rc != 0 ]] ; then
        exit $rc
    fi
    ;;

  doc)
    cd docs
    make clean
    cd ..
	$0 coverage
	# epydocgui epydoc.prj
	cd docs
	make html
    cd ..
    ;;

  deploy)
    $0 build
    $0 doc
	hg commit
    xmessage "Password required"
	hg push
	xmessage "Password required"
    scp -r docs/_build/html/* $USERNAME,pyssf@web.sf.net:/home/groups/p/py/pyssf/htdocs
    ;;

  *)
    echo "Usage: $N {clean|build|coverage|doc|deploy}" >&2
    exit 1
    ;;
esac

exit 0


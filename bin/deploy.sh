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
  clean)
    python setup.py clean --all
    rm -rf docs/build sdist dist build
    rm -rf MANIFEST
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
    nosetests --with-coverage --cover-html --cover-html-dir=docs/build/html/cover --cover-erase --cover-package=occi,ssf
    rc=$?
    if [[ $rc != 0 ]] ; then
        exit $rc
    fi
    ;;

  doc)
    $0 build
  cd docs
    make clean
    cd ..
    $0 coverage
    mkdir docs/build/html/lint/
    pylint -d I0011 -i y -f html ssf occi tests &> docs/build/html/lint/index.html
    pep8 --show-source --show-pep8 --statistics --count ssf occi tests
    cd docs
    make html
    cd ..
    ;;

  big-doc)
    $0 doc
    mkdir docs/build/html/api/
    epydocgui misc/epydoc.prj
    ;;

  test)
    $0 build
    $0 coverage
    ;;

  deploy)
    $0 build
    $0 big-doc
    hg commit
    xmessage "Password required"
    hg push
    xmessage "Password required"
    scp -r docs/build/html/* $USER,pyssf@web.sf.net:/home/groups/p/py/pyssf/htdocs
    ;;

  pypi)
    $0 deploy
    hg tag `cat setup.py | grep 'version =' | awk -F'version =' '{print $2}' | sed 's/,//'`
    python setup.py clean sdist register upload
    ;;

  *)
    echo "Usage: $N {clean,build,coverage,doc,big-doc,test,deploy,pypi}"
    echo "run this from the main code directory..."
    exit 1
    ;;
esac

exit 0


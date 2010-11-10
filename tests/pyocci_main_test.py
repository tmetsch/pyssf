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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 
'''
Created on Nov 10, 2010

@author: tmetsch
'''

# pylint: disable-all

from pyocci.main import MyService
import pyocci.main
import unittest

class Test(unittest.TestCase):

    #===========================================================================
    # Test for succes
    #===========================================================================

    def test_instanciation_of_myservice(self):
        MyService()

    def test_main_for_success(self):
        pyocci.main.__name__ = '__main__'

if __name__ == "__main__":
    unittest.main()

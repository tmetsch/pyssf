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
'''
Created on Jun 28, 2010

@author: tmetsch
'''
from ssf import main
import unittest
import sys

class Test(unittest.TestCase):

    def test_numerus_for_success(self):
        """Form a complex number.
        
        Keyword arguments:
        real -- the real part (default 0.0)
        imag-- the imaginary part (default 0.0)
        """
        self.assertEquals('bla', 'bla')

    def test_run_job_for_success(self):
        main.run_job("/bin/sleep 1")
        pass

    def _some_private_stuff(self):
        pass

if __name__ == "__main__":
    print(sys.path)
    unittest.main()

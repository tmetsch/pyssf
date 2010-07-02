'''
Created on Jun 28, 2010

@author: tmetsch
'''
import unittest
from ssf import main

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
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

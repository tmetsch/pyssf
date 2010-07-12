# 
# Copyright (C) 2010  Platform Computing
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
Created on Jul 12, 2010

@author: tmetsch
'''
from rendering_parsers import HTTPHeaderParser, HTTPData
import unittest

class HTTPHeaderParserTest(unittest.TestCase):

    # Note: Only term and scheme have multiplicity of 1 for categories...

    parser = HTTPHeaderParser()
    correct_header = {'CONTENT_LENGTH': 0,
              'HTTP_CATEGORY': 'compute;scheme="http://purl.org/occi/kind#";label="Compute Resource", myimage;scheme="http://example.com/user/categories/templates#"; ',
              'wsgi.input': '' ,
              'REQUEST_METHOD': 'POST',
              'HTTP_HOST': '0.0.0.0:8080',
              'PATH_INFO': '/',
              'HTTPS': 'False',
              'QUERY_STRING': ''}
    body = "bla-blubber"
    httpData = HTTPData(correct_header, body)

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_to_resource_for_success(self):
        # create a basic resource

        # create a job resource (via category def)
        pass

    def test_from_resource_for_success(self):
        # check if a given resource return proper HTTP stuff.
        pass

    # --------
    # TEST FOR FAILURE
    # --------

    def test_to_resource_for_failure(self):
        # missing categories -> fail big time!

        # missing links -> nothing :-)
        pass

    def test_from_resource_for_failure(self):
        # ??? this should never happen
        pass

    # --------
    # TEST FOR SANITY
    # --------

    def test_to_resource_for_sanity(self):
        # check if given categories are in the resource

        # check if given attributes are in the job resource
        pass

    def test_from_resource_for_sanity(self):
        # check if given data, categories & links are in the response
        pass

if __name__ == "__main__":
    unittest.main()

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
Created on Jul 12, 2010

@author: tmetsch
'''
from pyrest.myexceptions import MissingCategoriesException
from pyrest.rendering_parsers import Parser, HTTPHeaderParser, HTTPData
from pyrest.resource_model import Link, Category, Resource, JobResource
import unittest

class AbstractParserTest(unittest.TestCase):

    parser = Parser()

    # --------
    # TEST FOR FAILURE
    # --------

    def test_not_implemented_throws_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.to_resource, "111", None)
        self.assertRaises(NotImplementedError, self.parser.from_resource, None)

class HTTPHeaderParserTest(unittest.TestCase):

    # Note: Only term and scheme have multiplicity of 1 for categories...
    # currently not handling related etc.

    parser = HTTPHeaderParser()
    # a correct request
    correct_header = {'CONTENT_LENGTH': 0,
              'HTTP_CATEGORY': 'compute;scheme="http://schemas.ogf.org/occi/resource#";title="FooBar";label="Compute Resource", myimage;scheme="http://example.com/user/categories/templates#";',
              'wsgi.input': '' ,
              'REQUEST_METHOD': 'POST',
              'HTTP_HOST': '0.0.0.0:8080',
              'PATH_INFO': '/',
              'HTTPS': 'False',
              'QUERY_STRING': ''}
    body = "bla-blubber"
    http_data = HTTPData(correct_header, body)
    # the corresponding resource
    link = Link()
    category_one = Category()
    category_two = Category()
    category_three = Category()
    resource = Resource()
    job_resource = JobResource()

    def setUp(self):
        self.correct_http_data = HTTPData(self.correct_header, self.body)
        self.link.link_class = 'action'
        self.link.rel = 'http://schemas.ogf.org/occi/job/action#kill'
        self.link.target = 'http://www.example.com/456/#kill'
        self.link.title = 'Kill Job'
        self.category_one.related = ''
        self.category_one.scheme = 'http://schemas.ogf.org/occi/resource#'
        self.category_one.term = 'compute'
        self.category_one.title = 'Compute Resource'
        self.category_two.related = ''
        self.category_two.scheme = 'http://example.com/user/categories/templates#'
        self.category_two.term = 'myimage'
        self.category_two.title = ''
        self.category_three.related = 'http://www.google.com'
        self.category_three.scheme = 'http://schemas.ogf.org/occi/resource#'
        self.category_three.term = 'job'
        self.category_three.title = ''
        self.resource.categories = [self.category_one, self.category_two]
        self.resource.data = self.body
        self.resource.id = '123'
        self.resource.links = [self.link]
        self.job_resource.categories = [self.category_three]
        self.job_resource.id = '456'
        self.job_resource.links = [self.link]
        self.job_resource.attributes = {'occi.drmaa.remote_command': '/bin/sleep'}
        self.job_resource.data = self.body

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_to_resource_for_success(self):
        # create a basic resource
        res = self.parser.to_resource("123", self.http_data)
        self.assertEquals(self.resource.id, res.id)

        # create a job resource (via category def)
        new_header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"'}
        request = HTTPData(new_header, None)
        job_res = self.parser.to_resource("123", request)
        if not isinstance(job_res, JobResource):
            self.fail("Should be Job Resource type...")
        self.assertEquals(job_res.id, '123')

    def test_from_resource_for_success(self):
        # check if a given resource return proper HTTP stuff.
        result = self.parser.from_resource(self.resource)
        self.assertEquals(result.body, self.body)

        # check if it returns a job resource when asking for one...
        category_job = Category()
        category_job.scheme = 'http://schemas.ogf.org/occi/resource#'
        category_job.term = 'job'
        self.resource.categories.append(category_job)
        result = self.parser.from_resource(self.resource)
        self.assertNotEqual(-1, result.header['Category'].find('job'))

    # --------
    # TEST FOR FAILURE
    # --------

    def test_to_resource_for_failure(self):
        # missing categories -> fail big time!
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", None)
        request = HTTPData({}, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # action links -> error :-)
        new_header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"', 'HTTP_LINK': '</network/566-566-566>; class="action"'}
        request = HTTPData(new_header, None)
        res = self.parser.to_resource("123", request)
        self.assertEquals(len(res.links), 0)

        # test that a faulty scheme without http in it doesn't show up...
        test_data = HTTPData({'HTTP_CATEGORY': 'job;scheme="schemas.ogf.org/occi/resource#"'}, self.body)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", test_data)

        # missing scheme for category
        header = {'HTTP_CATEGORY': 'job;scheme=;label=Tada'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # missing term for category
        header = {'HTTP_CATEGORY': ';scheme=http://schemas.ogf.org/occi/resource#;label=Tada'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # wrong order in header for category
        header = {'HTTP_CATEGORY': 'scheme=http://schemas.ogf.org/occi/resource#;job;label=Tada;'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # faulty URL
        header = {'HTTP_CATEGORY': 'job;scheme=glubber;label=Tada;'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # faulty term
        header = {'HTTP_CATEGORY': 'flaver daver 1s;scheme=glubber;job;label="Tada";'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # faulty attributes
        header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"', 'HTTP_ATTRIBUTE': ' occi.drmaa.remote_command = , occi.drmaa.args = 10'}
        request = HTTPData(header, None)
        tmp = self.parser.to_resource("123", request)
        self.assertFalse('occi.drmaa.remote_command' in tmp.attributes)

    def test_from_resource_for_failure(self):
        # ??? this should never happen
        pass

    # --------
    # TEST FOR SANITY
    # --------

    def test_to_resource_for_sanity(self):
        # check if given categories are in the resource
        res = self.parser.to_resource("123", self.http_data)
        self.assertEquals(res.get_certain_categories('compute')[0].term, 'compute')
        # test body
        self.assertEquals(res.data, self.body)

        # test category with len(rel)=1 and len(rel)=x
        test_data = HTTPData({'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#";rel=http://example'}, self.body)
        res = self.parser.to_resource("456", test_data)
        test_data = HTTPData({'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#";rel="http://example,http://www.abc.com"'}, self.body)
        res = self.parser.to_resource("456", test_data)

        # check if given attributes are in the job resource
        test_data = HTTPData({'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"', 'HTTP_ATTRIBUTE': ' occi.drmaa.remote_command = "/bin/sleep", occi.drmaa.args = 10'}, self.body)
        res = self.parser.to_resource("456", test_data)
        # category
        self.assertEquals(res.get_certain_categories('job')[0].term, 'job')
        # get attribute
        self.assertEquals(res.attributes['occi.drmaa.remote_command'], '"/bin/sleep"')

        # test links
        new_header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"', 'HTTP_LINK': '</network/566-566-566>; class="link"'}
        request = HTTPData(new_header, None)
        res = self.parser.to_resource("123", request)
        self.assertEquals(res.links[0].rel, '')
        self.assertEquals(res.links[0].title, '')
        self.assertEquals(res.links[0].target, '/network/566-566-566')
        self.assertEquals(res.links[0].link_class, 'link')

        new_header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"', 'HTTP_LINK': '</compute/345-345-345/default>; class="link"; rel="self";title="type"'}
        request = HTTPData(new_header, None)
        res = self.parser.to_resource("123", request)
        self.assertEquals(res.links[0].rel, 'self')
        self.assertEquals(res.links[0].title, 'type')
        self.assertEquals(res.links[0].target, '/compute/345-345-345/default')
        self.assertEquals(res.links[0].link_class, 'link')

    def test_from_resource_for_sanity(self):
        # check if given data, categories & links are in the response
        res = self.parser.from_resource(self.job_resource)
        # body
        self.assertEquals(res.body, self.body)
        # attributes
        self.assertEquals(res.header['occi.drmaa.remote_command'], '/bin/sleep')
        # category
        self.assertEquals(res.header['Category'].split(';')[0], 'job')
        # links
        self.assertEquals(res.header['Link'].split(';')[0], '<' + self.link.target + '>')

if __name__ == "__main__":
    unittest.main()

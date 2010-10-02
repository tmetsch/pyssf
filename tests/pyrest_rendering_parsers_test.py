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
from pyrest.rendering_parsers import Parser, HTTPHeaderParser, HTTPListParser, \
    HTTPData, HTTPTextParser, HTTPHTMLParser
from pyrest.resource_model import Action, Category, Resource
from tests.mocks import DummyBackend
import unittest

class AbstractParserTest(unittest.TestCase):

    parser = Parser()

    # --------
    # TEST FOR FAILURE
    # --------

    def test_not_implemented_throws_for_failure(self):
        self.assertRaises(NotImplementedError, self.parser.to_resource, "111", None)
        self.assertRaises(NotImplementedError, self.parser.from_resource, None)
        self.assertRaises(NotImplementedError, self.parser.to_action, None)
        self.assertRaises(NotImplementedError, self.parser.from_categories, None)

class HTTPHeaderParserTest(unittest.TestCase):

    # FIXME: include title="A title, quotes required, foo=bar", checks!
    # FIXME: also set/get hard coded resource/cat/action attributes (title etc).

    # Note: Only term and scheme have multiplicity of 1 for categories...
    # currently not handling related etc.

    parser = HTTPHeaderParser()
    # a correct request
    correct_header = {'CONTENT_LENGTH': 0,
              'HTTP_CATEGORY': 'compute;scheme="http://schemas.ogf.org/occi/resource#";title="FooBar", myimage;scheme="http://example.com/user/categories/templates#";',
              'HTTP_ATTRIBUTE':'occi.compute.cores=2, occi.compute.speed=2.5, occi.compute.memory=2.0',
              'wsgi.input': '' ,
              'REQUEST_METHOD': 'POST',
              'HTTP_HOST': '0.0.0.0:8080',
              'PATH_INFO': '/',
              'HTTPS': 'False',
              'QUERY_STRING': ''}
    body = "bla-blubber"
    http_data = HTTPData(correct_header, body)
    # the corresponding resource
    action_category = Category()
    action_header = {'HTTP_CATEGORY': 'action;scheme="http://schemas.ogf.org/occi/core#";title="An Action"'}
    category_one = Category()
    category_two = Category()
    category_three = Category()

    category_keys_list = [category_one, category_two, category_three]

    resource = Resource()
    term_action = Action()
    job_resource = Resource()

    def setUp(self):
        self.correct_http_data = HTTPData(self.correct_header, self.body)
        self.correct_action_http_data = HTTPData(self.action_header, self.body)

        self.action_category = Action.category

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

        self.term_action.categories = [DummyBackend.action_category]

        self.job_resource.categories = [self.category_three]
        self.job_resource.id = '456'
        self.job_resource.attributes = {'occi.drmaa.remote_command': '/bin/sleep'}
        self.job_resource.actions = [self.term_action]
        self.job_resource.data = self.body

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_to_action_for_success(self):
        action = self.parser.to_action(self.correct_action_http_data)
        self.assertTrue(action.categories[0].__eq__(self.action_category))

    def test_from_categories_for_succes(self):
        http_data = self.parser.from_categories(self.category_keys_list)
        self.assertEquals(len(http_data.header['Category'].split(',')), 3)

    def test_to_resource_for_success(self):
        # create a basic resource
        res = self.parser.to_resource("123", self.http_data)
        self.assertEquals(self.resource.id, res.id)

        # create a job resource (via category def)
        new_header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"'}
        request = HTTPData(new_header, None)
        job_res = self.parser.to_resource("123", request)
        if len(job_res.get_certain_categories('job')) < 1:
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

    def test_from_resources_for_success(self):
        result = self.parser.from_resources([self.resource, self.job_resource])
        self.assertEquals(result.header['Location'], '/' + self.resource.id + ',/' + self.job_resource.id)

    # --------
    # TEST FOR FAILURE
    # --------

    def test_to_action_for_failure(self):
        self.assertRaises(MissingCategoriesException, self.parser.to_action, HTTPData({}, None))
        self.assertRaises(MissingCategoriesException, self.parser.to_action, None)

    def test_from_categories_for_failure(self):
        self.assertRaises(AttributeError, self.parser.from_categories, None)

    def test_to_resource_for_failure(self):
        # missing categories -> fail big time!
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", None)
        request = HTTPData({}, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # test that a faulty scheme without http in it doesn't show up...
        test_data = HTTPData({'HTTP_CATEGORY': 'job;scheme="schemas.ogf.org/occi/resource#"'}, self.body)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", test_data)

        # missing scheme for category
        header = {'HTTP_CATEGORY': 'job;scheme=;title=Tada'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # missing term for category
        header = {'HTTP_CATEGORY': ';scheme=http://schemas.ogf.org/occi/resource#;title=Tada'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # wrong order in header for category
        header = {'HTTP_CATEGORY': 'scheme=http://schemas.ogf.org/occi/resource#;job;title=Tada;'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # faulty URL
        header = {'HTTP_CATEGORY': 'job;scheme=glubber;title=Tada;'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # faulty term
        header = {'HTTP_CATEGORY': 'flaver daver 1s;scheme=glubber;job;title="Tada";'}
        request = HTTPData(header, None)
        self.assertRaises(MissingCategoriesException, self.parser.to_resource, "123", request)

        # faulty attributes
        header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"', 'HTTP_ATTRIBUTE': ' occi.drmaa.remote_command = , occi.drmaa.args = 10'}
        request = HTTPData(header, None)
        tmp = self.parser.to_resource("123", request)
        self.assertFalse('occi.drmaa.remote_command' in tmp.attributes)

        header = {'HTTP_CATEGORY': 'job;scheme="http://schemas.ogf.org/occi/resource#"', 'HTTP_ATTRIBUTE': ' occi.drmaa.remote_command, occi.drmaa.args = 10'}
        request = HTTPData(header, None)
        tmp = self.parser.to_resource("123", request)
        self.assertFalse('occi.drmaa.remote_command' in tmp.attributes)

    def test_from_resource_for_failure(self):
        # ??? this should never happen
        pass

    def test_from_resources_for_failure(self):
        pass

    # --------
    # TEST FOR SANITY
    # --------

    def test_to_action_for_sanity(self):
        action = self.parser.to_action(self.correct_action_http_data)
        self.assertEquals(action.categories[0], self.action_category)

    def test_from_categories_for_sanity(self):
        # check that no , are added when only one cate needs to be parsed...
        http_data = self.parser.from_categories([self.category_one])
        self.assertTrue(http_data.header['Category'].find(self.category_one.term + ';scheme=' + self.category_one.scheme) > -1)

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

    def test_from_resource_for_sanity(self):
        # check if given data, categories & links are in the response
        res = self.parser.from_resource(self.job_resource)
        # body
        self.assertEquals(res.body, self.body)
        # attributes
        self.assertEquals(res.header['Attribute'], 'occi.drmaa.remote_command=/bin/sleep')
        # category
        self.assertEquals(res.header['Category'].split(';')[0], 'job')
        # actions
        self.assertEquals(res.header['Link'].split(';')[1], "action=" + DummyBackend.action_category.term + ">")

    def test_from_resources_for_sanity(self):
        result = self.parser.from_resources([self.resource, self.job_resource])
        self.assertEquals(result.header['Location'], '/' + self.resource.id + ',/' + self.job_resource.id)

class HTTPListParserTest(unittest.TestCase):
    list_parser = HTTPListParser()

    category_keys_list = [HTTPHeaderParserTest.category_one, HTTPHeaderParserTest.category_two, HTTPHeaderParserTest.category_three]
    resource = Resource()
    job_resource = Resource()

    def setUp(self):

        self.resource.categories = []
        self.resource.id = '123'

        self.job_resource.categories = [HTTPHeaderParserTest.category_three]
        self.job_resource.id = '456'

    # --------
    # TEST FOR SUCCESS
    # --------

    def test_from_categories_for_success(self):
        data = self.list_parser.from_categories(self.category_keys_list)
        self.assertEquals(data.header['Content-type'], 'text/uri-list')

    def test_from_resources_for_success(self):
        result = self.list_parser.from_resources([self.resource, self.job_resource])
        self.assertEquals(result.body, '/' + self.resource.id + '\n/' + self.job_resource.id)

    # --------
    # TEST FOR FAILURE
    # --------

    def test_from_categories_for_failure(self):
        self.assertRaises(AttributeError, self.list_parser.from_categories, None)

    def test_from_resources_for_failure(self):
        pass

    # --------
    # TEST FOR SANITY
    # --------

    def test_from_categories_for_sanity(self):
        data = self.list_parser.from_categories([HTTPHeaderParserTest.category_one])
        self.assertEquals(data.header['Content-type'], 'text/uri-list')
        self.assertEquals(data.body, self.category_keys_list[0].scheme + self.category_keys_list[0].term)
        self.assertTrue(data.body is not None)

    def test_from_resources_for_sanity(self):
        result = self.list_parser.from_resources([self.resource, self.job_resource])
        self.assertEquals(result.header['Content-type'], 'text/uri-list')
        self.assertEquals(result.body, '/' + self.resource.id + '\n/' + self.job_resource.id)

class HTTPTextParserTest(unittest.TestCase):

    parser = HTTPTextParser()

    category_keys_list = [HTTPHeaderParserTest.category_one, HTTPHeaderParserTest.category_two, HTTPHeaderParserTest.category_three]
    resource = Resource()
    job_resource = Resource()

    def setUp(self):
        self.category_keys_list = []

        self.resource.categories = []
        self.resource.id = '123'

        self.job_resource.categories = [HTTPHeaderParserTest.category_three]
        self.job_resource.id = '456'
    # --------
    # TEST FOR SUCCESS
    # --------

    def test_from_categories_for_success(self):
        data = self.parser.from_categories(self.category_keys_list)
        self.assertTrue(data.body is not None)

    def test_from_resources_for_success(self):
        result = self.parser.from_resources([self.resource, self.job_resource])
        self.assertEquals(result.body, 'Location:/' + self.resource.id + '\nLocation:/' + self.job_resource.id)
    # --------
    # TEST FOR FAILURE
    # --------

    def test_from_categories_for_failure(self):
        self.assertRaises(AttributeError, self.parser.from_categories, None)

    # --------
    # TEST FOR SANITY
    # --------

    def test_from_categories_for_sanity(self):
        data = self.parser.from_categories([HTTPHeaderParserTest.category_one])
        self.assertEquals(data.header['Content-type'], 'text/plain')
        self.assertEquals(data.body, 'Category:' + HTTPHeaderParserTest.category_one.term + ';scheme=' + HTTPHeaderParserTest.category_one.scheme + ';title=' + HTTPHeaderParserTest.category_one.title + '\n')
        self.assertTrue(data.body is not None)

    def test_from_resources_for_sanity(self):
        result = self.parser.from_resources([self.resource, self.job_resource])
        self.assertEquals(result.header['Content-type'], 'text/plain')
        self.assertEquals(result.body, 'Location:/' + self.resource.id + '\nLocation:/' + self.job_resource.id)

class HTTPHTMLParserTest(unittest.TestCase):

    # Note: only testing for sanity and looking for text/html content type.

    parser = HTTPHTMLParser()
    category_one = Category()
    category_two = Category()
    category_keys_list = [category_one, category_two]
    resource = Resource()

    def setUp(self):
        self.category_one.related = ''
        self.category_one.scheme = 'http://schemas.ogf.org/occi/resource#'
        self.category_one.term = 'compute'
        self.category_one.title = 'Compute Resource'

        self.category_two.related = ''
        self.category_two.scheme = 'http://example.com/user/categories/templates#'
        self.category_two.term = 'myimage'
        self.category_two.title = ''

        self.resource.categories = [self.category_one, self.category_two]
        self.resource.attributes = {'foo':'bar'}
        self.resource.id = '123'

        self.category_keys_list = []

    # --------
    # TEST FOR SANITY
    # --------

    def test_from_categories_for_sanity(self):
        http_data = self.parser.from_categories(self.category_keys_list)
        self.assertEquals(http_data.header['Content-type'], "text/html")
        self.assertTrue(http_data.body is not None)

    def test_from_resource_for_sanity(self):
        http_data = self.parser.from_resource(self.resource)
        self.assertEquals(http_data.header['Content-type'], "text/html")
        self.assertTrue(http_data.body is not None)

    def test_from_resources_for_sanity(self):
        http_data = self.parser.from_resources([self.resource])
        self.assertEquals(http_data.header['Content-type'], "text/html")
        self.assertTrue(http_data.body is not None)

if __name__ == "__main__":
    unittest.main()


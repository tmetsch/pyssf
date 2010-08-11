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
This module actually configures and runs the service.

Created on Aug 10, 2010

@author: tmetsch
'''
from pyrest.service import ResourceHandler
import web

# 
# Configures web.py and tells him which handlers should listen to which 
# entry-point.
# 
urls = ('/(.*)', 'ResourceHandler')

# 
# Turns debugging on of off - Default is False (off).
# 
web.config.debug = False

# 
# When using the build-in webserver of the web.py framework there is no need to
# change the following line. If the service is deployed in Apache using the
# mod_wsgi use the second line. Do not change the name of the attribute. Apache
# mod_wsgi will assume it is named application (lowercase).
# 
application = web.application(urls, globals())
#application = web.application(urls, globals()).wsgifunc()

# 
# When using the build-in webserver with SSL enabled uncomment the following
# lines
# 
from web.wsgiserver import CherryPyWSGIServer
#CherryPyWSGIServer.ssl_certificate = "<path to CA>/newcert.pem"
#CherryPyWSGIServer.ssl_private_key = "<path to CA>/newkey.pem"
CherryPyWSGIServer.ssl_certificate = "/home/tmetsch/scrap/CA/server/newcert.pem"
CherryPyWSGIServer.ssl_private_key = "/home/tmetsch/scrap/CA/server/newkey.pem"

#
# Tells the service to enable Basic authentication. Therefore a security
# handler needs to be defined.
#


# 
# Tells the service tells the ResourceHandler which Storage, Backend and which
# Parser it should use.
#
#from <module> import <class>
#
# define storage
#ResourceHandler.resources = MyStorage()
#
# define parser
#MyStorage.parser = MyParser()
#
# define a backend
#ResourceHandler.backend = MyHandler()

if __name__ == "__main__":
    """
    Finally run the application.
    """
    application.run()

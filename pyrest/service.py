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
Created on Jul 2, 2010

@author: tmetsch
'''

import web

urls = (
    '/(.*)', 'ResourceHandler'
)
app = web.application(urls, globals())

class ResourceHandler:
    # overall add ssl sec...

    def POST(self, *data):
        # create a new resource
        # if exists say they'll need to use put
        # return location
        pass

    def GET(self, *data):
        # return resource representation (and act based on mime-types)
        return 'Hello World'

    def PUT(self, *data):
        # update a resource
        pass

    def DELETE(self, *data):
        # delete a resource representation
        pass

if __name__ == "__main__":
    app.run()

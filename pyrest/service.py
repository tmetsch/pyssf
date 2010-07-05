'''
Created on Jul 2, 2010

@author: tmetsch
'''

import web
import os

urls = (
    '/(.*)', 'ResourceHandler'
)
app = web.application(urls, globals())

def is_test():
    if 'WEBPY_ENV' in os.environ:
        return os.environ['WEBPY_ENV'] == 'test'

class ResourceHandler:
    # overall add ssl sec...

    def POST(self, *data):
        # create a new resource
        # if exists say they'll need to use put
        # return location
        pass

    def GET(self, *data):
        # return resource representation (and act based on mime-types)
        return 'resource' + str(data)

    def PUT(self, *data):
        # update a resource
        pass

    def DELETE(self, *data):
        # delete a resource representation
        pass

if (not is_test()) and __name__ == "__main__":
    app.run()

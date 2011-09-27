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
'''
The Service Sharing Facility.

Created on Jun 28, 2010

@author: tmetsch
'''

from occi.service import OCCI
from ssf.negotiation_service import AGREEMENT, AgreementHandler
import logging


class SSF(object):
    '''
    Service Sharing Facility.
    '''

    logger = logging.getLogger()

    PORT = 8888

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s [%(levelname)-7s] %(message)s")
        self.logger.info('Welcome to SSF')
        self.service = OCCI()

    def start(self):
        '''
        Start the service.
        '''
        self.service.register_backend(AGREEMENT, AgreementHandler())
        self.logger.info('Starting Negotiation Service on port %i', self.PORT)
        self.service.start(self.PORT)

if __name__ == '__main__':
    SSF().start()

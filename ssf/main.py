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

from pylsf import lsf

def run_job(command):
    """
    Run a job...
    """
    submitreq = lsf.submit()
    submitreq.command = command
    submitreq.options = 0
    submitreq.options2 = 0

    limits = []
    for i in range (0, lsf.LSF_RLIM_NLIMITS):
        limits.append(lsf.DEFAULT_RLIMIT)

    submitreq.rLimits = limits

    submitreq.beginTime = 0
    submitreq.termTime = 0
    submitreq.numProcessors = 1
    submitreq.maxNumProcessors = 1

    submitreply = lsf.submitReply()

    if lsf.lsb_init("test") > 0:
        exit(1)
#
#    hInfo = lsf.hostInfoEnt()
#    numHosts = lsf.new_ip()
#    lsf.ip_assign(numHosts, 1)
#    print(lsf.ip_value(numHosts))
#    #hInfo = lsf.lsb_hostinfo("ubuntu", numHosts)
#    print(hInfo.host)

    job_id = lsf.lsb_submit(submitreq, submitreply)
    return job_id

if __name__ == '__main__':
    print("LSF Clustername is :", lsf.ls_getclustername())
    run_job("/bin/sleep 10")


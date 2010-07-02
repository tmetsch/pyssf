'''
Created on Jun 28, 2010

@author: tmetsch
'''

from pylsf import lsf

def run_job(command):
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
    submitreq.maxNumProcessors = 1;

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

    jobId = lsf.lsb_submit(submitreq, submitreply)
    return jobId

if __name__ == '__main__':
    print(lsf.ls_getclustername())
    run_job("/bin/sleep 10")


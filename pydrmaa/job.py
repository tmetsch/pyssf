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
Module which defines a model, factory and starters. Work is based upon DRMAAv2.

Created on Jul 19, 2010

@author: tmetsch
'''
try:
    from pylsf import lsf
except ImportError:
    print("Warning: pylsf not initialized properly - check if '_lsf.so' is in"
          + " your PYTHONPATH.")
try:
    import drmaa
except ImportError:
    print("Warning: drmaa-python not initialized properly - check if the"
          + " prerequisite package is installed!")
import os

class Job(object):
    """
    A simple job - should correspond to JobTemplate in the DRMAAv2 spec.
    """

    def __init__(self):
        self.job_id = 0
        self.remote_command = ''
        self.args = []

    def terminate(self):
        """
        terminate a running job.
        """
        raise NotImplementedError

    def get_state(self):
        """
        return job state.
        """
        raise NotImplementedError

class JobFactory(object):
    """
    Factory for jobs.
    """

    def create_job(self, command, args = None):
        """
        Create a new job instance.
        
        command - mandatory field for the executable.
        """
        if args is None:
            # need to do this...default values are shared!
            args = []
        return DRMAAJob(command, args)

class DRMAAJob(Job):
    """
    A DRMAAv1 job.
    """

    s = drmaa.Session()
    try:
        s.initialize()
    except:
        pass

    def __init__(self, command, args):
        super(DRMAAJob, self).__init__()
        self.remote_command = command
        self.args = args

        self.job_template = self.s.createJobTemplate()
        self.job_template.remoteCommand = command
        self.job_template.args = args
        self.job_template.joinFiles = True

        self.job_id = self.s.runJob(self.job_template)

    def __del__(self):
        self.s.deleteJobTemplate(self.job_template)

    def terminate(self):
        self.s.control(self.job_id, drmaa.JobControlAction.TERMINATE)

    def get_state(self):
        return self.s.jobStatus(self.job_id)

class LSFJob(Job):
    """
    Wraps the job commands to the LSF API using pylsf.
    """

    def __init__(self, command, args):
        """
        Initialize a LSF Job and schedules it!
        """
        super(LSFJob, self).__init__()
        self.remote_command = command
        self.args = args

        if lsf.lsb_init("job_" + command) > 0:
            raise RuntimeError("Couldn't initialize LSF!")

        submitreq = lsf.submit()
        submitreq.command = command + ' ' + ' '.join(args)
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

        self.job_id = lsf.lsb_submit(submitreq, submitreply)

    def terminate(self):
        # lsf.lsb_signaljob(jobId, 9)
        if self.get_state() != 'DONE':
            lsf.lsb_signaljob(self.job_id, 9)
        else:
            raise AttributeError('Cannot terminate done job.')

    def get_state(self):
        # FIXME: this needs to be fixed!
        process = os.popen("bjobs -a " + str(self.job_id) +
                           " | awk 'NR != 1 {print $3}'")
        string = process.readline()
        process.close()
        return string.replace('\n', '')

# following lines are taken from the DRMAAv2 stack - eventually this should all
# be supported:
# 
#        void suspend()  // suspend a running job
#            raises (???);
#        void resume()  // resume a suspended job
#            raises (???);
#        void hold()   // put a queued job on hold
#            raises (???);
#        void release() // release a job on hold
#            raises (???);
#        void terminate()  // terminate a running job
#            raises (???);
#        JobState getState(out native subState)
#            raises (???);
#        JobInfo getInfo()
#            raises (???);
#        Job waitStarted(in TimeAmount timeout)
#            raises (???);
#        Job waitTerminated(in TimeAmount timeout)
#            raises (???);
#            
#readonly attribute StringList attributeNames;            // must be supported
#attribute string remoteCommand;                          // must be supported
#attribute OrderedStringList args;                        // must be supported
#attribute DRMAA::JobSubmissionState jobSubmissionState;  // must be supported
#attribute Dictionary jobEnvironment;                     // must be supported
#attribute string workingDirectory;                       // must be supported
#attribute string jobCategory;                            // must be supported
#attribute string accountingId;                           // must be supported
#attribute StringList email;                              // must be supported
#attribute boolean blockEmail;                            // must be supported
#attribute string jobName;                                // must be supported
#attribute string inputPath;                              // must be supported
#attribute string outputPath;                             // must be supported
#attribute string errorPath;                              // must be supported
#attribute boolean joinFiles;                             // must be supported
#attribute string reservationId;                          // must be supported
#attribute string queueName;                              // must be supported
#attribute long minSlots;                                 // must be supported
#attribute long maxSlots;                                 // must be supported
#attribute StringList candidateMachines;                  // must be supported
#attribute long minPhysMemory;                            // must be supported
#attribute OperatingSystem machineOS;                     // must be supported
#attribute CpuArchitecture machineArch;                   // must be supported
#attribute AbsoluteTime startTime;                        // must be supported
#attribute AbsoluteTime deadlineTime;                     // support is optional
#attribute OrderedStringList stageInFiles;                // support is optional
#attribute OrderedStringList stageOutFiles;               // support is optional
#attribute TimeAmount wallclockTimeLimit;                 // support is optional
#attribute Dictionary softResourceLimits;                 // support is optional
#attribute Dictionary hardResourceLimits;                 // support is optional
#attribute Dictionary drmsSpecific;                       // must be supported

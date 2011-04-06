"""
Copyright (C) 2011  David Morton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import multiprocessing
import math
import string

import wx
from wx.lib.pubsub import Publisher as pub
from wx.lib.delayedresult import startWorker
import numpy

from spikepy.common.open_data_file import open_data_file
from spikepy.common import utils
from spikepy.common import path_utils 
from spikepy.common import plugin_utils
from spikepy.common import signal_utils
from spikepy.common import projection_utils as pu
from spikepy.common import config_utils
from spikepy.common.config_manager import config_manager
import spikepy.common.program_text as pt

def plugin_process_worker(input_queue, results_queue):
    for job in iter(input_queue.get, None):
        # continue processing from the run_queue until a sentinel is 
        #  encountered... put results in results_queue.
        stage_name = job.stage_name
        method_name = job.method_name
        run_dict = job.run_dict
        method_obj = plugin_utils.get_method(stage_name, method_name,
                                             instantiate=True)

        run_results = method_obj.run(*run_dict['args'], **run_dict['kwargs'])
        results_queue.put({'job_id':job.job_id,
                           'results':run_results})

def standard_process_worker(input_queue, results_queue)
    for job in iter(input_queue.get, None):
        # continue processing from the run_queue until a sentinel is 
        #  encountered... put results in results_queue.
        run_dict = job.run_dict

        run_results = function(*run_dict['args'], **run_dict['kwargs'])
        results_queue.put({'job_id':job.job_id,
                           'results':run_results})

class DCRunManager(object):
    def run(self, trial_list, pending_jobs_list, message_queue):
        # message_queue is used to communicate with the rest of the
        #  main program.  We will only push onto it from here, never get
        #  from it.
        startWorker(self._run_consumer, self._run_worker,
                    wargs=(trial_list, pending_jobs_list, message_queue, 
                           abort_queue),
                    cargs=(pending_jobs_list, message_queue))

    def _run_worker(self, trial_list, pending_jobs_list, 
                          message_queue, abort_queue):
        try:
            num_process_workers = multiprocessing.cpu_count()
        except NotImplimentedError:
            num_process_workers = 8

        # these run queues will be initially empty, then as dependencies are
        #  satisfied, they will be loaded up with jobs.  When all the jobs
        #  have been processed we need to send sentinels
        #  to kill the process workers.
        standard_run_queue = multiprocessing.Queue.Queue()
        plugin_run_queue = multiprocessing.Queue.Queue()

        results_queue = multiprocessing.Queue.Queue()

        # we're going to start up all the jobs here.
        processes = []
        standard_worker_info = [standard_process_worker, 
                                (standard_run_queue, results_queue)]
        plugin_worker_info   = [plugin_process_worker,   
                                (plugin_run_queue, results_queue)]
        for i in xrange(num_process_workers):
            for worker, args in [standard_worker_info, plugin_worker_info]:
                process = multiprocessing.Process(target=worker, args=args)
                process.start()
                processes.append(process)

        # determine what jobs can run and load them up.
        total_num_jobs = len(pending_jobs_list)
        ready_jobs, remaining_jobs = find_ready_jobs(trial_list,
                                                     pending_jobs_list)
        start_jobs(ready_jobs, standard_run_queue, plugin_run_queue,
                   message_queue)
        num_running_jobs = len(ready_jobs)

        # wait for results to start comming in.
        results = []
        should_abort = False
        while not should_abort and num_running_jobs > 1:
            job_result = None
            try:
                # look for a result but do not block
                job_result = results_queue.get(False))
            except multiprocessing.Queue.Empty:
                pass

            # check for abort message, block at most 0.05 seconds
            should_abort = False
            try:
                should_abort = abort_queue.get(True, 0.05)
            except multiprocessing.Queue.Empty:
                pass

            if should_abort:
                # do abort
                break

            if job_result is None:
                continue
                
            # continue processing result.
            end_job(job_result, pending_jobs_list, message_queue)
            num_running_jobs -= 1

            # load up newly ready jobs
            ready_jobs, remaining_jobs = find_ready_jobs(trial_list, 
                                                         remaining_jobs)
            start_jobs(ready_jobs, standard_run_queue, plugin_run_queue,
                       message_queue)
            num_running_jobs += len(ready_jobs)

            # check for stuckness
            if num_running_jobs == 0 and len(remaining_jobs) > 0:
                print "BAD!!! DEPENDENCY COULD NOT BE MET"
                pass # XXX BAD!! MEANS DEPENDENCY COULD NOT BE MET!!

        # put sentinels in run_queues to allow process_workers to end naturally
        for i in range(len(processes)):
            standard_run_queue.put(None)
            plugin_run_queue.put(None)

        for process in processes:
            process.terminate() # in case some processes didn't end naturally.
            process.join()

        # tell the main program that all processes have finished.
        message_queue.put(('all processes ended', pending_jobs_list))

        return pending_jobs_list # jobs that didn't complete.

    def _run_consumer(self, delayed_result, pending_jobs_list, message_queue):
        unfinished_jobs_list = delayed_result.get()
        
        # publish whatever you want now, you're back in the main thread.
        

def find_ready_jobs(trial_list, pending_jobs_list):
    '''
        Looks at the pending jobs list and does dependency checking to see what
    jobs are ready to be run now.
    Returns:
        ready_jobs, remaining_jobs     : both are lists (potentially empty)
    '''
    ready_jobs = []
    remaining_jobs = []
    for job in pending_jobs_list:
        if job.is_ready_to_run(trial_list):
            ready_jobs.append(job)
        else:
            remaining_jobs.append(job)
    return ready_jobs, remaining_jobs


def end_job(job_result, trial_list, message_queue):
    '''
        Run after the result of a job has been calculated.  This function puts 
    the results into the appropriate place and uses the message_queue to tell
    the main program that the job has completed.
    Returns: 
        None
    '''
    trial_dict = {}
    for trial in trial_list:
        trial_dict[trial.trial_id] = trial

    results = job_result['results']
    job  = job_result['job']
    pending_jobs_list.remove(job)

    stage_name = job.stage_name
    trial_ids = job.trial_ids
    for trial_id in trial_ids:
        trial = trial_dict[trial_id]
        if stage_name is not None:
            stage_data = trial.get_stage_data(stage_name)
            if stage_data.results is not None:
                stage_data.results.update(results)
            else:
                stage_data.results = results
    message_queue.put(('finished', job))


def start_jobs(job_list, standard_run_queue, plugin_run_queue, message_queue):
    '''
        Puts all jobs in the job_list into the appropriate run_queue and
    updates the main program via the message_queue.
    Returns:
        None
    '''
    for job in job_list:
        if job.kind == 'standard':
            standard_run_queue.put(job)
        elif job.kind == 'plugin':
            plugin_run_queue.put(job)
    message_queue.put(('started', job)

#!/usr/bin/python3 -u
#
# Copyright 2008 Google Inc. All Rights Reserved.


"""Tests for job."""

import copy
import getpass
import sys
import unittest

try:
    import autotest.common as common  # pylint: disable=W0611
except ImportError:
    from . import common  # pylint: disable=W0611
from autotest.cli import cli_mock
# pylint: disable=E0611
from autotest.cli import job
from autotest.cli import rpc
from autotest.client.shared.test_utils import mock


class job_unittest(cli_mock.cli_unittest):

    def setUp(self):
        super(job_unittest, self).setUp()
        self.values = copy.deepcopy(self.values_template)

    results = [{'status_counts': {'Aborted': 1},
                'control_file':
                "job.run_test('sleeptest')\n",
                'name': 'test_job0',
                'control_type': 'Server',
                'priority':
                'Medium',
                'owner': 'user0',
                'created_on':
                '2008-07-08 17:45:44',
                'synch_count': 2,
                'id': 180},
               {'status_counts': {'Queued': 1},
                'control_file':
                "job.run_test('sleeptest')\n",
                'name': 'test_job1',
                'control_type': 'Client',
                'priority':
                'High',
                'owner': 'user0',
                'created_on':
                '2008-07-08 12:17:47',
                'synch_count': 1,
                'id': 338}]

    values_template = [{'id': 180,          # Valid job
                        'priority': 'Low',
                        'name': 'test_job0',
                        'owner': 'Cringer',
                        'invalid': False,
                        'created_on': '2008-07-02 13:02:40',
                        'control_type': 'Server',
                        'status_counts': {'Queued': 1},
                        'synch_count': 2},
                       {'id': 338,          # Valid job
                        'priority': 'High',
                        'name': 'test_job1',
                        'owner': 'Fisto',
                        'invalid': False,
                        'created_on': '2008-07-06 14:05:33',
                        'control_type': 'Client',
                        'status_counts': {'Queued': 1},
                        'synch_count': 1},
                       {'id': 339,          # Valid job
                        'priority': 'Medium',
                        'name': 'test_job2',
                        'owner': 'Roboto',
                        'invalid': False,
                        'created_on': '2008-07-07 15:33:18',
                        'control_type': 'Server',
                        'status_counts': {'Queued': 1},
                        'synch_count': 1},
                       {'id': 340,          # Invalid job priority
                        'priority': 'Uber',
                        'name': 'test_job3',
                        'owner': 'Panthor',
                        'invalid': True,
                        'created_on': '2008-07-04 00:00:01',
                        'control_type': 'Server',
                        'status_counts': {'Queued': 1},
                        'synch_count': 2},
                       {'id': 350,          # Invalid job created_on
                        'priority': 'Medium',
                        'name': 'test_job4',
                        'owner': 'Icer',
                        'invalid': True,
                        'created_on': 'Today',
                        'control_type': 'Client',
                        'status_counts': {'Queued': 1},
                        'synch_count': 1},
                       {'id': 420,          # Invalid job control_type
                        'priority': 'Urgent',
                        'name': 'test_job5',
                        'owner': 'Spikor',
                        'invalid': True,
                        'created_on': '2012-08-08 18:54:37',
                        'control_type': 'Child',
                        'status_counts': {'Queued': 1},
                        'synch_count': 2}]


class job_list_unittest(job_unittest):

    def test_job_list_jobs(self):
        self.god.stub_function(getpass, 'getuser')
        getpass.getuser.expect_call().and_return('user0')
        self.run_cmd(argv=['atest', 'job', 'list', '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'owner': 'user0',
                                                 'running': None},
                            True, self.values)],
                     out_words_ok=['test_job0', 'test_job1', 'test_job2'],
                     out_words_no=['Uber', 'Today', 'Child'])

    def test_job_list_jobs_only_user(self):
        values = [item for item in self.values if item['owner'] == 'Cringer']
        self.run_cmd(argv=['atest', 'job', 'list', '-u', 'Cringer',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'owner': 'Cringer',
                                                 'running': None},
                            True, values)],
                     out_words_ok=['Cringer'],
                     out_words_no=['Fisto', 'Roboto', 'Panthor', 'Icer',
                                   'Spikor'])

    def test_job_list_jobs_all(self):
        self.run_cmd(argv=['atest', 'job', 'list', '--all',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'running': None},
                            True, self.values)],
                     out_words_ok=['Fisto', 'Roboto', 'Panthor',
                                   'Icer', 'Spikor', 'Cringer'],
                     out_words_no=['Created', 'Priority'])

    def test_job_list_jobs_id(self):
        self.run_cmd(argv=['atest', 'job', 'list', '5964',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['5964'],
                                                 'running': None},
                            True,
                            [{'status_counts': {'Completed': 1},
                              'control_file': 'kernel = \'8210088647656509311.kernel-smp-2.6.18-220.5.x86_64.rpm\'\ndef step_init():\n    job.next_step([step_test])\n    testkernel = job.kernel(\'8210088647656509311.kernel-smp-2.6.18-220.5.x86_64.rpm\')\n    \n    testkernel.install()\n    testkernel.boot(args=\'console_always_print=1\')\n\ndef step_test():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "Autotest Team"\n    NAME = "Sleeptest"\n    TIME = "SHORT"\n    TEST_CATEGORY = "Functional"\n    TEST_CLASS = "General"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    This test simply sleeps for 1 second by default.  It\'s a good way to test\n    profilers and double check that autotest is working.\n    The seconds argument can also be modified to make the machine sleep for as\n    long as needed.\n    """\n    \n    job.run_test(\'sleeptest\',                             seconds = 1)',
                              'name': 'mytest',
                              'control_type': 'Client',
                              'run_verify': 1,
                              'priority': 'Medium',
                              'owner': 'user0',
                              'created_on': '2008-07-28 12:42:52',
                              'timeout': 144,
                              'synch_count': 1,
                              'id': 5964}])],
                     out_words_ok=['user0', 'Completed', '1', '5964'],
                     out_words_no=['sleeptest', 'Priority', 'Client', '2008'])

    def test_job_list_jobs_id_verbose(self):
        self.run_cmd(argv=['atest', 'job', 'list', '5964', '-v',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['5964'],
                                                 'running': None},
                            True,
                            [{'status_counts': {'Completed': 1},
                              'control_file': 'kernel = \'8210088647656509311.kernel-smp-2.6.18-220.5.x86_64.rpm\'\ndef step_init():\n    job.next_step([step_test])\n    testkernel = job.kernel(\'8210088647656509311.kernel-smp-2.6.18-220.5.x86_64.rpm\')\n    \n    testkernel.install()\n    testkernel.boot(args=\'console_always_print=1\')\n\ndef step_test():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "Autotest Team"\n    NAME = "Sleeptest"\n    TIME = "SHORT"\n    TEST_CATEGORY = "Functional"\n    TEST_CLASS = "General"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    This test simply sleeps for 1 second by default.  It\'s a good way to test\n    profilers and double check that autotest is working.\n    The seconds argument can also be modified to make the machine sleep for as\n    long as needed.\n    """\n    \n    job.run_test(\'sleeptest\',                             seconds = 1)',
                              'name': 'mytest',
                              'control_type': 'Client',
                              'run_verify': 1,
                              'priority': 'Medium',
                              'owner': 'user0',
                              'created_on': '2008-07-28 12:42:52',
                              'timeout': 144,
                              'synch_count': 1,
                              'id': 5964}])],
                     out_words_ok=['user0', 'Completed', '1', '5964',
                                   'Client', '2008', 'Priority'],
                     out_words_no=['sleeptest'])

    def test_job_list_jobs_name(self):
        self.run_cmd(argv=['atest', 'job', 'list', 'myt*',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'name__startswith': 'myt',
                                                 'running': None},
                            True,
                            [{'status_counts': {'Completed': 1},
                              'control_file': 'kernel = \'8210088647656509311.kernel-smp-2.6.18-220.5.x86_64.rpm\'\ndef step_init():\n    job.next_step([step_test])\n    testkernel = job.kernel(\'8210088647656509311.kernel-smp-2.6.18-220.5.x86_64.rpm\')\n    \n    testkernel.install()\n    testkernel.boot(args=\'console_always_print=1\')\n\ndef step_test():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "Autotest Team"\n    NAME = "Sleeptest"\n    TIME = "SHORT"\n    TEST_CATEGORY = "Functional"\n    TEST_CLASS = "General"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    This test simply sleeps for 1 second by default.  It\'s a good way to test\n    profilers and double check that autotest is working.\n    The seconds argument can also be modified to make the machine sleep for as\n    long as needed.\n    """\n    \n    job.run_test(\'sleeptest\',                             seconds = 1)',
                              'name': 'mytest',
                              'control_type': 'Client',
                              'run_verify': 1,
                              'priority': 'Medium',
                              'owner': 'user0',
                              'created_on': '2008-07-28 12:42:52',
                              'timeout': 144,
                              'synch_count': 1,
                              'id': 5964}])],
                     out_words_ok=['user0', 'Completed', '1', '5964'],
                     out_words_no=['sleeptest', 'Priority', 'Client', '2008'])

    def test_job_list_jobs_all_verbose(self):
        self.run_cmd(argv=['atest', 'job', 'list', '--all', '--verbose',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'running': None},
                            True, self.values)],
                     out_words_ok=['Fisto', 'Spikor', 'Cringer', 'Priority',
                                   'Created'])


class job_list_jobs_all_and_user_unittest(cli_mock.cli_unittest):

    def test_job_list_jobs_all_and_user(self):
        testjob = job.job_list()
        sys.argv = ['atest', 'job', 'list', '-a', '-u', 'user0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()


class job_stat_unittest(job_unittest):

    def test_job_stat_job(self):
        results = copy.deepcopy(self.results)
        self.run_cmd(argv=['atest', 'job', 'stat', '180',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['180']}, True,
                            [results[0]]),
                           ('get_host_queue_entries', {'job__in': ['180']},
                            True,
                            [{'status': 'Failed',
                              'complete': 1,
                              'host': {'status': 'Repair Failed',
                                        'locked': False,
                                        'hostname': 'host0',
                                        'invalid': True,
                                        'id': 4432,
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': "def run(machine):\n\thost = hosts.create_host(machine)\n\tat = autotest_remote.Autotest(host)\n\tat.run_test('sleeptest')\n\nparallel_simple(run, machines)",
                                       'name': 'test_sleep',
                                       'control_type': 'Server',
                                       'synchronizing': 0,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-03-18 11:27:29',
                                       'synch_count': 1,
                                       'id': 180},
                              'active': 0,
                              'id': 101084}])],
                     out_words_ok=['test_job0', 'host0', 'Failed',
                                   'Aborted'])

    def test_job_stat_list_unassigned_host(self):
        self.run_cmd(argv=['atest', 'job', 'stat', '6761',
                           '--list-hosts', '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['6761']}, True,
                            [{'status_counts': {'Queued': 1},
                              'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                              'name': 'test_on_meta_hosts',
                              'control_type': 'Client',
                              'run_verify': 1,
                              'priority': 'Medium',
                              'owner': 'user0',
                              'created_on': '2008-07-30 22:15:43',
                              'timeout': 144,
                              'synch_count': 1,
                              'id': 6761}]),
                           ('get_host_queue_entries', {'job__in': ['6761']},
                            True,
                            [{'status': 'Queued',
                              'complete': 0,
                              'deleted': 0,
                              'host': None,
                              'priority': 1,
                              'meta_host': 'Xeon',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193166}])],
                     err_words_ok=['unassigned', 'meta-hosts'],
                     out_words_no=['Xeon'])

    def test_job_stat_list_hosts(self):
        self.run_cmd(argv=['atest', 'job', 'stat', '6761',
                           '--list-hosts', '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['6761']}, True,
                            [{'status_counts': {'Queued': 1},
                              'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                              'name': 'test_on_meta_hosts',
                              'control_type': 'Client',
                              'run_verify': 1,
                              'priority': 'Medium',
                              'owner': 'user0',
                              'created_on': '2008-07-30 22:15:43',
                              'timeout': 144,
                              'synch_count': 1,
                              'id': 6761}]),
                           ('get_host_queue_entries', {'job__in': ['6761']},
                            True,
                            [{'status': 'Queued',
                              'complete': 0,
                              'deleted': 0,
                              'host': {'status': 'Running',
                                        'lock_time': None,
                                        'hostname': 'host41',
                                        'locked': False,
                                        'locked_by': None,
                                        'invalid': False,
                                        'id': 4833,
                                        'protection': 'Repair filesystem only',
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': 'Xeon',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193166},
                             {'status': 'Running',
                              'complete': 0,
                              'deleted': 0,
                              'host': {'status': 'Running',
                                        'lock_time': None,
                                        'hostname': 'host42',
                                        'locked': False,
                                        'locked_by': None,
                                        'invalid': False,
                                        'id': 4833,
                                        'protection': 'Repair filesystem only',
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': 'Xeon',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193166}])],
                     out_words_ok=['host41', 'host42'],
                     out_words_no=['Xeon', 'Running', 'Queued'],
                     err_words_no=['unassigned'])

    def test_job_stat_list_hosts_status(self):
        self.run_cmd(argv=['atest', 'job', 'stat', '6761',
                           '--list-hosts-status', 'Running,Queued',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['6761']}, True,
                            [{'status_counts': {'Queued': 1, 'Running': 1},
                              'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                              'name': 'test',
                              'control_type': 'Client',
                              'run_verify': 1,
                              'priority': 'Medium',
                              'owner': 'user0',
                              'created_on': '2008-07-30 22:15:43',
                              'timeout': 144,
                              'synch_count': 1,
                              'id': 6761}]),
                           ('get_host_queue_entries', {'job__in': ['6761']},
                            True,
                            [{'status': 'Queued',
                              'complete': 0,
                              'deleted': 0,
                              'host': {'status': 'Queued',
                                        'lock_time': None,
                                        'hostname': 'host41',
                                        'locked': False,
                                        'locked_by': None,
                                        'invalid': False,
                                        'id': 4833,
                                        'protection': 'Repair filesystem only',
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193166},
                             {'status': 'Running',
                              'complete': 0,
                              'deleted': 0,
                              'host': {'status': 'Running',
                                        'lock_time': None,
                                        'hostname': 'host42',
                                        'locked': False,
                                        'locked_by': None,
                                        'invalid': False,
                                        'id': 4833,
                                        'protection': 'Repair filesystem only',
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193166}])],
                     out_words_ok=['Queued', 'Running', 'host41', 'host42'],
                     out_words_no=['Xeon'],
                     err_words_no=['unassigned'])

    def test_job_stat_job_multiple_hosts(self):
        self.run_cmd(argv=['atest', 'job', 'stat', '6761',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['6761']}, True,
                            [{'status_counts': {'Running': 1,
                                                 'Queued': 4},
                              'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                              'name': 'test_on_meta_hosts',
                              'control_type': 'Client',
                              'run_verify': 1,
                              'priority': 'Medium',
                              'owner': 'user0',
                              'created_on': '2008-07-30 22:15:43',
                              'timeout': 144,
                              'synch_count': 1,
                              'id': 6761}]),
                           ('get_host_queue_entries', {'job__in': ['6761']},
                            True,
                            [{'status': 'Queued',
                              'complete': 0,
                              'deleted': 0,
                              'host': None,
                              'priority': 1,
                              'meta_host': 'Xeon',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193166},
                             {'status': 'Queued',
                              'complete': 0,
                              'deleted': 0,
                              'host': None,
                              'priority': 1,
                              'meta_host': 'Xeon',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193167},
                             {'status': 'Queued',
                              'complete': 0,
                              'deleted': 0,
                              'host': None,
                              'priority': 1,
                              'meta_host': 'Athlon',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193168},
                             {'status': 'Queued',
                              'complete': 0,
                              'deleted': 0,
                              'host': None,
                              'priority': 1,
                              'meta_host': 'x286',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 0,
                              'id': 193169},
                             {'status': 'Running',
                              'complete': 0,
                              'deleted': 0,
                              'host': {'status': 'Running',
                                        'lock_time': None,
                                        'hostname': 'host42',
                                        'locked': False,
                                        'locked_by': None,
                                        'invalid': False,
                                        'id': 4833,
                                        'protection': 'Repair filesystem only',
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': 'Athlon',
                              'job': {'control_file': 'def step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "mbligh@google.com (Martin Bligh)"\n    NAME = "Kernbench"\n    TIME = "SHORT"\n    TEST_CLASS = "Kernel"\n    TEST_CATEGORY = "Benchmark"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    A standard CPU benchmark. Runs a kernel compile and measures the performance.\n    """\n    \n    job.run_test(\'kernbench\')',
                                       'name': 'test_on_meta_hosts',
                                       'control_type': 'Client',
                                       'run_verify': 1,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-07-30 22:15:43',
                                       'timeout': 144,
                                       'synch_count': 1,
                                       'id': 6761},
                              'active': 1,
                              'id': 193170}])],
                     out_words_ok=['test_on_meta_hosts',
                                   'host42', 'Queued', 'Running'],
                     out_words_no=['Athlon', 'Xeon', 'x286'])

    def test_job_stat_job_no_host_in_qes(self):
        results = copy.deepcopy(self.results)
        self.run_cmd(argv=['atest', 'job', 'stat', '180',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['180']}, True,
                            [results[0]]),
                           ('get_host_queue_entries', {'job__in': ['180']},
                            True,
                            [{'status': 'Failed',
                              'complete': 1,
                              'host': None,
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': "def run(machine):\n\thost = hosts.create_host(machine)\n\tat = autotest_remote.Autotest(host)\n\tat.run_test('sleeptest')\n\nparallel_simple(run, machines)",
                                       'name': 'test_sleep',
                                       'control_type': 'Server',
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-03-18 11:27:29',
                                       'synch_count': 1,
                                       'id': 180},
                              'active': 0,
                              'id': 101084}])],
                     err_words_ok=['unassigned', 'meta-hosts'])

    def test_job_stat_multi_jobs(self):
        results = copy.deepcopy(self.results)
        self.run_cmd(argv=['atest', 'job', 'stat', '180', '338',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['180', '338']},
                            True, results),
                           ('get_host_queue_entries',
                            {'job__in': ['180', '338']},
                            True,
                            [{'status': 'Failed',
                              'complete': 1,
                              'host': {'status': 'Repair Failed',
                                        'locked': False,
                                        'hostname': 'host0',
                                        'invalid': True,
                                        'id': 4432,
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': "def run(machine):\n\thost = hosts.create_host(machine)\n\tat = autotest_remote.Autotest(host)\n\tat.run_test('sleeptest')\n\nparallel_simple(run, machines)",
                                       'name': 'test_sleep',
                                       'control_type': 'Server',
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-03-18 11:27:29',
                                       'synch_count': 1,
                                       'id': 180},
                              'active': 0,
                              'id': 101084},
                             {'status': 'Failed',
                              'complete': 1,
                              'host': {'status': 'Repair Failed',
                                        'locked': False,
                                        'hostname': 'host10',
                                        'invalid': True,
                                        'id': 4432,
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': "def run(machine):\n\thost = hosts.create_host(machine)\n\tat = autotest_remote.Autotest(host)\n\tat.run_test('sleeptest')\n\nparallel_simple(run, machines)",
                                       'name': 'test_sleep',
                                       'control_type': 'Server',
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-03-18 11:27:29',
                                       'synch_count': 1,
                                       'id': 338},
                              'active': 0,
                              'id': 101084}])],
                     out_words_ok=['test_job0', 'test_job1'])

    def test_job_stat_multi_jobs_name_id(self):
        self.run_cmd(argv=['atest', 'job', 'stat', 'mytest', '180',
                           '--ignore_site_file'],
                     rpcs=[('get_jobs_summary', {'id__in': ['180']},
                            True,
                            [{'status_counts': {'Aborted': 1},
                              'control_file':
                              "job.run_test('sleeptest')\n",
                              'name': 'job0',
                              'control_type': 'Server',
                              'priority':
                              'Medium',
                              'owner': 'user0',
                              'created_on':
                              '2008-07-08 17:45:44',
                              'synch_count': 2,
                              'id': 180}]),
                           ('get_jobs_summary', {'name__in': ['mytest']},
                            True,
                            [{'status_counts': {'Queued': 1},
                              'control_file':
                              "job.run_test('sleeptest')\n",
                              'name': 'mytest',
                              'control_type': 'Client',
                              'priority':
                              'High',
                              'owner': 'user0',
                              'created_on': '2008-07-08 12:17:47',
                              'synch_count': 1,
                              'id': 338}]),
                           ('get_host_queue_entries',
                            {'job__in': ['180']},
                            True,
                            [{'status': 'Failed',
                              'complete': 1,
                              'host': {'status': 'Repair Failed',
                                        'locked': False,
                                        'hostname': 'host0',
                                        'invalid': True,
                                        'id': 4432,
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': "def run(machine):\n\thost = hosts.create_host(machine)\n\tat = autotest_remote.Autotest(host)\n\tat.run_test('sleeptest')\n\nparallel_simple(run, machines)",
                                       'name': 'test_sleep',
                                       'control_type': 'Server',
                                       'synchronizing': 0,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-03-18 11:27:29',
                                       'synch_count': 1,
                                       'id': 180},
                              'active': 0,
                              'id': 101084}]),
                           ('get_host_queue_entries',
                            {'job__name__in': ['mytest']},
                            True,
                            [{'status': 'Failed',
                              'complete': 1,
                              'host': {'status': 'Repair Failed',
                                        'locked': False,
                                        'hostname': 'host10',
                                        'invalid': True,
                                        'id': 4432,
                                        'synch_id': None},
                              'priority': 1,
                              'meta_host': None,
                              'job': {'control_file': "def run(machine):\n\thost = hosts.create_host(machine)\n\tat = autotest_remote.Autotest(host)\n\tat.run_test('sleeptest')\n\nparallel_simple(run, machines)",
                                       'name': 'test_sleep',
                                       'control_type': 'Server',
                                       'synchronizing': 0,
                                       'priority': 'Medium',
                                       'owner': 'user0',
                                       'created_on': '2008-03-18 11:27:29',
                                       'synch_count': 1,
                                       'id': 338},
                              'active': 0,
                              'id': 101084}])],
                     out_words_ok=['job0', 'mytest', 'Aborted', 'Queued',
                                   'Failed', 'Medium', 'High'])


class job_create_unittest(cli_mock.cli_unittest):
    ctrl_file = '\ndef step_init():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "Autotest Team"\n    NAME = "Sleeptest"\n  TIME =\n    "SHORT"\n    TEST_CATEGORY = "Functional"\n    TEST_CLASS = "General"\n\n    TEST_TYPE = "client"\n \n    DOC = """\n    This test simply sleeps for 1\n    second by default.  It\'s a good way to test\n    profilers and double check\n    that autotest is working.\n The seconds argument can also be modified to\n    make the machine sleep for as\n    long as needed.\n    """\n   \n\n    job.run_test(\'sleeptest\', seconds = 1)'

    kernel_ctrl_file = 'kernel = \'kernel\'\ndef step_init():\n    job.next_step([step_test])\n    testkernel = job.kernel(\'kernel\')\n    \n    testkernel.install()\n    testkernel.boot(args=\'console_always_print=1\')\n\ndef step_test():\n    job.next_step(\'step0\')\n\ndef step0():\n    AUTHOR = "Autotest Team"\n    NAME = "Sleeptest"\n    TIME = "SHORT"\n    TEST_CATEGORY = "Functional"\n    TEST_CLASS = "General"\n    TEST_TYPE = "client"\n    \n    DOC = """\n    This test simply sleeps for 1 second by default.  It\'s a good way to test\n    profilers and double check that autotest is working.\n    The seconds argument can also be modified to make the machine sleep for as\n    long as needed.\n    """\n    \n    job.run_test(\'sleeptest\', seconds = 1)'

    trivial_ctrl_file = 'print "Hello"\n'

    data = {'priority': 'Medium', 'control_file': ctrl_file, 'hosts': ['host0'],
            'name': 'test_job0', 'control_type': 'Client', 'email_list': '',
            'meta_hosts': [], 'synch_count': 1, 'dependencies': []}

    def test_execute_create_job(self):
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           'test_job0', '-m', 'host0', '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest']},
                            True,
                            {'control_file': self.ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', self.data, True, 180)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])

    def test_execute_create_job_with_atomic_group(self):
        data = dict(self.data)
        data['atomic_group_name'] = 'my-atomic-group'
        data['control_type'] = 'Server'
        mock_ctrl_file = 'mock control file'
        data['control_file'] = mock_ctrl_file
        data['synch_count'] = 2
        data['hosts'] = []
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'mocktest',
                           'test_job0', '--ignore_site_file',
                           '-G', 'my-atomic-group'],
                     rpcs=[('generate_control_file',
                            {'tests': ['mocktest']},
                            True,
                            {'control_file': mock_ctrl_file,
                             'synch_count': 2,
                             'is_server': True,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])

    def test_execute_create_job_with_control(self):
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '--ignore_site_file'],
                     rpcs=[('create_job', self.data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_control_and_kernel(self):
        data = self.data.copy()
        data['control_file'] = '# Made up control "file" for unittest.'
        file_temp = cli_mock.create_file(self.trivial_ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           '-k', 'Kernel', 'test_job0', '-m', 'host0',
                           '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'client_control_file': self.trivial_ctrl_file,
                             'kernel': [{'version': 'Kernel'}]},
                            True,
                            {'control_file': data['control_file'],
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created',
                                   'Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_control_and_email(self):
        data = self.data.copy()
        data['email_list'] = 'em'
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '-e', 'em',
                           '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_control_and_dependencies(self):
        data = self.data.copy()
        data['dependencies'] = ['dep1', 'dep2']
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '-d', 'dep1, dep2 ',
                           '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_control_and_comma_dependencies(self):
        data = self.data.copy()
        data['dependencies'] = ['dep2,False', 'dep1,True']
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '-d',
                           'dep1\,True, dep2\,False ', '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_synch_count(self):
        data = self.data.copy()
        data['synch_count'] = 2
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '-y', '2',
                           '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_test_and_dependencies(self):
        data = self.data.copy()
        data['dependencies'] = ['dep1', 'dep2', 'dep3']
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           'test_job0', '-m', 'host0', '-d', 'dep1, dep2 ',
                           '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest']},
                            True,
                            {'control_file': self.ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': ['dep3']}),
                           ('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])

    def test_execute_create_job_with_test_and_comma_dependencies(self):
        data = self.data.copy()
        data['dependencies'] = ['dep1,True', 'dep2,False', 'dep3,123']
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           'test_job0', '-m', 'host0', '-d',
                           'dep1\,True dep2\,False ', '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest']},
                            True,
                            {'control_file': self.ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': ['dep3,123']}),
                           ('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])

    def test_execute_create_job_with_kernel(self):
        data = self.data.copy()
        data['control_file'] = self.kernel_ctrl_file
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           '-k', 'kernel', 'test_job0', '-m', 'host0',
                           '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest'],
                             'kernel': [{'version': 'kernel'}]
                             },
                            True,
                            {'control_file': self.kernel_ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     out_words_ok=['test_job0', 'Created',
                                   'Uploading', 'Done'])

    def test_execute_create_job_with_kernels_and_cmdline(self):
        data = self.data.copy()
        data['control_file'] = self.kernel_ctrl_file
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           '-k', 'kernel1,kernel2', '--kernel-cmdline',
                           'arg1 arg2', 'test_job0', '-m', 'host0',
                           '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest'],
                             'kernel': [{'version': 'kernel1',
                                         'cmdline': 'arg1 arg2'},
                                        {'version': 'kernel2',
                                         'cmdline': 'arg1 arg2'}]
                             },
                            True,
                            {'control_file': self.kernel_ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     out_words_ok=['test_job0', 'Created',
                                   'Uploading', 'Done'])

    def test_execute_create_job_with_2kernels_and_2config(self):
        data = self.data.copy()
        data['control_file'] = self.kernel_ctrl_file
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           '-k', 'kernel1,kernel2',
                           '--kernel-config', 'config1,config2',
                           '--kernel-cmdline', 'arg1 arg2',
                           'test_job0', '-m', 'host0', '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest'],
                             'kernel': [{'version': 'kernel1',
                                         'config_file': 'config1',
                                         'cmdline': 'arg1 arg2'},
                                        {'version': 'kernel2',
                                         'config_file': 'config2',
                                         'cmdline': 'arg1 arg2'}]
                             },
                            True,
                            {'control_file': self.kernel_ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     out_words_ok=['test_job0', 'Created',
                                   'Uploading', 'Done'])

    def test_execute_create_job_with_3kernels_and_explicit_none_config(self):
        data = self.data.copy()
        data['control_file'] = self.kernel_ctrl_file
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           '-k', 'kernel1,kernel2,kernel3',
                           '--kernel-config', 'config1,none,config3',
                           '--kernel-cmdline', 'arg1 arg2',
                           'test_job0', '-m', 'host0', '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest'],
                             'kernel': [{'version': 'kernel1',
                                         'config_file': 'config1',
                                         'cmdline': 'arg1 arg2'},
                                        {'version': 'kernel2',
                                         'cmdline': 'arg1 arg2'},
                                        {'version': 'kernel3',
                                         'config_file': 'config3',
                                         'cmdline': 'arg1 arg2'}]
                             },
                            True,
                            {'control_file': self.kernel_ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     out_words_ok=['test_job0', 'Created',
                                   'Uploading', 'Done'])

    def test_execute_create_job_with_kernel_spaces(self):
        data = self.data.copy()
        data['control_file'] = self.kernel_ctrl_file
        data['name'] = 'test job    with  spaces'
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           '-k', 'kernel', 'test job    with  spaces',
                           '-m', 'host0', '--ignore_site_file'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest'],
                             'kernel': [{'version': 'kernel'}]
                             },
                            True,
                            {'control_file': self.kernel_ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     # This is actually 7 spaces, the extra single quote that
                     # gets displayed before "test" causes the tab completion
                     # to move to the next 8 char boundary which is 7 characters
                     # away. Hence the 7 spaces in out_words_ok.
                     # The tab has been converted by print.
                     out_words_ok=['test job    with  spaces', 'Created',
                                   'id', '180'])

    def test_execute_create_job_no_args(self):
        testjob = job.job_create()
        sys.argv = ['atest', 'job', 'create']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()

    def test_execute_create_job_no_hosts(self):
        testjob = job.job_create()
        file_temp = cli_mock.create_file(self.ctrl_file)
        sys.argv = ['atest', '-f', file_temp.name, 'test_job0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()
        file_temp.clean()

    def test_execute_create_job_cfile_and_tests(self):
        testjob = job.job_create()
        sys.argv = ['atest', 'job', 'create', '-t', 'sleeptest', '-f',
                    'control_file', 'test_job0', '-m', 'host0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()

    def test_execute_create_job_cfile_and_kernel(self):
        testjob = job.job_create()
        sys.argv = ['atest', 'job', 'create', '-f', 'control_file', '-k',
                    'kernel', 'test_job0', '-m', 'host0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()

    def test_execute_create_job_more_kernels_than_configs(self):
        testjob = job.job_create()
        sys.argv = ['atest', 'job', 'create', '-f', 'control_file', '-k',
                    'kernel1,kernel2', '--kernel-config', 'config1',
                    'test_job0', '-m', 'host0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()

    def test_execute_create_job_bad_cfile(self):
        testjob = job.job_create()
        sys.argv = ['atest', 'job', 'create', '-f', 'control_file',
                    'test_job0', '-m', 'host0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(IOError))
        self.assertRaises(IOError, testjob.parse)
        self.god.unmock_io()

    def test_execute_create_job_bad_priority(self):
        testjob = job.job_create()
        sys.argv = ['atest', 'job', 'create', '-t', 'sleeptest', '-p', 'Uber',
                    '-m', 'host0', 'test_job0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()

    def test_execute_create_job_with_mfile(self):
        data = self.data.copy()
        data['hosts'] = ['host3', 'host2', 'host1', 'host0']
        ctemp = cli_mock.create_file(self.ctrl_file)
        file_temp = cli_mock.create_file('host0\nhost1\nhost2\nhost3')
        self.run_cmd(argv=['atest', 'job', 'create', '--mlist', file_temp.name,
                           '-f', ctemp.name, 'test_job0', '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'])
        ctemp.clean()
        file_temp.clean()

    def test_execute_create_job_with_timeout(self):
        data = self.data.copy()
        data['timeout'] = '222'
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '-o', '222',
                           '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],)
        file_temp.clean()

    def test_execute_create_job_with_max_runtime(self):
        data = self.data.copy()
        data['max_runtime_hrs'] = '222'
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '--max_runtime', '222',
                           '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],)
        file_temp.clean()

    def test_execute_create_job_with_noverify(self):
        data = self.data.copy()
        data['run_verify'] = False
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '-n',
                           '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],)
        file_temp.clean()

    def test_execute_create_job_oth(self):
        data = self.data.copy()
        data['hosts'] = []
        data['one_time_hosts'] = ['host0']
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           'test_job0', '--one-time-hosts', 'host0'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest']},
                            True,
                            {'control_file': self.ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])

    def test_execute_create_job_multi_oth(self):
        data = self.data.copy()
        data['hosts'] = []
        data['one_time_hosts'] = ['host1', 'host0']
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           'test_job0', '--one-time-hosts', 'host0,host1'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest']},
                            True,
                            {'control_file': self.ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, True, 180)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])

    def test_execute_create_job_oth_exists(self):
        data = self.data.copy()
        data['hosts'] = []
        data['one_time_hosts'] = ['host0']
        self.run_cmd(argv=['atest', 'job', 'create', '-t', 'sleeptest',
                           'test_job0', '--one-time-hosts', 'host0'],
                     rpcs=[('generate_control_file',
                            {'tests': ['sleeptest']},
                            True,
                            {'control_file': self.ctrl_file,
                             'synch_count': 1,
                             'is_server': False,
                             'dependencies': []}),
                           ('create_job', data, False,
                            '''ValidationError: {'hostname': 'host0 '''
                            '''already exists in the autotest DB.  '''
                            '''Select it rather than entering it as '''
                            '''a one time host.'}''')],
                     out_words_no=['test_job0', 'Created'],
                     err_words_ok=['failed', 'already exists'])

    def test_execute_create_job_with_control_and_labels(self):
        data = self.data.copy()
        data['hosts'] = ['host0', 'host1', 'host2']
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0', '-b', 'label1,label2',
                           '--ignore_site_file'],
                     rpcs=[('get_hosts', {'multiple_labels': ['label1',
                                                              'label2']}, True,
                            [{'status': 'Running', 'lock_time': None,
                              'hostname': 'host1', 'locked': False,
                              'locked_by': None, 'invalid': False, 'id': 42,
                              'labels': ['label1'], 'platform':
                              'Warp18_Diskfull', 'protection':
                              'Repair software only', 'dirty':
                              True, 'synch_id': None},
                             {'status': 'Running', 'lock_time': None,
                              'hostname': 'host2', 'locked': False,
                              'locked_by': None, 'invalid': False, 'id': 43,
                              'labels': ['label2'], 'platform':
                              'Warp18_Diskfull', 'protection':
                              'Repair software only', 'dirty': True,
                              'synch_id': None}]),
                           ('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_label_and_duplicate_hosts(self):
        data = self.data.copy()
        data['hosts'] = ['host1', 'host0']
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0,host1', '-b', 'label1',
                           '--ignore_site_file'],
                     rpcs=[('get_hosts', {'multiple_labels': ['label1']}, True,
                            [{'status': 'Running', 'lock_time': None,
                              'hostname': 'host1', 'locked': False,
                              'locked_by': None, 'invalid': False, 'id': 42,
                              'labels': ['label1'], 'platform':
                              'Warp18_Diskfull', 'protection':
                              'Repair software only', 'dirty':
                              True, 'synch_id': None}]),
                           ('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_label_commas_and_duplicate_hosts(self):
        data = self.data.copy()
        data['hosts'] = ['host1', 'host0']
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0,host1', '-b',
                           'label1,label\\,2', '--ignore_site_file'],
                     rpcs=[('get_hosts', {'multiple_labels': ['label1',
                                                              'label,2']}, True,
                            [{'status': 'Running', 'lock_time': None,
                              'hostname': 'host1', 'locked': False,
                              'locked_by': None, 'invalid': False, 'id': 42,
                              'labels': ['label1', 'label,2'], 'platform':
                              'Warp18_Diskfull', 'protection':
                              'Repair software only', 'dirty':
                              True, 'synch_id': None}]),
                           ('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def test_execute_create_job_with_label_escaping_and_duplicate_hosts(self):
        data = self.data.copy()
        data['hosts'] = ['host1', 'host0']
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-f', file_temp.name,
                           'test_job0', '-m', 'host0,host1', '-b',
                           'label1,label\\,2\\\\,label3', '--ignore_site_file'],
                     rpcs=[('get_hosts', {'multiple_labels': ['label,2\\',
                                                              'label1', 'label3']}, True,
                            [{'status': 'Running', 'lock_time': None,
                              'hostname': 'host1', 'locked': False,
                              'locked_by': None, 'invalid': False, 'id': 42,
                              'labels': ['label1', 'label,2\\', 'label3'],
                              'platform': 'Warp18_Diskfull', 'protection':
                              'Repair software only', 'dirty':
                              True, 'synch_id': None}]),
                           ('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()

    def _test_parse_hosts(self, args, exp_hosts=[], exp_meta_hosts=[]):
        testjob = job.job_create_or_clone()
        (hosts, meta_hosts) = testjob._parse_hosts(args)
        self.assertEqualNoOrder(hosts, exp_hosts)
        self.assertEqualNoOrder(meta_hosts, exp_meta_hosts)

    def test_parse_hosts_regular(self):
        self._test_parse_hosts(['host0'], ['host0'])

    def test_parse_hosts_regulars(self):
        self._test_parse_hosts(['host0', 'host1'], ['host0', 'host1'])

    def test_parse_hosts_meta_one(self):
        self._test_parse_hosts(['*meta0'], [], ['meta0'])

    def test_parse_hosts_meta_five(self):
        self._test_parse_hosts(['5*meta0'], [], ['meta0'] * 5)

    def test_parse_hosts_metas_five(self):
        self._test_parse_hosts(['5*meta0', '2*meta1'], [],
                               ['meta0'] * 5 + ['meta1'] * 2)

    def test_parse_hosts_mix(self):
        self._test_parse_hosts(['5*meta0', 'host0', '2*meta1', 'host1',
                                '*meta2'], ['host0', 'host1'],
                               ['meta0'] * 5 + ['meta1'] * 2 + ['meta2'])

    def test_parse_hosts_metas_labels_wildcards(self):
        values = [{'id': 180,
                   'platform': False,
                   'name': 'label0',
                   'invalid': False,
                   'kernel_config': ''},
                  {'id': 338,
                   'platform': False,
                   'name': 'label1',
                   'invalid': False,
                   'kernel_config': ''}]
        testjob = job.job_create_or_clone()
        testjob.afe = rpc.afe_comm()
        self.mock_rpcs([('get_labels', {'name__startswith': 'label'},
                         True, values)])
        (unused_hosts, meta_hosts) = testjob._parse_hosts(['3*label*'])
        self.assertEqualNoOrder(meta_hosts, ['label0'] * 3 + ['label1'] * 3)

    def test_parse_hosts_metas_labels_wildcards_not_found(self):
        testjob = job.job_create_or_clone()
        testjob.afe = rpc.afe_comm()
        self.mock_rpcs([('get_labels', {'name__startswith': 'label'},
                         True, [])])
        testjob._parse_hosts(['3*label*'])
        self.assertEqual(testjob.failed['Failed to find labels'],
                         {'No labels matching <XYZ>': set(['label*'])})

    def test_execute_create_job_hostless(self):
        data = self.data.copy()
        data['hostless'] = True
        data['hosts'] = []
        data['control_type'] = 'Server'
        del data['synch_count']
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create', '-s', '-f', file_temp.name,
                           '--hostless', 'test_job0'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],)
        file_temp.clean()

    def test_execute_create_job_hostless_bad_args_hosts(self):
        testjob = job.job_create()
        file_temp = cli_mock.create_file(self.ctrl_file)
        sys.argv = ['atest', 'job', 'create', '--hostless',
                    '-s', '-f', file_temp.name,
                    '-m', 'myhost',
                    'test_hosteless_job0']
        self.god.mock_io()
        (sys.exit.expect_call(mock.anything_comparator())
         .and_raises(cli_mock.ExitException))
        self.assertRaises(cli_mock.ExitException, testjob.parse)
        self.god.unmock_io()
        self.god.check_playback()
        file_temp.clean()

    def test_execute_create_job_reserve_hosts(self):
        data = self.data.copy()
        data['reserve_hosts'] = True
        file_temp = cli_mock.create_file(self.ctrl_file)
        self.run_cmd(argv=['atest', 'job', 'create',
                           '-f', file_temp.name,
                           'test_job0', '-m', 'host0',
                           '--reserve-hosts',
                           '--ignore_site_file'],
                     rpcs=[('create_job', data, True, 42)],
                     out_words_ok=['test_job0', 'Created'],
                     out_words_no=['Uploading', 'Done'])
        file_temp.clean()


class job_clone_unittest(cli_mock.cli_unittest):
    job_data = {'control_file': 'NAME = \'Server Sleeptest\'\nAUTHOR = \'mbligh@google.com (Martin Bligh)\'\nTIME = \'SHORT\'\nTEST_CLASS = \'Software\'\nTEST_CATEGORY = \'Functional\'\nTEST_TYPE = \'server\'\nEXPERIMENTAL = \'False\'\n\nDOC = """\nruns sleep for one second on the list of machines.\n"""\n\ndef run(machine):\n    host = hosts.create_host(machine)\n    job.run_test(\'sleeptest\')\n\njob.parallel_simple(run, machines)\n',
                'control_type': 'Server',
                'dependencies': [],
                'email_list': '',
                'max_runtime_hrs': 480,
                'parse_failed_repair': True,
                'priority': 'Medium',
                'reboot_after': 'Always',
                'reboot_before': 'If dirty',
                'run_verify': True,
                'synch_count': 1,
                'timeout': 480}

    local_hosts = [{'acls': ['acl0'],
                    'atomic_group': None,
                    'attributes': {},
                    'dirty': False,
                    'hostname': 'host0',
                    'id': 8,
                    'invalid': False,
                    'labels': ['label0', 'label1'],
                    'lock_time': None,
                    'locked': False,
                    'locked_by': None,
                    'other_labels': 'label0, label1',
                    'platform': 'plat0',
                    'protection': 'Repair software only',
                    'status': 'Ready',
                    'synch_id': None},
                   {'acls': ['acl0'],
                    'atomic_group': None,
                    'attributes': {},
                    'dirty': False,
                    'hostname': 'host1',
                    'id': 9,
                    'invalid': False,
                    'labels': ['label0', 'label1'],
                    'lock_time': None,
                    'locked': False,
                    'locked_by': None,
                    'other_labels': 'label0, label1',
                    'platform': 'plat0',
                    'protection': 'Repair software only',
                    'status': 'Ready',
                    'synch_id': None}]

    def setUp(self):
        super(job_clone_unittest, self).setUp()
        self.job_data_clone_info = copy.deepcopy(self.job_data)
        self.job_data_clone_info['created_on'] = '2009-07-23 16:21:29'
        self.job_data_clone_info['name'] = 'testing_clone'
        self.job_data_clone_info['id'] = 42
        self.job_data_clone_info['owner'] = 'user0'

        self.job_data_cloned = copy.deepcopy(self.job_data)
        self.job_data_cloned['name'] = 'cloned'
        self.job_data_cloned['hosts'] = ['host0']
        self.job_data_cloned['meta_hosts'] = []

    def test_backward_compat(self):
        self.run_cmd(argv=['atest', 'job', 'create', '--clone', '42',
                           '-r', 'cloned'],
                     rpcs=[('get_info_for_clone', {'id': '42',
                                                   'preserve_metahosts': True},
                            True,
                            {'atomic_group_name': None,
                             'hosts': [{'acls': ['acl0'],
                                         'atomic_group': None,
                                         'attributes': {},
                                         'dirty': False,
                                         'hostname': 'host0',
                                         'id': 4378,
                                         'invalid': False,
                                         'labels': ['label0', 'label1'],
                                         'lock_time': None,
                                         'locked': False,
                                         'locked_by': None,
                                         'other_labels': 'label0, label1',
                                         'platform': 'plat0',
                                         'protection': 'Repair software only',
                                         'status': 'Ready',
                                         'synch_id': None}],
                             'job': self.job_data_clone_info,
                             'meta_host_counts': {}}),
                           ('create_job', self.job_data_cloned, True, 43)],
                     out_words_ok=['Created job', '43'])

    def test_clone_reuse_hosts(self):
        self.job_data_cloned['hosts'] = ['host0', 'host1']
        self.run_cmd(argv=['atest', 'job', 'clone', '--id', '42',
                           '-r', 'cloned'],
                     rpcs=[('get_info_for_clone', {'id': '42',
                                                   'preserve_metahosts': True},
                            True,
                            {'atomic_group_name': None,
                             'hosts': self.local_hosts,
                             'job': self.job_data_clone_info,
                             'meta_host_counts': {}}),
                           ('create_job', self.job_data_cloned, True, 43)],
                     out_words_ok=['Created job', '43'])

    def test_clone_reuse_metahosts(self):
        self.job_data_cloned['hosts'] = []
        self.job_data_cloned['meta_hosts'] = ['type1'] * 4 + ['type0']
        self.run_cmd(argv=['atest', 'job', 'clone', '--id', '42',
                           '-r', 'cloned'],
                     rpcs=[('get_info_for_clone', {'id': '42',
                                                   'preserve_metahosts': True},
                            True,
                            {'atomic_group_name': None,
                             'hosts': [],
                             'job': self.job_data_clone_info,
                             'meta_host_counts': {'type0': 1,
                                                   'type1': 4}}),
                           ('create_job', self.job_data_cloned, True, 43)],
                     out_words_ok=['Created job', '43'])

    def test_clone_reuse_both(self):
        self.job_data_cloned['hosts'] = ['host0', 'host1']
        self.job_data_cloned['meta_hosts'] = ['type1'] * 4 + ['type0']
        self.run_cmd(argv=['atest', 'job', 'clone', '--id', '42',
                           '-r', 'cloned'],
                     rpcs=[('get_info_for_clone', {'id': '42',
                                                   'preserve_metahosts': True},
                            True,
                            {'atomic_group_name': None,
                             'hosts': self.local_hosts,
                             'job': self.job_data_clone_info,
                             'meta_host_counts': {'type0': 1,
                                                   'type1': 4}}),
                           ('create_job', self.job_data_cloned, True, 43)],
                     out_words_ok=['Created job', '43'])

    def test_clone_no_hosts(self):
        self.run_cmd(argv=['atest', 'job', 'clone', '--id', '42', 'cloned'],
                     exit_code=1,
                     out_words_ok=['usage'],
                     err_words_ok=['machine'])

    def test_clone_reuse_and_hosts(self):
        self.run_cmd(argv=['atest', 'job', 'clone', '--id', '42',
                           '-r', '-m', 'host5', 'cloned'],
                     exit_code=1,
                     out_words_ok=['usage'],
                     err_words_ok=['specify'])

    def test_clone_new_multiple_hosts(self):
        self.job_data_cloned['hosts'] = ['host5', 'host4', 'host3']
        self.run_cmd(argv=['atest', 'job', 'clone', '--id', '42',
                           '-m', 'host5,host4,host3', 'cloned'],
                     rpcs=[('get_info_for_clone', {'id': '42',
                                                   'preserve_metahosts': False},
                            True,
                            {'atomic_group_name': None,
                             'hosts': self.local_hosts,
                             'job': self.job_data_clone_info,
                             'meta_host_counts': {}}),
                           ('create_job', self.job_data_cloned, True, 43)],
                     out_words_ok=['Created job', '43'])

    def test_clone_oth(self):
        self.job_data_cloned['hosts'] = []
        self.job_data_cloned['one_time_hosts'] = ['host5']
        self.run_cmd(argv=['atest', 'job', 'clone', '--id', '42',
                           '--one-time-hosts', 'host5', 'cloned'],
                     rpcs=[('get_info_for_clone', {'id': '42',
                                                   'preserve_metahosts': False},
                            True,
                            {'atomic_group_name': None,
                             'hosts': self.local_hosts,
                             'job': self.job_data_clone_info,
                             'meta_host_counts': {}}),
                           ('create_job', self.job_data_cloned, True, 43)],
                     out_words_ok=['Created job', '43'])


class job_abort_unittest(cli_mock.cli_unittest):
    results = [{'status_counts': {'Aborted': 1}, 'control_file':
                "job.run_test('sleeptest')\n", 'name': 'test_job0',
                'control_type': 'Server', 'priority':
                'Medium', 'owner': 'user0', 'created_on':
                '2008-07-08 17:45:44', 'synch_count': 2, 'id': 180}]

    def test_execute_job_abort(self):
        self.run_cmd(argv=['atest', 'job', 'abort', '180',
                           '--ignore_site_file'],
                     rpcs=[('abort_host_queue_entries',
                            {'job__id__in': ['180']}, True, None)],
                     out_words_ok=['Aborting', '180'])


if __name__ == '__main__':
    unittest.main()

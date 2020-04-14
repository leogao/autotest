#!/usr/bin/python3
#
# Copyright 2008 Google Inc. All Rights Reserved.

"""Tests for test."""

import unittest

try:
    import autotest.common as common  # pylint: disable=W0611
except ImportError:
    from . import common  # pylint: disable=W0611
from autotest.cli import cli_mock


class test_list_unittest(cli_mock.cli_unittest):
    values = [{'description': 'unknown',
               'test_type': 'Client',
               'test_class': 'Canned Test Sets',
               'path': 'client/tests/test0/control',
               'synch_type': 'Asynchronous',
               'id': 138,
               'name': 'test0',
               'experimental': False},
              {'description': 'unknown',
               'test_type': 'Server',
               'test_class': 'Kernel',
               'path': 'server/tests/test1/control',
               'synch_type': 'Asynchronous',
               'id': 139,
               'name': 'test1',
               'experimental': False},
              {'description': 'unknown',
               'test_type': 'Client',
               'test_class': 'Canned Test Sets',
               'path': 'client/tests/test2/control.readprofile',
               'synch_type': 'Asynchronous',
               'id': 140,
               'name': 'test2',
               'experimental': False},
              {'description': 'unknown',
               'test_type': 'Server',
               'test_class': 'Canned Test Sets',
               'path': 'server/tests/test3/control',
               'synch_type': 'Asynchronous',
               'id': 142,
               'name': 'test3',
               'experimental': False},
              {'description': 'Random stuff to check that things are ok',
               'test_type': 'Client',
               'test_class': 'Hardware',
               'path': 'client/tests/test4/control.export',
               'synch_type': 'Asynchronous',
               'id': 143,
               'name': 'test4',
               'experimental': True}]

    def test_test_list_tests_default(self):
        self.run_cmd(argv=['atest', 'test', 'list'],
                     rpcs=[('get_tests', {'experimental': False},
                            True, self.values)],
                     out_words_ok=['test0', 'test1', 'test2',
                                   'test3', 'test4'],
                     out_words_no=['Random', 'control.export'])

    def test_test_list_tests_all(self):
        self.run_cmd(argv=['atest', 'test', 'list', '--all'],
                     rpcs=[('get_tests', {},
                            True, self.values)],
                     out_words_ok=['test0', 'test1', 'test2',
                                   'test3', 'test4'],
                     out_words_no=['Random', 'control.export'])

    def test_test_list_tests_exp(self):
        self.run_cmd(argv=['atest', 'test', 'list', '--experimental'],
                     rpcs=[('get_tests', {'experimental': True},
                            True,
                            [{'description': 'Random stuff',
                              'test_type': 'Client',
                              'test_class': 'Hardware',
                              'path': 'client/tests/test4/control.export',
                              'synch_type': 'Asynchronous',
                              'id': 143,
                              'name': 'test4',
                              'experimental': True}])],
                     out_words_ok=['test4'],
                     out_words_no=['Random', 'control.export'])

    def test_test_list_tests_select_one(self):
        filtered = [val for val in self.values if val['name'] in ['test3']]
        self.run_cmd(argv=['atest', 'test', 'list', 'test3'],
                     rpcs=[('get_tests', {'name__in': ['test3'],
                                          'experimental': False},
                            True, filtered)],
                     out_words_ok=['test3'],
                     out_words_no=['test0', 'test1', 'test2', 'test4',
                                   'unknown'])

    def test_test_list_tests_select_two(self):
        filtered = [val for val in self.values
                    if val['name'] in ['test3', 'test1']]
        self.run_cmd(argv=['atest', 'test', 'list', 'test3,test1'],
                     rpcs=[('get_tests', {'name__in': ['test1', 'test3'],
                                          'experimental': False},
                            True, filtered)],
                     out_words_ok=['test3', 'test1', 'Server'],
                     out_words_no=['test0', 'test2', 'test4',
                                   'unknown', 'Client'])

    def test_test_list_tests_select_two_space(self):
        filtered = [val for val in self.values
                    if val['name'] in ['test3', 'test1']]
        self.run_cmd(argv=['atest', 'test', 'list', 'test3', 'test1'],
                     rpcs=[('get_tests', {'name__in': ['test1', 'test3'],
                                          'experimental': False},
                            True, filtered)],
                     out_words_ok=['test3', 'test1', 'Server'],
                     out_words_no=['test0', 'test2', 'test4',
                                   'unknown', 'Client'])

    def test_test_list_tests_all_verbose(self):
        self.run_cmd(argv=['atest', 'test', 'list', '-v'],
                     rpcs=[('get_tests', {'experimental': False},
                            True, self.values)],
                     out_words_ok=['test0', 'test1', 'test2',
                                   'test3', 'test4', 'client/tests',
                                   'server/tests'],
                     out_words_no=['Random'])

    def test_test_list_tests_all_desc(self):
        self.run_cmd(argv=['atest', 'test', 'list', '-d'],
                     rpcs=[('get_tests', {'experimental': False},
                            True, self.values)],
                     out_words_ok=['test0', 'test1', 'test2',
                                   'test3', 'test4', 'unknown', 'Random'],
                     out_words_no=['client/tests', 'server/tests'])

    def test_test_list_tests_all_desc_verbose(self):
        self.run_cmd(argv=['atest', 'test', 'list', '-d', '-v'],
                     rpcs=[('get_tests', {'experimental': False},
                            True, self.values)],
                     out_words_ok=['test0', 'test1', 'test2',
                                   'test3', 'test4', 'client/tests',
                                   'server/tests', 'unknown', 'Random'])


if __name__ == '__main__':
    unittest.main()

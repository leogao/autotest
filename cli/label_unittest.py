#!/usr/bin/python3
#
# Copyright 2008 Google Inc. All Rights Reserved.

"""Tests for label."""

import unittest

try:
    import autotest.common as common  # pylint: disable=W0611
except ImportError:
    from . import common  # pylint: disable=W0611
from autotest.cli import cli_mock


class label_list_unittest(cli_mock.cli_unittest):
    values = [{'id': 180,          # Valid label
               'platform': False,
               'name': 'label0',
               'invalid': False,
               'kernel_config': '',
               'only_if_needed': False},
              {'id': 338,          # Valid label
               'platform': False,
               'name': 'label1',
               'invalid': False,
               'kernel_config': '',
               'only_if_needed': False},
              {'id': 340,          # Invalid label
               'platform': False,
               'name': 'label2',
               'invalid': True,
               'kernel_config': '',
               'only_if_needed': False},
              {'id': 350,          # Valid platform
               'platform': True,
               'name': 'plat0',
               'invalid': False,
               'kernel_config': '',
               'only_if_needed': False},
              {'id': 420,          # Invalid platform
               'platform': True,
               'name': 'plat1',
               'invalid': True,
               'kernel_config': '',
               'only_if_needed': False}]

    def test_label_list_labels_only(self):
        self.run_cmd(argv=['atest', 'label', 'list', '--ignore_site_file'],
                     rpcs=[('get_labels', {}, True, self.values)],
                     out_words_ok=['label0', 'label1', 'label2'],
                     out_words_no=['plat0', 'plat1'])

    def test_label_list_labels_only_valid(self):
        self.run_cmd(argv=['atest', 'label', 'list', '-d',
                           '--ignore_site_file'],
                     rpcs=[('get_labels', {}, True, self.values)],
                     out_words_ok=['label0', 'label1'],
                     out_words_no=['label2', 'plat0', 'plat1'])

    def test_label_list_labels_and_platforms(self):
        self.run_cmd(argv=['atest', 'label', 'list', '--all',
                           '--ignore_site_file'],
                     rpcs=[('get_labels', {}, True, self.values)],
                     out_words_ok=['label0', 'label1', 'label2',
                                   'plat0', 'plat1'])

    def test_label_list_platforms_only(self):
        self.run_cmd(argv=['atest', 'label', 'list', '-t',
                           '--ignore_site_file'],
                     rpcs=[('get_labels', {}, True, self.values)],
                     out_words_ok=['plat0', 'plat1'],
                     out_words_no=['label0', 'label1', 'label2'])

    def test_label_list_platforms_only_valid(self):
        self.run_cmd(argv=['atest', 'label', 'list',
                           '-t', '--valid-only', '--ignore_site_file'],
                     rpcs=[('get_labels', {}, True, self.values)],
                     out_words_ok=['plat0'],
                     out_words_no=['label0', 'label1', 'label2',
                                   'plat1'])


class label_create_unittest(cli_mock.cli_unittest):

    def test_execute_create_two_labels(self):
        self.run_cmd(argv=['atest', 'label', 'create', 'label0', 'label1',
                           '--ignore_site_file'],
                     rpcs=[('add_label',
                            {'name': 'label0', 'platform': False,
                             'only_if_needed': False},
                            True, 42),
                           ('add_label',
                            {'name': 'label1', 'platform': False,
                             'only_if_needed': False},
                            True, 43)],
                     out_words_ok=['Created', 'label0', 'label1'])

    def test_execute_create_two_labels_bad(self):
        self.run_cmd(argv=['atest', 'label', 'create', 'label0', 'label1',
                           '--ignore_site_file'],
                     rpcs=[('add_label',
                            {'name': 'label0', 'platform': False,
                             'only_if_needed': False},
                            True, 3),
                           ('add_label',
                            {'name': 'label1', 'platform': False,
                             'only_if_needed': False},
                            False,
                            '''ValidationError: {'name':
                            'This value must be unique (label0)'}''')],
                     out_words_ok=['Created', 'label0'],
                     out_words_no=['label1'],
                     err_words_ok=['label1', 'ValidationError'])


class label_delete_unittest(cli_mock.cli_unittest):

    def test_execute_delete_labels(self):
        self.run_cmd(argv=['atest', 'label', 'delete', 'label0', 'label1',
                           '--ignore_site_file'],
                     rpcs=[('delete_label', {'id': 'label0'}, True, None),
                           ('delete_label', {'id': 'label1'}, True, None)],
                     out_words_ok=['Deleted', 'label0', 'label1'])


class label_add_unittest(cli_mock.cli_unittest):

    def test_execute_add_labels_to_hosts(self):
        self.run_cmd(argv=['atest', 'label', 'add', 'label0',
                           '--machine', 'host0,host1', '--ignore_site_file'],
                     rpcs=[('label_add_hosts', {'id': 'label0',
                                                'hosts': ['host1', 'host0']},
                            True, None)],
                     out_words_ok=['Added', 'label0', 'host0', 'host1'])


class label_remove_unittest(cli_mock.cli_unittest):

    def test_execute_remove_labels_from_hosts(self):
        self.run_cmd(argv=['atest', 'label', 'remove', 'label0',
                           '--machine', 'host0,host1', '--ignore_site_file'],
                     rpcs=[('label_remove_hosts', {'id': 'label0',
                                                   'hosts': ['host1', 'host0']},
                            True, None)],
                     out_words_ok=['Removed', 'label0', 'host0', 'host1'])


if __name__ == '__main__':
    unittest.main()

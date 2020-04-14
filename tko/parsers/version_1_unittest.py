#!/usr/bin/python3

import datetime
import time
import unittest

try:
    import autotest.common as common  # pylint: disable=W0611
except ImportError:
    from . import common  # pylint: disable=W0611
from autotest.client.shared import utils
from autotest.tko.parsers import version_1


class test_status_line(unittest.TestCase):
    statuses = ["GOOD", "WARN", "FAIL", "ABORT"]

    def test_handles_start(self):
        line = version_1.status_line(0, "START", "----", "test",
                                     "", {})
        self.assertEqual(line.type, "START")
        self.assertEqual(line.status, None)

    def test_handles_info(self):
        line = version_1.status_line(0, "INFO", "----", "----",
                                     "", {})
        self.assertEqual(line.type, "INFO")
        self.assertEqual(line.status, None)

    def test_handles_status(self):
        for stat in self.statuses:
            line = version_1.status_line(0, stat, "----", "test",
                                         "", {})
            self.assertEqual(line.type, "STATUS")
            self.assertEqual(line.status, stat)

    def test_handles_endstatus(self):
        for stat in self.statuses:
            line = version_1.status_line(0, "END " + stat, "----",
                                         "test", "", {})
            self.assertEqual(line.type, "END")
            self.assertEqual(line.status, stat)

    def test_fails_on_bad_status(self):
        for stat in self.statuses:
            self.assertRaises(AssertionError,
                              version_1.status_line, 0,
                              "BAD " + stat, "----", "test",
                              "", {})

    def test_saves_all_fields(self):
        line = version_1.status_line(5, "GOOD", "subdir_name",
                                     "test_name", "my reason here",
                                     {"key1": "value",
                                      "key2": "another value",
                                      "key3": "value3"})
        self.assertEqual(line.indent, 5)
        self.assertEqual(line.status, "GOOD")
        self.assertEqual(line.subdir, "subdir_name")
        self.assertEqual(line.testname, "test_name")
        self.assertEqual(line.reason, "my reason here")
        self.assertEqual(line.optional_fields,
                          {"key1": "value", "key2": "another value",
                           "key3": "value3"})

    def test_parses_blank_subdir(self):
        line = version_1.status_line(0, "GOOD", "----", "test",
                                     "", {})
        self.assertEqual(line.subdir, None)

    def test_parses_blank_testname(self):
        line = version_1.status_line(0, "GOOD", "subdir", "----",
                                     "", {})
        self.assertEqual(line.testname, None)

    def test_parse_line_smoketest(self):
        input_data = ("\t\t\tGOOD\t----\t----\t"
                      "field1=val1\tfield2=val2\tTest Passed")
        line = version_1.status_line.parse_line(input_data)
        self.assertEqual(line.indent, 3)
        self.assertEqual(line.type, "STATUS")
        self.assertEqual(line.status, "GOOD")
        self.assertEqual(line.subdir, None)
        self.assertEqual(line.testname, None)
        self.assertEqual(line.reason, "Test Passed")
        self.assertEqual(line.optional_fields,
                          {"field1": "val1", "field2": "val2"})

    def test_parse_line_handles_newline(self):
        input_data = ("\t\tGOOD\t----\t----\t"
                      "field1=val1\tfield2=val2\tNo newline here!")
        for suffix in ("", "\n"):
            line = version_1.status_line.parse_line(input_data +
                                                    suffix)
            self.assertEqual(line.indent, 2)
            self.assertEqual(line.type, "STATUS")
            self.assertEqual(line.status, "GOOD")
            self.assertEqual(line.subdir, None)
            self.assertEqual(line.testname, None)
            self.assertEqual(line.reason, "No newline here!")
            self.assertEqual(line.optional_fields,
                              {"field1": "val1",
                               "field2": "val2"})

    def test_parse_line_fails_on_untabbed_lines(self):
        input_data = "   GOOD\trandom\tfields\tof text"
        line = version_1.status_line.parse_line(input_data)
        self.assertEqual(line, None)
        line = version_1.status_line.parse_line(input_data.lstrip())
        self.assertEqual(line.indent, 0)
        self.assertEqual(line.type, "STATUS")
        self.assertEqual(line.status, "GOOD")
        self.assertEqual(line.subdir, "random")
        self.assertEqual(line.testname, "fields")
        self.assertEqual(line.reason, "of text")
        self.assertEqual(line.optional_fields, {})

    def test_parse_line_fails_on_incomplete_lines(self):
        input_data = "\t\tGOOD\tfield\tsecond field"
        complete_data = input_data + "\tneeded last field"
        line = version_1.status_line.parse_line(input_data)
        self.assertEqual(line, None)
        line = version_1.status_line.parse_line(complete_data)
        self.assertEqual(line.indent, 2)
        self.assertEqual(line.type, "STATUS")
        self.assertEqual(line.status, "GOOD")
        self.assertEqual(line.subdir, "field")
        self.assertEqual(line.testname, "second field")
        self.assertEqual(line.reason, "needed last field")
        self.assertEqual(line.optional_fields, {})

    def test_good_reboot_passes_success_test(self):
        line = version_1.status_line(0, "NOSTATUS", None, "reboot",
                                     "reboot success", {})
        self.assertEqual(line.is_successful_reboot("GOOD"), True)
        self.assertEqual(line.is_successful_reboot("WARN"), True)

    def test_bad_reboot_passes_success_test(self):
        line = version_1.status_line(0, "NOSTATUS", None, "reboot",
                                     "reboot success", {})
        self.assertEqual(line.is_successful_reboot("FAIL"), False)
        self.assertEqual(line.is_successful_reboot("ABORT"), False)

    def test_get_kernel_returns_kernel_plus_patches(self):
        line = version_1.status_line(0, "GOOD", "subdir", "testname",
                                     "reason text",
                                     {"kernel": "2.6.24-rc40",
                                      "patch0": "first_patch 0 0",
                                      "patch1": "another_patch 0 0"})
        kern = line.get_kernel()
        kernel_hash = utils.hash("md5", "2.6.24-rc40,0,0").hexdigest()
        self.assertEqual(kern.base, "2.6.24-rc40")
        self.assertEqual(kern.patches[0].spec, "first_patch")
        self.assertEqual(kern.patches[1].spec, "another_patch")
        self.assertEqual(len(kern.patches), 2)
        self.assertEqual(kern.kernel_hash, kernel_hash)

    def test_get_kernel_ignores_out_of_sequence_patches(self):
        line = version_1.status_line(0, "GOOD", "subdir", "testname",
                                     "reason text",
                                     {"kernel": "2.6.24-rc40",
                                      "patch0": "first_patch 0 0",
                                      "patch2": "another_patch 0 0"})
        kern = line.get_kernel()
        kernel_hash = utils.hash("md5", "2.6.24-rc40,0").hexdigest()
        self.assertEqual(kern.base, "2.6.24-rc40")
        self.assertEqual(kern.patches[0].spec, "first_patch")
        self.assertEqual(len(kern.patches), 1)
        self.assertEqual(kern.kernel_hash, kernel_hash)

    def test_get_kernel_returns_unknown_with_no_kernel(self):
        line = version_1.status_line(0, "GOOD", "subdir", "testname",
                                     "reason text",
                                     {"patch0": "first_patch 0 0",
                                      "patch2": "another_patch 0 0"})
        kern = line.get_kernel()
        self.assertEqual(kern.base, "UNKNOWN")
        self.assertEqual(kern.patches, [])
        self.assertEqual(kern.kernel_hash, "UNKNOWN")

    def test_get_timestamp_returns_timestamp_field(self):
        timestamp = datetime.datetime(1970, 1, 1, 4, 30)
        timestamp -= datetime.timedelta(seconds=time.timezone)
        line = version_1.status_line(0, "GOOD", "subdir", "testname",
                                     "reason text",
                                     {"timestamp": "16200"})
        self.assertEqual(timestamp, line.get_timestamp())

    def test_get_timestamp_returns_none_on_missing_field(self):
        line = version_1.status_line(0, "GOOD", "subdir", "testname",
                                     "reason text", {})
        self.assertEqual(None, line.get_timestamp())


class iteration_parse_line_into_dicts(unittest.TestCase):

    def parse_line(self, line):
        attr, perf = {}, {}
        version_1.iteration.parse_line_into_dicts(line, attr, perf)
        return attr, perf

    def test_perf_entry(self):
        result = self.parse_line("perf-val{perf}=-173")
        self.assertEqual(({}, {"perf-val": -173}), result)

    def test_attr_entry(self):
        result = self.parse_line("attr-val{attr}=173")
        self.assertEqual(({"attr-val": "173"}, {}), result)

    def test_untagged_is_perf(self):
        result = self.parse_line("untagged=-678.5e5")
        self.assertEqual(({}, {"untagged": -678.5e5}), result)

    def test_invalid_tag_ignored(self):
        result = self.parse_line("bad-tag{invalid}=56")
        self.assertEqual(({}, {}), result)

    def test_non_numeric_perf_ignored(self):
        result = self.parse_line("perf-val{perf}=FooBar")
        self.assertEqual(({}, {}), result)

    def test_non_numeric_untagged_ignored(self):
        result = self.parse_line("untagged=FooBar")
        self.assertEqual(({}, {}), result)


class DummyAbortTestCase(unittest.TestCase):

    def setUp(self):
        self.indent = 3
        self.testname = 'testname'
        self.timestamp = 1220565792
        self.reason = 'Job aborted unexpectedly'

    def test_make_dummy_abort_with_timestamp(self):
        abort = version_1.parser.make_dummy_abort(
            self.indent, None, self.testname, self.timestamp, self.reason)
        self.assertEqual(
            abort, '%sEND ABORT\t----\t%s\ttimestamp=%d\t%s' % (
                '\t' * self.indent, self.testname, self.timestamp, self.reason))

    def test_make_dummy_abort_no_timestamp(self):
        abort = version_1.parser.make_dummy_abort(
            self.indent, None, self.testname, None, self.reason)
        self.assertEqual(
            abort, '%sEND ABORT\t----\t%s\t%s' % (
                '\t' * self.indent, self.testname, self.reason))


if __name__ == "__main__":
    unittest.main()

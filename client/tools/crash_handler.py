#!/usr/bin/python3
"""
Simple crash handling application for autotest

:copyright: Red Hat Inc 2009
:author: Lucas Meneghel Rodrigues <lmr@redhat.com>
"""
import subprocess
import glob
import os
import random
import re
import string
import sys
import syslog
import time


def generate_random_string(length):
    """
    Return a random string using alphanumeric characters.

    @length: length of the string that will be generated.
    """
    r = random.SystemRandom()
    str = ""
    chars = string.ascii_letters + string.digits
    while length > 0:
        str += r.choice(chars)
        length -= 1
    return str


def get_parent_pid(pid):
    """
    Returns the parent PID for a given PID, converted to an integer.

    :param pid: Process ID.
    """
    try:
        ppid = int(open('/proc/%s/stat' % pid).read().split()[3])
    except Exception:
        # It is not possible to determine the parent because the process
        # already left the process table.
        ppid = 1

    return ppid


def write_to_file(filename, data, report=False):
    """
    Write contents to a given file path specified. If not specified, the file
    will be created.

    :param file_path: Path to a given file.
    :param data: File contents.
    :param report: Whether we'll use GDB to get a backtrace report of the
                   file.
    """
    f = open(filename, 'w')
    try:
        f.write(data)
    finally:
        f.close()

    if report:
        gdb_report(filename)

    return filename


def get_results_dir_list(pid, core_dir_basename):
    """
    Get all valid output directories for the core file and the report. It works
    by inspecting files created by each test on /tmp and verifying if the
    PID of the process that crashed is a child or grandchild of the autotest
    test process. If it can't find any relationship (maybe a daemon that died
    during a test execution), it will write the core file to the debug dirs
    of all tests currently being executed. If there are no active autotest
    tests at a particular moment, it will return a list with ['/tmp'].

    :param pid: PID for the process that generated the core
    :param core_dir_basename: Basename for the directory that will hold both
            the core dump and the crash report.
    """
    pid_dir_dict = {}
    for debugdir_file in glob.glob("/tmp/autotest_results_dir.*"):
        a_pid = os.path.splitext(debugdir_file)[1]
        results_dir = open(debugdir_file).read().strip()
        pid_dir_dict[a_pid] = os.path.join(results_dir, core_dir_basename)

    results_dir_list = []
    # If a bug occurs and we can't grab the PID for the process that died, just
    # return all directories available and write to all of them.
    if pid is not None:
        while pid > 1:
            if pid in pid_dir_dict:
                results_dir_list.append(pid_dir_dict[pid])
            pid = get_parent_pid(pid)
    else:
        results_dir_list = list(pid_dir_dict.values())

    return (results_dir_list or
            list(pid_dir_dict.values()) or
            [os.path.join("/tmp", core_dir_basename)])


def get_info_from_core(path):
    """
    Reads a core file and extracts a dictionary with useful core information.

    Right now, the only information extracted is the full executable name.

    :param path: Path to core file.
    """
    full_exe_path = None
    output = subprocess.getoutput('gdb -c %s batch' % path)
    path_pattern = re.compile("Core was generated by `([^\0]+)'", re.IGNORECASE)
    match = re.findall(path_pattern, output)
    for m in match:
        # Sometimes the command line args come with the core, so get rid of them
        m = m.split(" ")[0]
        if os.path.isfile(m):
            full_exe_path = m
            break

    if full_exe_path is None:
        syslog.syslog("Could not determine from which application core file %s "
                      "is from" % path)

    return {'full_exe_path': full_exe_path}


def gdb_report(path):
    """
    Use GDB to produce a report with information about a given core.

    :param path: Path to core file.
    """
    # Get full command path
    exe_path = get_info_from_core(path)['full_exe_path']
    basedir = os.path.dirname(path)
    gdb_command_path = os.path.join(basedir, 'gdb_cmd')

    if exe_path is not None:
        # Write a command file for GDB
        gdb_command = 'bt full\n'
        write_to_file(gdb_command_path, gdb_command)

        # Take a backtrace from the running program
        gdb_cmd = ('gdb -se %s -c %s -x %s -n -batch -quiet' %
                   (exe_path, path, gdb_command_path))
        backtrace = subprocess.getoutput(gdb_cmd)
        # Sanitize output before passing it to the report
        backtrace = backtrace.decode('utf-8', 'ignore')
    else:
        exe_path = "Unknown"
        backtrace = ("Could not determine backtrace for core file %s" % path)

    # Composing the format_dict
    report = "Program: %s\n" % exe_path
    if crashed_pid is not None:
        report += "PID: %s\n" % crashed_pid
    if signal is not None:
        report += "Signal: %s\n" % signal
    if hostname is not None:
        report += "Hostname: %s\n" % hostname
    if crash_time is not None:
        report += ("Time of the crash (according to kernel): %s\n" %
                   time.ctime(float(crash_time)))
    report += "Program backtrace:\n%s\n" % backtrace

    report_path = os.path.join(basedir, 'report')
    write_to_file(report_path, report)


def write_cores(core_data, dir_list):
    """
    Write core files to all directories, optionally providing reports.

    :param core_data: Contents of the core file.
    :param dir_list: List of directories the cores have to be written.
    :param report: Whether reports are to be generated for those core files.
    """
    syslog.syslog("Writing core files to %s" % dir_list)
    for result_dir in dir_list:
        if not os.path.isdir(result_dir):
            os.makedirs(result_dir)
        core_path = os.path.join(result_dir, 'core')
        core_path = write_to_file(core_path, core_file, report=True)


if __name__ == "__main__":
    syslog.openlog('AutotestCrashHandler', 0, syslog.LOG_DAEMON)
    global crashed_pid, crash_time, uid, signal, hostname, exe
    try:
        full_functionality = False
        try:
            crashed_pid, crash_time, uid, signal, hostname, exe = sys.argv[1:]  # pylint: disable=E0632
            full_functionality = True
        except ValueError:
            # Probably due a kernel bug, we can't exactly map the parameters
            # passed to this script. So we have to reduce the functionality
            # of the script (just write the core at a fixed place).
            syslog.syslog("Unable to unpack parameters passed to the "
                          "script. Operating with limited functionality.")
            crashed_pid, crash_time, uid, signal, hostname, exe = (None, None,
                                                                   None, None,
                                                                   None, None)

        if full_functionality:
            core_dir_name = 'crash.%s.%s' % (exe, crashed_pid)
        else:
            core_dir_name = 'core.%s' % generate_random_string(4)

        # Get the filtered results dir list
        results_dir_list = get_results_dir_list(crashed_pid, core_dir_name)

        # Write the core file to the appropriate directory
        # (we are piping it to this script)
        core_file = sys.stdin.read()

        if (exe is not None) and (crashed_pid is not None):
            syslog.syslog("Application %s, PID %s crashed" % (exe, crashed_pid))
        write_cores(core_file, results_dir_list)

    except Exception as e:
        syslog.syslog("Crash handler had a problem: %s" % e)

# This file must use Python 1.5 syntax.
import glob
import os
import re
import sys


class base_check_python_version:

    def __init__(self):
        version = None
        try:
            version = sys.version_info[0:2]
        except AttributeError:
            pass  # pre 2.0, no neat way to get the exact number
        #self.restart()

    def extract_version(self, path):
        match = re.search(r'/python(\d+)\.(\d+)$', path)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        else:
            return None

    PYTHON_BIN_GLOB_STRINGS = ['/usr/bin/python3*', '/usr/local/bin/python3*']

    def find_desired_python(self):
        """Returns the path of the desired python interpreter."""
        pythons = []
        for glob_str in self.PYTHON_BIN_GLOB_STRINGS:
            pythons.extend(glob.glob(glob_str))

        possible_versions = []
        best_python = (0, 0), ''
        for python in pythons:
            version = self.extract_version(python)
            if version and version >= (2, 4):
                possible_versions.append((version, python))

        possible_versions.sort()

        if not possible_versions:
            raise ValueError('Python 2.x version 2.4 or better is required')
        # Return the lowest possible version so that we use 2.4 if available
        # rather than more recent versions.
        return possible_versions[0][1]

    def restart(self):
        python = self.find_desired_python()
        sys.stderr.write('NOTE: %s switching to %s\n' %
                         (os.path.basename(sys.argv[0]), python))
        sys.argv.insert(0, '-u')
        sys.argv.insert(0, python)
        os.execv(sys.argv[0], sys.argv)

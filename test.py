#!/usr/bin/python
import optparse
import sys
import unittest

USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules"""


def main(sdk_path):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest.loader.TestLoader().discover('tests', '*.py')
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    SDK_PATH = args[0] if len(args) == 1 else '/usr/local/google_appengine'
    main(SDK_PATH)

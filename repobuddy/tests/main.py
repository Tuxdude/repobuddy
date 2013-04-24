#
#   Copyright (C) 2012 Ash (Tuxdude) <tuxdude.github@gmail.com>
#
#   This file is part of repobuddy.
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as
#   published by the Free Software Foundation; either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.
#

import os as _os

from repobuddy.tests.common import TestSuiteManager


def run_tests():
    _os.environ['GIT_AUTHOR_NAME'] = 'repobuddy-testbot'
    _os.environ['GIT_AUTHOR_EMAIL'] = 'testbot@repobuddy'
    _os.environ['GIT_COMMITTER_NAME'] = _os.environ['GIT_AUTHOR_NAME']
    _os.environ['GIT_COMMITTER_EMAIL'] = _os.environ['GIT_COMMITTER_NAME']

    test_dir = _os.path.join(_os.getcwd(), 'testing-ground')
    tests = TestSuiteManager(test_dir)

    tests_override = _os.environ.get('REPOBUDDY_TESTS')
    test_suite_classes = None

    if not tests_override is None and not tests_override.strip() is '':
        test_suite_classes = tests_override.strip().split(',')
    else:
        test_suite_classes = [
            'git_wrapper.GitWrapperTestSuite',
            'manifest_parser.ManifestParserTestSuite',
            'client_info.ClientInfoTestSuite',
            'utils.UtilsTestSuite',
            'arg_parser.ArgParserTestSuite']

    for class_name in test_suite_classes:
        module_parts = ('repobuddy.tests.' + class_name).split('.')
        test_suite_class = __import__('.'.join(module_parts[:-1]))
        for part in module_parts[1:]:
            test_suite_class = getattr(test_suite_class, part)
        tests.add_test_suite(test_suite_class.get_test_suite())

    tests.run()
    tests.show_results()

    return tests.was_successful()

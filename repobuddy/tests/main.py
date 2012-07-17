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
from repobuddy.tests.git_wrapper import GitWrapperTestSuite
from repobuddy.tests.manifest_parser import ManifestParserTestSuite


def run_tests():
    test_dir = _os.path.join(_os.getcwd(), 'testing-ground')
    tests = TestSuiteManager(test_dir)

    git_wrapper_tests = GitWrapperTestSuite.get_test_suite()
    manifest_parser_tests = ManifestParserTestSuite.get_test_suite()
    tests.add_test_suite(git_wrapper_tests)
    tests.add_test_suite(manifest_parser_tests)
    tests.run()
    tests.show_results()

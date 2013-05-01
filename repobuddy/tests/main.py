#
#   Copyright (C) 2013 Ash (Tuxdude) <tuxdude.github@gmail.com>
#
#   This file is part of repobuddy.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
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
            'arg_parser.ArgParserTestSuite',
            'command_handler.CommandHandlerTestSuite']

    for class_name in test_suite_classes:
        module_parts = ('repobuddy.tests.' + class_name).split('.')
        test_suite_class = __import__('.'.join(module_parts[:-1]))
        for part in module_parts[1:]:
            test_suite_class = getattr(test_suite_class, part)
        tests.add_test_suite(test_suite_class.get_test_suite())

    tests.run()
    tests.show_results()

    return tests.was_successful()

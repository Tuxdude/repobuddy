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
import shlex as _shlex
import shutil as _shutil
import subprocess as _subprocess
import sys as _sys
import traceback as _traceback

if _sys.version_info < (2, 7):
    import cStringIO as _io
    import ordereddict as _collections
    import unittest2 as _unittest
else:
    if _sys.version_info < (3, 0):
        import cStringIO as _io
    else:
        import io as _io
    import collections as _collections
    import unittest as _unittest

from repobuddy.utils import RepoBuddyBaseException, Logger


class ShellError(RepoBuddyBaseException):
    def __init__(self, error_str):
        super(ShellError, self).__init__(error_str)
        return


class ShellHelper:
    @classmethod
    def exec_command(cls, command, base_dir, debug_output=True):
        Logger.msg('>> ' + ' '.join(command))
        try:
            if debug_output:
                proc = _subprocess.Popen(
                    command,
                    cwd=base_dir)
            else:
                proc = _subprocess.Popen(
                    command,
                    cwd=base_dir,
                    stdout=open(_os.devnull, 'w'),
                    stderr=_subprocess.STDOUT)
            proc.communicate()
            return_code = proc.wait()
            if return_code != 0:
                raise ShellError('Command \'%s\' failed!' % command)
        except (OSError, IOError) as err:
            raise ShellError(str(err))
        return

    @classmethod
    def append_text_to_file(cls, text, filename, base_dir):
        try:
            file_handle = open(_os.path.join(base_dir, filename), 'a')
            file_handle.write(text)
            file_handle.close()
        except (OSError, IOError) as err:
            raise ShellError(str(err))
        return

    @classmethod
    def remove_file(cls, filename):
        try:
            _os.unlink(filename)
        except (OSError, IOError) as err:
            raise ShellError(str(err))
        return

    @classmethod
    def make_dir(cls, dirname):
        try:
            _os.mkdir(dirname)
        except (OSError, IOError) as err:
            raise ShellError(str(err))
        return

    @classmethod
    def remove_dir(cls, dirname):
        if _os.path.isdir(dirname):
            try:
                _shutil.rmtree(dirname, ignore_errors=False)
            except (OSError, IOError) as err:
                raise ShellError(str(err))
        return


class TestCommon:
    @classmethod
    def _git_append_add_commit(cls, text, filename, commit_log, exec_dir):
        ShellHelper.append_text_to_file(text, filename, exec_dir)
        ShellHelper.exec_command(
            _shlex.split('git add %s' % filename),
            exec_dir)
        ShellHelper.exec_command(
            _shlex.split('git commit -m "%s"' % commit_log),
            exec_dir)
        return

    @classmethod
    def setup_test_repos(cls, base_dir):
        # Cleanup and create an empty directory
        ShellHelper.remove_dir(base_dir)
        ShellHelper.make_dir(base_dir)

        # Set up the origin and clone repo paths
        origin_repo_url = _os.path.join(base_dir, 'repo-origin')
        clone_repo1 = _os.path.join(base_dir, 'clone1')
        clone_repo2 = _os.path.join(base_dir, 'clone2')

        # Set up the origin as a bare repo
        ShellHelper.make_dir(origin_repo_url)
        ShellHelper.exec_command(
            _shlex.split('git init --bare'),
            origin_repo_url)

        # Create Clone1 from the origin
        ShellHelper.exec_command(
            _shlex.split('git clone %s %s' % (origin_repo_url, clone_repo1)),
            base_dir)

        # Create some content in clone1
        cls._git_append_add_commit(
            'First content...\n',
            'README',
            'First commit.',
            clone_repo1)
        cls._git_append_add_commit(
            'Hardly useful...\n',
            'dummy',
            'Here we go.',
            clone_repo1)
        cls._git_append_add_commit(
            'More content...\n',
            'README',
            'Appending to README.',
            clone_repo1)

        # Push the changes to origin
        ShellHelper.exec_command(
            _shlex.split('git push origin master'),
            clone_repo1)

        # Make some more changes, but do not push yet
        cls._git_append_add_commit(
            'Another line...\n',
            'README',
            'One more to README.',
            clone_repo1)
        cls._git_append_add_commit(
            'Dummy2 in place...\n',
            'dummy2',
            'Creating dummy2.',
            clone_repo1)

        # Create clone2 from the origin
        ShellHelper.exec_command(
            _shlex.split('git clone %s %s' % (origin_repo_url, clone_repo2)),
            base_dir)

        # Add and commit changes in clone2
        cls._git_append_add_commit(
            'Another line...\n',
            'dummy',
            'One more to dummy.',
            clone_repo2)
        cls._git_append_add_commit(
            'More dummy...\n',
            'dummy',
            'More dummy.',
            clone_repo2)

        # Create a new branch in clone2
        ShellHelper.exec_command(
            _shlex.split('git branch new-branch'),
            clone_repo2)
        ShellHelper.exec_command(
            _shlex.split('git checkout new-branch'),
            clone_repo2)

        # Add some more changes in clone2's new-branch
        cls._git_append_add_commit(
            'More lines...\n',
            'dummy',
            'Another line to dummy.',
            clone_repo2)
        cls._git_append_add_commit(
            'Just keep it coming...\n',
            'dummy',
            'Again :D',
            clone_repo2)

        # Switch back to master in clone2
        ShellHelper.exec_command(
            _shlex.split('git checkout master'),
            clone_repo2)

        # Push all branches to origin
        ShellHelper.exec_command(
            _shlex.split('git push origin --all'),
            clone_repo2)

        # Pull changes from origin into clone1
        ShellHelper.exec_command(
            _shlex.split('git fetch origin'),
            clone_repo1)
        ShellHelper.exec_command(
            _shlex.split(
                'git merge --commit -m "Merge origin into clone1" ' +
                'origin/master'),
            clone_repo1)

        # Now push the merges back to origin
        ShellHelper.exec_command(
            _shlex.split('git push origin master'),
            clone_repo1)

        # Get the changes from origin into clone2
        ShellHelper.exec_command(
            _shlex.split('git fetch origin'),
            clone_repo2)
        ShellHelper.exec_command(
            _shlex.split(
                'git merge --commit -m "Merge origin into clone2" ' +
                'origin/master'),
            clone_repo2)

        # Now push the merges back to origin
        ShellHelper.exec_command(
            _shlex.split('git push origin --all'),
            clone_repo2)

        # Now get rid of the clone repos, we only need the origin
        ShellHelper.remove_dir(clone_repo1)
        ShellHelper.remove_dir(clone_repo2)

        return


class TestCaseBase(_unittest.TestCase):
    def _set_tear_down_cb(self, method, *args, **kwargs):
        self._tear_down_cb = method
        self._tear_down_cb_args = args
        self._tear_down_cb_kwargs = kwargs
        return

    def _clear_tear_down_cb(self):
        self._tear_down_cb = None
        self._tear_down_cb_args = None
        self._tear_down_cb_kwargs = None
        return

    def __init__(self, methodName='runTest'):
        super(TestCaseBase, self).__init__(methodName)
        self._tear_down_cb = None
        self._tear_down_cb_args = None
        self._tear_down_cb_kwargs = None

        if _sys.version_info >= (3, 2):
            self._count_equal = self.assertCountEqual
        else:
            self._count_equal = self.assertItemsEqual
        return

    def setUp(self):
        return

    def tearDown(self):
        if not self._tear_down_cb is None:
            self._tear_down_cb(*self._tear_down_cb_args,
                               **self._tear_down_cb_kwargs)
            self._clear_tear_down_cb()
        return


class TestResult(_unittest.TestResult):
    PASSED = 0
    ERROR = 1
    FAILED = 2
    SKIPPED = 3
    EXPECTED_FAILURE = 4
    UNEXPECTED_SUCCESS = 5

    _result_str = {PASSED: 'PASSED',
                   ERROR: 'ERROR',
                   FAILED: 'FAILED',
                   SKIPPED: 'SKIPPED',
                   EXPECTED_FAILURE: 'EXPECTED FAILURE',
                   UNEXPECTED_SUCCESS: 'UNEXPECTED_SUCCESS'}

    def _update_result(self, test, err, result_type):
        module_test_results = []
        test_id = test.id().split('.')

        if test_id[-2] not in self.test_results:
            self.test_results[test_id[-2]] = module_test_results
        else:
            module_test_results = self.test_results[test_id[-2]]

        result = {}
        result['test_case'] = test_id[-1]
        result['description'] = str(test.shortDescription())
        result['result'] = result_type
        if not err is None:
            result['formated_traceback'] = \
                ''.join(_traceback.format_exception(err[0], err[1], err[2]))

        module_test_results.append(result)
        return

    def __init__(self):
        super(TestResult, self).__init__()
        self.test_results = _collections.OrderedDict()
        self.hasErrors = False
        self.hasFailures = False
        self.hasUnexpectedSuccess = False
        return

    @classmethod
    def get_result_str(cls, result):
        return cls._result_str[result]

    def addError(self, test, err):
        self._update_result(test, err, type(self).ERROR)
        self.hasErrors = True
        return

    def addFailure(self, test, err):
        self._update_result(test, err, type(self).FAILED)
        self.hasFailures = True
        return

    def addSuccess(self, test):
        self._update_result(test, None, type(self).PASSED)
        return

    def addSkip(self, test, reason):
        self._update_result(test, None, type(self).SKIPPED)
        return

    def addExpectedFailure(self, test, err):
        self._update_result(test, err, type(self).EXPECTED_FAILURE)
        return

    def addUnexpectedSuccess(self, test):
        self._update_result(test, None, type(self).UNEXPECTED_SUCCESS)
        self.hasUnexpectedSuccess = True
        return


class TestRunner(_unittest.TextTestRunner):
    def __init__(self, stream=_sys.stderr, descriptions=True, verbosity=1):
        super(TestRunner, self).__init__(stream, descriptions, verbosity)
        self._test_result = None
        return

    def _makeResult(self):
        self._test_result = TestResult()
        return self._test_result

    def get_test_result(self):
        return self._test_result


class TestSuiteManager(object):
    _base_dir = None

    @classmethod
    def get_base_dir(cls):
        return cls._base_dir

    def __init__(self, base_dir):
        if not _os.path.isdir(base_dir):
            ShellHelper.make_dir(base_dir)
        type(self)._base_dir = base_dir
        self._test_suite = None
        self._output = _io.StringIO()
        self._test_result = None
        return

    def add_test_suite(self, test_suite):
        if self._test_suite is None:
            self._test_suite = test_suite
        else:
            self._test_suite.addTest(test_suite)
        return

    def run(self):
        runner = TestRunner(
            stream=self._output,
            verbosity=0)
        runner.run(self._test_suite)
        self._test_result = runner.get_test_result()
        return

    def show_results(self):
        Logger.msg('\n')
        Logger.msg('*' * 120)
        Logger.msg('{0:^120}'.format('Test Summary'))
        Logger.msg('*' * 120)
        Logger.msg(self._output.getvalue())
        Logger.msg('-' * 120 + '\n\n')

        error_traces_str = ''
        failure_traces_str = ''

        for test_suite, results in self._test_result.test_results.items():
            Logger.msg('TestSuite: %s' % test_suite)
            Logger.msg('#' * 120)
            Logger.msg('{0:48} {1:56} {2:16}'.format(
                'TestCase',
                'Description',
                'Result'))
            Logger.msg('#' * 120)
            for result in results:
                Logger.msg('{0:48} {1:56} {2:16}'.format(
                    result['test_case'],
                    result['description'],
                    TestResult.get_result_str(result['result'])))
                if result['result'] == TestResult.ERROR:
                    error_traces_str += \
                        '%s::%s\n%s\n' % (test_suite,
                                          result['test_case'],
                                          result['formated_traceback'])
                elif result['result'] == TestResult.FAILED:
                    failure_traces_str += \
                        '%s::%s\n%s\n' % (test_suite,
                                          result['test_case'],
                                          result['formated_traceback'])
            Logger.msg('-' * 120 + '\n\n')

        if self._test_result.hasErrors:
            Logger.msg('#' * 120)
            Logger.msg('Errors')
            Logger.msg('#' * 120 + '\n')
            Logger.msg(error_traces_str + '-' * 120 + '\n')

        if self._test_result.hasFailures:
            Logger.msg('#' * 120)
            Logger.msg('Failures')
            Logger.msg('#' * 120 + '\n')
            Logger.msg(failure_traces_str + '-' * 120 + '\n')

        Logger.msg('Tests Run: ' + str(self._test_result.testsRun))
        return

    def was_successful(self):
        return (not self._test_result.hasErrors) and \
               (not self._test_result.hasFailures) and \
               (not self._test_result.hasUnexpectedSuccess)

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

import cStringIO as _cStringIO
import os as _os
import subprocess as _subprocess
import shlex as _shlex
import shutil as _shutil
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
        return

    def setUp(self):
        return

    def tearDown(self):
        if not self._tear_down_cb is None:
            self._tear_down_cb(*self._tear_down_cb_args,
                               **self._tear_down_cb_kwargs)
            self._clear_tear_down_cb()
        return


class TestSuiteManager(object):
    def __init__(self, base_test_dir):
        self._base_test_dir = base_test_dir
        self._test_suite = None
        self._output = _cStringIO.StringIO()
        return

    def add_test_suite(self, test_suite):
        if self._test_suite is None:
            self._test_suite = test_suite
        else:
            self._test_suite.addTest(test_suite)
        return

    def run(self):
        runner = _unittest.TextTestRunner(
            stream=self._output,
            verbosity=2)
        runner.run(self._test_suite)
        return

    def show_results(self):
        Logger.msg('\n')
        Logger.msg('#' * 80 + '\n')
        Logger.msg('Test Results')
        Logger.msg('-' * 70 + '\n')
        Logger.msg(self._output.getvalue())
        Logger.msg('#' * 80)
        return

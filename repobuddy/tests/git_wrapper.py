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
import shlex as _shlex
import stat as _stat
import sys as _sys

if _sys.version_info < (2, 7):
    import unittest2 as _unittest   # pylint: disable=F0401
else:
    import unittest as _unittest    # pylint: disable=F0401

from repobuddy.tests.common import TestCommon, TestCaseBase, \
    TestSuiteManager, ShellHelper
from repobuddy.git_wrapper import GitWrapper, GitWrapperError


class GitWrapperTestCase(TestCaseBase):
    _repos_dir = None
    _skip_cleanup = True

    def _git_wrapper_clone_helper(self,
                                  base_dir,
                                  url,
                                  branch,
                                  dest,
                                  remove_base_dir=False):
        clone_dir = _os.path.join(base_dir, dest)
        if not remove_base_dir:
            self._set_tear_down_cb(self._clone_tear_down_cb, clone_dir)
        else:
            self._set_tear_down_cb(self._clone_tear_down_cb, base_dir)

        git = GitWrapper(base_dir)
        git.clone(url, branch, dest)
        return

    def _clone_tear_down_cb(self, clone_dir):
        ShellHelper.remove_dir(clone_dir)
        return

    def _raw_git_clone(self, base_dir, url, branch, dest):
        clone_dir = _os.path.join(base_dir, dest)
        self._set_tear_down_cb(self._clone_tear_down_cb, clone_dir)
        ShellHelper.exec_command(
            _shlex.split('git clone -b %s %s %s' % (branch, url, dest)),
            base_dir)
        return

    @classmethod
    def setUpClass(cls):
        cls._repos_dir = _os.path.join(TestSuiteManager.get_base_dir(),
                                       'repos')
        TestCommon.setup_test_repos(cls._repos_dir)
        cls._origin_repo = _os.path.join(cls._repos_dir, 'repo-origin')
        return

    @classmethod
    def tearDownClass(cls):
        if not cls._skip_cleanup:   # pragma: no cover
            ShellHelper.remove_dir(cls._repos_dir)
        return

    def __init__(self, methodName='runTest'):
        super(GitWrapperTestCase, self).__init__(methodName)
        return

    def test_clone_valid_repo(self):
        self._git_wrapper_clone_helper(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        return

    def test_clone_invalid_url(self):
        with self.assertRaisesRegexp(
                GitWrapperError,
                r'^Command \'git clone -b .*\' failed$'):
            self._git_wrapper_clone_helper(
                type(self)._repos_dir,
                type(self)._origin_repo + '-invalid-suffix',
                'master',
                'test-clone')
        return

    def test_clone_invalid_branch(self):
        with self.assertRaisesRegexp(
                GitWrapperError,
                r'^Command \'git clone -b .*\' failed$'):
            self._git_wrapper_clone_helper(
                type(self)._repos_dir,
                type(self)._origin_repo,
                'does-not-exist-branch',
                'test-clone')
        return

    def test_clone_no_write_permissions(self):
        base_dir = _os.path.join(
            type(self)._repos_dir,
            'test-no-write')
        ShellHelper.make_dir(base_dir)
        _os.chmod(base_dir, _os.stat(base_dir).st_mode & ~(_stat.S_IWUSR))

        with self.assertRaisesRegexp(
                GitWrapperError,
                r'^Command \'git clone -b .*\' failed$'):
            self._git_wrapper_clone_helper(
                base_dir,
                type(self)._origin_repo,
                'master',
                'test-clone',
                remove_base_dir=True)
        return

    def test_update_index_valid_repo(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')

        git = GitWrapper(base_dir)
        git.update_index()
        return

    def test_update_index_invalid_repo(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        git_dir = _os.path.join(base_dir, '.git')
        ShellHelper.remove_dir(git_dir)

        with self.assertRaisesRegexp(
                GitWrapperError,
                r'^Command \'git update-index -q --ignore-submodules ' +
                r'--refresh\' failed$'):
            git = GitWrapper(base_dir)
            git.update_index()
        return

    def test_untracked_no_files(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')

        git = GitWrapper(base_dir)
        self._assert_count_equal(git.get_untracked_files(), [])
        return

    def test_untracked_with_files(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        ShellHelper.append_text_to_file(
            'Untracked file here...',
            'untracked-test',
            base_dir)
        ShellHelper.append_text_to_file(
            'Untracked file here too...',
            'untracked-test2',
            base_dir)

        git = GitWrapper(base_dir)
        self._assert_count_equal(
            git.get_untracked_files(),
            ['untracked-test', 'untracked-test2'])
        return

    def test_unstaged_no_files(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')

        git = GitWrapper(base_dir)
        self._assert_count_equal(git.get_unstaged_files(), [])
        return

    def test_unstaged_with_files(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        ShellHelper.append_text_to_file(
            'Modifying existing file...',
            'README',
            base_dir)
        ShellHelper.remove_file(_os.path.join(base_dir, 'dummy'))

        git = GitWrapper(base_dir)
        self._assert_count_equal(git.get_unstaged_files(),
                                 ['M\tREADME', 'D\tdummy'])

        return

    def test_uncommitted_no_changes(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')

        git = GitWrapper(base_dir)
        self._assert_count_equal(git.get_uncommitted_staged_files(), [])
        return

    def test_uncommitted_with_changes(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        ShellHelper.append_text_to_file(
            'Modifying existing file...',
            'README',
            base_dir)
        ShellHelper.remove_file(_os.path.join(base_dir, 'dummy'))
        ShellHelper.exec_command(_shlex.split('git add README'), base_dir)
        ShellHelper.exec_command(_shlex.split('git rm dummy'), base_dir)

        git = GitWrapper(base_dir)
        self._assert_count_equal(git.get_uncommitted_staged_files(),
                                 ['M\tREADME', 'D\tdummy'])
        return

    def test_current_branch_valid_repo(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')

        git = GitWrapper(base_dir)
        self.assertEqual(git.get_current_branch(), 'master')
        return

    def test_current_branch_invalid_repo(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        git_dir = _os.path.join(base_dir, '.git')
        ShellHelper.remove_dir(git_dir)

        git = GitWrapper(base_dir)
        with self.assertRaisesRegexp(
                GitWrapperError,
                r'^Command \'git symbolic-ref HEAD\' failed$'):
            git.get_current_branch()
        return

    def test_current_branch_detached_head(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        ShellHelper.exec_command(_shlex.split('git checkout HEAD^'), base_dir)

        git = GitWrapper(base_dir)
        self.assertIsNone(git.get_current_branch())
        return

    def test_current_tag_lightweight_tag(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        ShellHelper.exec_command(_shlex.split('git tag tag-v1'), base_dir)

        git = GitWrapper(base_dir)
        self.assertEqual(git.get_current_tag(), 'tag-v1')

        ShellHelper.exec_command(_shlex.split('git checkout HEAD^^^'),
                                 base_dir)
        self.assertIsNone(git.get_current_tag())
        return

    def test_current_tag_annotated_tag(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')
        ShellHelper.exec_command(
            _shlex.split('git tag -a tag-v2 -m "Test annotated tags"'),
            base_dir)

        git = GitWrapper(base_dir)
        self.assertEqual(git.get_current_tag(), 'tag-v2')

        ShellHelper.exec_command(_shlex.split('git checkout HEAD^^^'),
                                 base_dir)
        self.assertIsNone(git.get_current_tag())
        return

    def test_current_tag_no_tag(self):
        self._raw_git_clone(
            type(self)._repos_dir,
            type(self)._origin_repo,
            'master',
            'test-clone')
        base_dir = _os.path.join(type(self)._repos_dir, 'test-clone')

        git = GitWrapper(base_dir)
        self.assertIsNone(git.get_current_tag())
        return


class GitWrapperTestSuite:  # pylint: disable=W0232
    @classmethod
    def get_test_suite(cls):
        tests = [
            'test_clone_valid_repo',
            'test_clone_invalid_url',
            'test_clone_invalid_branch',
            'test_clone_no_write_permissions',
            'test_update_index_valid_repo',
            'test_update_index_invalid_repo',
            'test_untracked_no_files',
            'test_untracked_with_files',
            'test_unstaged_no_files',
            'test_unstaged_with_files',
            'test_uncommitted_no_changes',
            'test_uncommitted_with_changes',
            'test_current_branch_valid_repo',
            'test_current_branch_invalid_repo',
            'test_current_branch_detached_head',
            'test_current_tag_lightweight_tag',
            'test_current_tag_annotated_tag',
            'test_current_tag_no_tag']
        return _unittest.TestSuite(map(GitWrapperTestCase, tests))

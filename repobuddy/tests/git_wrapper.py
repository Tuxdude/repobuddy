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

import inspect as _inspect
import os as _os
import unittest as _unittest

from repobuddy.tests.common import TestCommon, ShellHelper
from repobuddy.utils import Logger
from repobuddy.git_wrapper import GitWrapper, GitWrapperError


class GitWrapperTestCase(_unittest.TestCase):
    _base_dir = None
    _repos_dir = None
    _skip_cleanup = True

    @classmethod
    def set_base_dir(cls, base_dir):
        cls._base_dir = base_dir
        return

    @classmethod
    def setUpClass(cls):
        cls._repos_dir = _os.path.join(cls._base_dir, 'repos')
        TestCommon.setup_test_repos(cls._repos_dir)
        cls._origin_repo = _os.path.join(cls._repos_dir, 'repo-origin')
        return

    @classmethod
    def tearDownClass(cls):
        if not cls._skip_cleanup:
            ShellHelper.remove_dir(cls._repos_dir)
        return

    def __init__(self, methodName='runTest'):
        super(GitWrapperTestCase, self).__init__(methodName)
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

    def _clone_helper(self, base_dir, url, branch, destination):
        clone_dir = _os.path.join(base_dir, destination)
        self._set_tear_down_cb(self._clone_tear_down_cb, clone_dir)

        git = GitWrapper(base_dir)
        git.clone(url, branch, destination)

        ShellHelper.remove_dir(clone_dir)
        return

    def _clone_tear_down_cb(self, clone_dir):
        ShellHelper.remove_dir(clone_dir)
        return

    def test_clone_valid_repo(self):
        self._clone_helper(
            self.__class__._repos_dir,
            self.__class__._origin_repo,
            'master',
            'test-clone')
        return

    def test_clone_invalid_url(self):
        with self.assertRaisesRegexp(
            GitWrapperError,
            r'Command \'git clone -b .*\' failed'):
            self._clone_helper(
                self.__class__._repos_dir,
                self.__class__._origin_repo + '-invalid-suffix',
                'master',
                'test-clone')
        return

    def test_clone_invalid_branch(self):
        with self.assertRaisesRegexp(
            GitWrapperError,
            r'Command \'git clone -b .*\' failed'):
            self._clone_helper(
                self.__class__._repos_dir,
                self.__class__._origin_repo,
                'does-not-exist-branch',
                'test-clone')
        return


class GitWrapperTestSuite():
    def __init__(self, base_test_dir):
        if not _os.path.isdir(base_test_dir):
            ShellHelper.make_dir(base_test_dir)
        GitWrapperTestCase.set_base_dir(base_test_dir)
        return

    def get_test_suite(self):
        tests = [
            'test_clone_valid_repo',
            'test_clone_invalid_url',
            'test_clone_invalid_branch']
        return _unittest.TestSuite(map(GitWrapperTestCase, tests))


def setUpModule():
    return


def tearDownModule():
    return

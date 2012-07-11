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
import re as _re
import subprocess as _subprocess

from repobuddy.utils import Logger, RepoBuddyBaseException


class GitWrapperError(RepoBuddyBaseException):
    def __init__(self, error_str, is_git_error):
        super(GitWrapperError, self).__init__(error_str)
        self.is_git_error = is_git_error
        return


class GitWrapper(object):
    def _exec_git(self, command, capture_std_out=True):
        git_cmd = command[:]
        git_cmd.insert(0, 'git')
        Logger.debug('Exec: ' + ' '.join(git_cmd))
        try:
            if not capture_std_out:
                proc = _subprocess.Popen(
                    git_cmd,
                    cwd=self._base_dir)
            else:
                proc = _subprocess.Popen(
                    git_cmd,
                    cwd=self._base_dir,
                    stdout=_subprocess.PIPE,
                    stderr=_subprocess.PIPE)
            (out_msg, err_msg) = proc.communicate()
            return_code = proc.wait()
            if return_code != 0:
                raise GitWrapperError('Command \'%s\' failed' % cmd,
                                      is_git_error=True)
            if capture_std_out:
                return out_msg
        except OSError as err:
            raise GitWrapperError(str(err), is_git_error=False)
        return

    # Constructor
    # base_dir - is the base directory of the git repo
    def __init__(self, base_dir):
        if not _os.path.isabs(base_dir):
            raise GitWrapperError(
                'Error: base_dir \'' + base_dir +
                '\' needs to be an absolute path')
        self._base_dir = base_dir
        return

    def __del__(self):
        return

    # Clone the git repo at remote_url checking out branch
    # Equivalent of git clone -b branch remote_url
    # It also changes the current Dir to dest_dir
    def clone(self, remote_url, branch, dest_dir):
        self._exec_git(
            ['clone', '-b', branch, remote_url, dest_dir],
            capture_std_out=False)
        if _os.path.isabs(dest_dir):
            self._base_dir = dest_dir
        else:
            self._base_dir = _os.path.join(self._base_dir, dest_dir)
        return

    def update_index(self):
        self._exec_git(
            ['update-index', '-q', '--ignore-submodules', '--refresh'],
            capture_std_out=False)
        return

    def get_untracked_files(self):
        try:
            untracked_files = self._exec_git(
                ['ls-files', '--error-unmatch', '--exclude-standard',
                 '--others', '--']).rstrip()
        except GitWrapperError as err:
            if not err.is_git_error:
                raise err
        if untracked_files == '':
            return None
        else:
            return untracked_files

    def get_unstaged_files(self):
        try:
            self._exec_git(
                ['diff-files', '--quiet', '--ignore-submodules', '--'])
        except GitWrapperError as err:
            if not err.is_git_error:
                raise err
            unstaged_files = self._exec_git(
                ['diff-files', '--name-status', '-r',
                 '--ignore-submodules', '--'])
            return unstaged_files.rstrip()
        return

    def get_uncommitted_staged_files(self):
        try:
            self._exec_git(
                ['diff-index', '--cached', '--quiet', 'HEAD',
                 '--ignore-submodules', '--'])
        except GitWrapperError as err:
            if not err.is_git_error:
                raise err
            uncommited_staged_files = self._exec_git(
                ['diff-index', '--cached', '--name-status', '-r',
                 '--ignore-submodules', 'HEAD', '--'])
            return uncommited_staged_files.rstrip()
        return

    def get_current_branch(self):
        try:
            head_ref = self._exec_git(['symbolic-ref', 'HEAD'])
        except GitWrapperError as err:
            if not err.is_git_error:
                raise err
            else:
                return None
        match_obj = _re.compile(r'^refs\/heads\/(.*)$').match(head_ref)
        try:
            return match_obj.group(1).rstrip()
        except (IndexError, AttributeError):
            raise GitWrapperError('Error: Unknown symbolic-ref for HEAD')
        return

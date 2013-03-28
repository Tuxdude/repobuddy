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
import shlex as _shlex
import subprocess as _subprocess

from repobuddy.utils import Logger, RepoBuddyBaseException


class GitWrapperError(RepoBuddyBaseException):
    def __init__(self, error_str, is_git_error, git_error_msg=''):
        super(GitWrapperError, self).__init__(error_str)
        self.is_git_error = is_git_error
        self.git_error_msg = git_error_msg
        return


class GitWrapper(object):
    def _exec_git(self,
                  command,
                  capture_stdout=False,
                  capture_stderr=False,
                  is_clone=False):
        if is_clone:
            git_command = _shlex.split('git ' + command)
        else:
            git_command = _shlex.split(
                'git --work-tree=. --git-dir=.git ' + command)
        Logger.debug('Exec: git %s' % command)
        try:
            kwargs = {}
            if capture_stdout:
                kwargs['stdout'] = _subprocess.PIPE
            if capture_stderr:
                kwargs['stderr'] = _subprocess.PIPE

            proc = _subprocess.Popen(
                git_command,
                cwd=self._base_dir,
                **kwargs)
            (out_msg, err_msg) = proc.communicate()
            return_code = proc.wait()

            if not out_msg is None:
                out_msg = out_msg.decode('utf-8')
            if not err_msg is None:
                err_msg = err_msg.decode('utf-8')

            if return_code != 0:
                if capture_stderr:
                    raise GitWrapperError(
                        'Command \'git %s\' failed' % command,
                        is_git_error=True,
                        git_error_msg=err_msg.rstrip())
                else:
                    raise GitWrapperError(
                        'Command \'git %s\' failed' % command,
                        is_git_error=True)

            if capture_stdout and capture_stderr:
                return (out_msg.rstrip(), err_msg.rstrip())
            elif capture_stdout:
                return out_msg.rstrip()
            elif capture_stderr:
                return err_msg.rstrip()
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
        self._exec_git('clone -b %s %s %s' % (branch, remote_url, dest_dir),
                       is_clone=True)
        if _os.path.isabs(dest_dir):
            self._base_dir = dest_dir
        else:
            self._base_dir = _os.path.join(self._base_dir, dest_dir)
        return

    def update_index(self):
        self._exec_git('update-index -q --ignore-submodules --refresh')
        return

    def get_untracked_files(self):
        untracked_files = self._exec_git(
            'ls-files --exclude-standard --others --',
            capture_stdout=True)
        if untracked_files == '':
            return []
        else:
            return untracked_files.split('\n')

    def get_unstaged_files(self):
        unstaged_files = self._exec_git(
            'diff-files --name-status -r --ignore-submodules --',
            capture_stdout=True)
        if unstaged_files == '':
            return []
        else:
            return unstaged_files.split('\n')

    def get_uncommitted_staged_files(self):
        uncommited_staged_files = self._exec_git(
            'diff-index --cached --name-status -r --ignore-submodules HEAD --',
            capture_stdout=True)
        if uncommited_staged_files == '':
            return []
        else:
            return uncommited_staged_files.split('\n')

    def get_current_branch(self):
        try:
            out_msg = self._exec_git('symbolic-ref HEAD',
                                     capture_stdout=True,
                                     capture_stderr=True)[0]
        except GitWrapperError as err:
            if not err.is_git_error:
                raise err
            elif err.git_error_msg == 'fatal: ref HEAD is not a symbolic ref':
                return None
            else:
                raise err

        try:
            return _re.match(r'^refs\/heads\/(.*)$', out_msg).group(1)
        except (IndexError, AttributeError):
            raise GitWrapperError('Error: Unknown symbolic-ref for HEAD')
        return

    def get_current_tag(self):
        try:
            out_msg = self._exec_git(
                'name-rev --name-only --tags --no-undefined HEAD',
                capture_stdout=True,
                capture_stderr=True)[0]
        except GitWrapperError as err:
            if not err.is_git_error:
                raise err
            elif not _re.match(
                    r'^fatal: cannot describe \'[0-9a-f]{40}\'$',
                    err.git_error_msg) is None:
                return None
            else:
                raise err

        try:
            tag = _re.match(r'^([^^~]+)(\^0){0,1}$', out_msg).group(1)
        except (IndexError, AttributeError):
            tag = None
        return tag

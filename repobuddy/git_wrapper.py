#
#   Copyright (C) 2013 Ash (Tuxdude) <tuxdude.github@gmail.com>
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
"""
.. module: git_wrapper
   :platform: Unix, Windows
   :synopsis: Helper classes to run the git commands for ``repobuddy``.
.. moduleauthor: Ash <tuxdude.github@gmail.com>

"""

import os as _os
import re as _re
import shlex as _shlex
import subprocess as _subprocess

from repobuddy.utils import Logger, RepoBuddyBaseException


class GitWrapperError(RepoBuddyBaseException):

    """Exception raised by :class:`GitWrapper`.

    :ivar is_git_error: Set to ``True`` if :class:`GitWrapper` got back a
        non-zero status after executing of any of the git commands, otherwise
        ``False``.

    """

    def __init__(self, error_str, is_git_error, git_error_msg=''):
        super(GitWrapperError, self).__init__(error_str)
        self.is_git_error = is_git_error
        self.git_error_msg = git_error_msg
        return


class GitWrapper(object):

    """Helper for invoking ``git``.

    Provides a way to access and/or control the state of a git repository.
    Internally, it executes ``git`` commands in the work-tree for various
    operations.

    """

    def _exec_git(self,
                  command,
                  capture_stdout=False,
                  capture_stderr=False,
                  no_work_tree=False,
                  no_git_dir=False):
        """Execute the git command.

        :param command: The command string.
        :type command: str
        :param capture_stdout: If ``True``, ``stdout`` is captured, otherwise
            not.
        :type capture_stdout: Boolean
        :param capture_stderr: If ``True``, ``stderr` is captured, otherwise
            not.
        :param no_work_tree: If ``False``, ``--work-tree=.`` command line
            argument is passed to ``git``, otherwise not.
        :type no_work_tree: Boolean
        :param no_git_dir: If ``False``, ``--git-dir=.git`` command line
            argument is passed to ``git``, otherwise not.
        :type no_git_dir: Boolean
        :returns: Depends on the parameters to this method:

            - If both ``capture_stdout`` are ``capture_stderr`` are ``True``,
              a tuple with the corresponding strings as output, i.e.
              ``(stdout, stderr)``
            - If one of ``capture_stdout`` and ``capture_stderr`` is True, but
              not both, the corresponding output as a string.
            - If both ``capture_stdout`` and ``capture_stderr`` are ``False``,
              None.
        :rtype: str or Tuple
        :raises: :exc:`GitWrapperError` if the ``git`` command executed
            returns a non-zero status.

        """
        git_command = 'git '

        if not no_work_tree:
            git_command += '--work-tree=. '

        if not no_git_dir:
            git_command += '--git-dir=.git '

        git_command += command

        Logger.debug('Exec: git %s' % command)
        try:
            kwargs = {}
            if capture_stdout:
                kwargs['stdout'] = _subprocess.PIPE
            if capture_stderr:
                kwargs['stderr'] = _subprocess.PIPE

            proc = _subprocess.Popen(   # pylint: disable=W0142
                _shlex.split(git_command),
                cwd=self._base_dir,
                **kwargs)

            try:
                (out_msg, err_msg) = proc.communicate()
            except:
                proc.kill()
                proc.wait()
                raise

            return_code = proc.poll()

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

    def __init__(self, base_dir):
        """Initializer.

        :param base_dir: Absolute path of the git repository work-tree.
        :type base_dir: str
        :returns: None
        :raises: :exc:`GitWrapperError` if ``base_dir`` is not an absolute
            path.

        """
        if not _os.path.isabs(base_dir):
            raise GitWrapperError(
                'Error: base_dir \'' + base_dir +
                '\' needs to be an absolute path')
        self._base_dir = base_dir
        return

    # It also changes the current Dir to dest_dir
    def clone(self, remote_url, branch, dest_dir):
        """Clone a repo.

        Executes ``git clone -b branch remote_url dest_dir``. At the end of
        the ``clone`` operation, the working directory is changed to
        ``dest_dir``.

        :param remote_url: URL of the repository.
        :type remote_url: str
        :param branch: Branch to checkout after the clone.
        :type branch: str
        :dest_dir: Destination path to store the cloned repository.
        :returns: None
        :raises: :exc:`GitWrapperError` if the ``git clone`` command fails.

        """
        self._exec_git('clone -b %s %s %s' % (branch, remote_url, dest_dir),
                       no_work_tree=True, no_git_dir=True)
        if _os.path.isabs(dest_dir):
            self._base_dir = dest_dir
        else:
            self._base_dir = _os.path.join(self._base_dir, dest_dir)
        return

    def update_index(self):
        """Refresh the index.

        Executes ``git update-index -q --ignore-submodules --refresh``.

        :returns: None
        :raises: :exc:`GitWrapperError` if the ``git update-index`` command
            fails.

        """
        self._exec_git('update-index -q --ignore-submodules --refresh')
        return

    def get_untracked_files(self):
        """Get a list of all untracked files in the repository.

        Returns the files in ``git ls-files --exclude-standard --others --``
        as a list.

        :returns: List of untracked files.
        :rtype: list of str
        :raises: :exc:`GitWrapperError` if the ``git ls-files`` command fails.

        """
        untracked_files = self._exec_git(
            'ls-files --exclude-standard --others --',
            capture_stdout=True)
        if untracked_files == '':
            return []
        else:
            return untracked_files.split('\n')

    def get_unstaged_files(self):
        """Get a list of all unstaged files in the repository.

        Returns the files in ``git diff-files --name-status -r
        --ignore-submodules --`` as a list.

        :returns: List of unstaged files.
        :rtype: list of str
        :raises: :exc:`GitWrapperError` if the ``git diff-files`` command
            fails.

        """
        unstaged_files = self._exec_git(
            'diff-files --name-status -r --ignore-submodules --',
            capture_stdout=True)
        if unstaged_files == '':
            return []
        else:
            return unstaged_files.split('\n')

    def get_uncommitted_staged_files(self):
        """Get a list of all uncommitted but staged files.

        Returns the files in ``git diff-index --cached --name-status -r
        --ignore-submodules``.

        :returns: List of uncommitted files in the staging area.
        :rtype: list of str
        :raises: :exc:`GitWrapperError` if the ``git diff-index`` command
            fails.

        """
        uncommited_staged_files = self._exec_git(
            'diff-index --cached --name-status -r ' +
            '--ignore-submodules HEAD --',
            capture_stdout=True)
        if uncommited_staged_files == '':
            return []
        else:
            return uncommited_staged_files.split('\n')

    def get_current_branch(self):
        """Get the currently checked out branch.

        :returns: Currently checked out Branch name if ``HEAD`` points to a
            branch, otherwise ``None``
        :rtype: str
        :raises: :exc:`GitWrapperError` on errors.

        """
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
        """Get the currently checked out tag.

        :returns: The tag name which is currently checked out, ``None``
            otherwise. If the commit pointed by ``HEAD`` contains more than
            one tag, the returned tag name could be any one of those tags.
        :rtype: str
        :raises: :exc:`GitWrapperError` on errors.

        """
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

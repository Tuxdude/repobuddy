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
import subprocess as _subprocess
import shlex as _shlex
import shutil as _shutil

from repobuddy.utils import RepoBuddyBaseException


class ShellError(RepoBuddyBaseException):
    def __init__(self, error_str):
        super(ShellError, self).__init__(error_str)
        return


class ShellHelper:
    @classmethod
    def exec_command(cls, cmd, base_dir):
        print '>> ' + ' '.join(cmd)
        try:
            proc = _subprocess.Popen(
                cmd,
                cwd=base_dir)
            return_code = proc.wait()
            if return_code != 0:
                raise ShellError('Command \'%s\' failed!' % cmd)
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


class TestCommon(object):
#    def __init__(self):
#        return

    def git_append_add_commit(self, text, filename, commit_log, exec_dir):
        ShellHelper.append_text_to_file(text, filename, exec_dir)
        ShellHelper.exec_command(
            _shlex.split('git add %s' % filename),
            exec_dir)
        ShellHelper.exec_command(
            _shlex.split('git commit -m "%s"' % commit_log),
            exec_dir)
        return

    def setup_test_repos(self, base_dir):
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
        self.git_append_add_commit(
            'First content...\n',
            'README',
            'First commit.',
            clone_repo1)
        self.git_append_add_commit(
            'Hardly useful...\n',
            'dummy',
            'Here we go.',
            clone_repo1)
        self.git_append_add_commit(
            'More content...\n',
            'README',
            'Appending to README.',
            clone_repo1)

        # Push the changes to origin
        ShellHelper.exec_command(
            _shlex.split('git push origin master'),
            clone_repo1)

        # Make some more changes, but do not push yet
        self.git_append_add_commit(
            'Another line...\n',
            'README',
            'One more to README.',
            clone_repo1)
        self.git_append_add_commit(
            'Dummy2 in place...\n',
            'dummy2',
            'Creating dummy2.',
            clone_repo1)

        # Create clone2 from the origin
        ShellHelper.exec_command(
            _shlex.split('git clone %s %s' % (origin_repo_url, clone_repo2)),
            base_dir)

        # Add and commit changes in clone2
        self.git_append_add_commit(
            'Another line...\n',
            'dummy',
            'One more to dummy.',
            clone_repo2)
        self.git_append_add_commit(
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
        self.git_append_add_commit(
            'More lines...\n',
            'dummy',
            'Another line to dummy.',
            clone_repo2)
        self.git_append_add_commit(
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

        return

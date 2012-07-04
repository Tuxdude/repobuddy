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
from RepoBuddyUtils import Logger

class GitWrapperError(Exception):
    def __init__(self, errorStr, isGitError):
        self._errorStr = errorStr
        self.isGitError = isGitError
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return str(self._errorStr)

class GitWrapper(object):
    def _execGit(self, command, captureStdOut = True):
        gitCmd = command[:]
        gitCmd.insert(0, 'git')
        Logger.Debug('Exec: ' + ' '.join(gitCmd))
        try:
            if not captureStdOut:
                proc = _subprocess.Popen(
                        gitCmd,
                        cwd = self._baseDir,
                        stderr = _subprocess.PIPE)
            else:
                proc = _subprocess.Popen(
                        gitCmd,
                        cwd = self._baseDir,
                        stdout = _subprocess.PIPE,
                        stderr = _subprocess.PIPE)
            (outMsg, errMsg) = proc.communicate()
            returnCode = proc.wait()
            if not returnCode is 0:
                raise GitWrapperError(str(errMsg), isGitError = True)
            if captureStdOut:
                return outMsg
        except OSError as err:
            raise GitWrapperError(str(err), isGitError = False)
        return

    # Constructor
    # baseDir - is the base directory of the git repo
    def __init__(self, baseDir):
        if not _os.path.isabs(baseDir):
            raise GitWrapperError(
            'Error: baseDir \'' + baseDir + '\' needs to be an absolute path')
        self._baseDir = baseDir
        return

    def __del__(self):
        return

    # Clone the git repo at remoteUrl checking out branch
    # Equivalent of git clone -b branch remoteUrl
    # It also changes the current Dir to destDir
    def clone(self, remoteUrl, branch, destDir):
        self._execGit(
                ['clone', '-b', branch, remoteUrl, destDir],
                captureStdOut = False)
        if _os.path.isabs(destDir):
            self._baseDir = destDir
        else:
            self._baseDir = _os.path.join(self._baseDir, destDir)
        return

    def updateIndex(self):
        self._execGit(
                ['update-index', '-q', '--ignore-submodules', '--refresh'],
                captureStdOut = False)
        return

    def getUnstagedChanges(self):
        try:
            self._execGit(
                    ['diff-files', '--quiet', '--ignore-submodules', '--'])
        except GitWrapperError as err:
            if not err.isGitError:
                raise err
            unstagedChanges = self._execGit(
                    ['diff-files', '--name-status', '-r',
                     '--ignore-submodules', '--'])
            return unstagedChanges
        return

    def getUncommittedIndexChanges(self):
        try:
            self._execGit(
                    ['diff-index', '--cached', '--quiet', 'HEAD',
                     '--ignore-submodules', '--'])
        except GitWrapperError as err:
            if not err.isGitError:
                raise err
            uncommitedIndexChanges = self._execGit(
                    ['diff-index', '--cached', '--name-status', '-r',
                     '--ignore-submodules', 'HEAD', '--'])
            return uncommitedIndexChanges
        return

    def getCurrentBranch(self):
        try:
            headRef = self._execGit(['symbolic-ref', 'HEAD'])
        except GitWrapperError as err:
            if not err.isGitError:
                raise err
            else:
                return None
        matchObj = _re.compile(r'^refs\/heads\/(.*)$').match(headRef)
        try:
            return matchObj.group(1)
        except IndexError, AttributeError:
            raise GitWrapperError('Error: Unknown symbolic-ref for HEAD')
        return

#
#   Copyright (C) 2012 Ash (Tuxdude) <tuxdude.github@gmail.com>
#
#   This file is part of repodude.
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

import subprocess

class GitWrapperError:
    def __init__(self, errorStr):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return repr(self._errorStr)

class GitWrapper:
    def _execGit(self, command, dontChangeDir = False):
        gitCmd = command[:]
        gitCmd.insert(0, 'git')
        print 'Exec: ' + ' '.join(gitCmd)
        try:
            if not dontChangeDir:
                proc = subprocess.Popen(
                        gitCmd,
                        cwd = self._baseDir,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE)
            else:
                proc = subprocess.Popen(
                        gitCmd,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE)
            (outMsg, errMsg) = proc.communicate()
            print outMsg
            if errMsg != '':
                print errMsg
            returnCode = proc.wait()
            if returnCode != 0:
                raise GitWrapperError(str(errMsg))
        except OSError as err:
            raise GitWrapperError(str(err))
        return

    # Constructor
    # baseDir - is the base directory of the git repo
    def __init__(self, baseDir):
        self._baseDir = baseDir
        return

    def __del__(self):
        return

    # Clone the git repo at remoteUrl checking out branch
    # Equivalent of git clone -b branch remoteUrl
    def clone(self, remoteUrl, branch, destDir):
        self._execGit(['clone', '-b', branch, remoteUrl, destDir])
        return

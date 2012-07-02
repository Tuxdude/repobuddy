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

import os
from GitWrapper import GitWrapper, GitWrapperError
from RepoBuddyUtils import FileLock, FileLockError
from RepoConfigParser import RepoConfigParser, RepoConfigParserError

class CommandHandlerError(Exception):
    def __init__(self, errorStr):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return repr(self._errorStr)

class CommandHandler(object):
    def _getXmlConfig(self):
        config = 'config/repoconfig-example.xml'

        # Parse the config file
        repoConfigParser = RepoConfigParser()
        try:
            repoConfigParser.parse(config)
        except RepoConfigParserError as err:
            raise CommandHandlerError(str(err))

        self._xmlConfig = repoConfigParser.getConfig()
        return

    # Retrieve the client spec corresponding to the command-line argument
    def _getClientSpec(self, clientSpecName):
        foundClientSpec = False
        clientSpec = None
        for spec in self._xmlConfig.clientSpecList:
            if spec.name == clientSpecName:
                clientSpec = spec
                break
        if clientSpec == None:
            raise CommandHandlerError(
                    'Error: Unable to find the Client Spec: \'' +
                    args.clientSpec + '\'')
        return clientSpec

    # Calls execMethod while holding the .repobuddy/lock
    def _execWithLock(self, execMethod, *methodArgs):
        self._repoBuddyDir = os.path.join(self._currentDir, '.repobuddy')
        lockFile = os.path.join(self._repoBuddyDir, 'lock')

        if not os.path.isdir(self._repoBuddyDir):
            # Create the .repobuddy directory if it does not exist already
            try:
                os.mkdir(self._repoBuddyDir)
            except OSError as err:
                raise CommandHandlerError('Error: ' + str(err))
        else:
            print 'Found an existing .repobuddy directory...'

        try:
            # Acquire the lock before doing anything else
            with FileLock(lockFile) as lock:
                print 'Lock \'' + lockFile + '\' acquired'
                execMethod(*methodArgs)
        except FileLockError as err:
            # If it is a timeout error, it could be one of the following:
            # *** another instance of repobuddy is running
            # *** repobuddy was killed earlier without releasing the lock file
            if err.isTimeOut:
                raise CommandHandlerError(
                        'Error: Lock file ' + lockFile + ' already exists\n' +
                        'Is another instance of repobuddy running ?')
            else:
                raise CommandHandlerError(str(err))
        except GitWrapperError as err:
            raise CommandHandlerError('Error: Git said => ' + str(err))

        return

    # Init command which runs after acquiring the Lock
    def _execInit(self, args):
        # Download the XML config file
        self._getXmlConfig()

        # Get the Client Spec corresponding to the Command line argument
        clientSpec = self._getClientSpec(args.clientSpec)

        # Process each repo in the Client Spec
        for repo in clientSpec.repoList:
            git = GitWrapper(self._currentDir)
            git.clone(repo.url, repo.branch, repo.destination)

        return

    def __init__(self):
        self._currentDir = os.getcwd()
        return

    def getHandlers(self):
        handlers = { }
        handlers['init'] = self.initCommandHandler
        handlers['status'] = self.statusCommandHandler
        handlers['help'] = self.helpCommandHandler
        return handlers

    def initCommandHandler(self, args):
        self._execWithLock(self._execInit, args)
        return

    def statusCommandHandler(self, args):
        print 'status command'
        return

    def helpCommandHandler(self, args):
        print 'help ' + args.command
        return

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
import shutil as _shutil
from GitWrapper import GitWrapper, GitWrapperError
from RepoBuddyUtils import FileLock, FileLockError, Logger
from RepoConfigParser import RepoConfigParser, RepoConfigParserError
from ClientInfo import ClientInfo, ClientInfoError

class CommandHandlerError(Exception):
    def __init__(self, errorStr):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return str(self._errorStr)

class CommandHandler(object):
    def _getXmlConfig(self):
        # FIXME: Support various protcols for fetching the config XML file
        inputConfig = _os.path.join(
                self._currentDir,
                'config/repoconfig-example.xml')

        # Copy the xml config file to .repobuddy dir
        try:
            _shutil.copyfile(inputConfig, self._configFile)
        except IOError as err:
            raise CommandHandlerError('Error: ' + str(err))
        return

    def _parseXmlConfig(self):
        # Parse the config file
        repoConfigParser = RepoConfigParser()
        try:
            repoConfigParser.parse(self._configFile)
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
                    clientSpecName + '\'')
        return clientSpec

    def _storeClientInfo(self, clientSpecName):
        try:
            clientInfo = ClientInfo()
            clientInfo.setClientSpec(clientSpecName)
            clientInfo.setXmlConfig('config.xml')
            clientInfo.write(self._clientInfoFile)
        except ClientInfoError as err:
            raise CommandHandlerError(str(err))
        return

    def _getClientInfo(self):
        try:
            clientInfo = ClientInfo(self._clientInfoFile)
            return clientInfo.getClientSpec()
        except ClientInfoError as err:
            raise CommandHandlerError(str(err))
        return

    def _isClientInitialized(self):
        return _os.path.isfile(
                _os.path.join(self._repoBuddyDir, 'client.config'))

    # Calls execMethod while holding the .repobuddy/lock
    def _execWithLock(self, execMethod, *methodArgs):
        lockFile = _os.path.join(self._repoBuddyDir, 'lock')

        if not _os.path.isdir(self._repoBuddyDir):
            # Create the .repobuddy directory if it does not exist already
            try:
                _os.mkdir(self._repoBuddyDir)
            except OSError as err:
                raise CommandHandlerError('Error: ' + str(err))
        else:
            Logger.Debug('Found an existing .repobuddy directory...')

        try:
            # Acquire the lock before doing anything else
            with FileLock(lockFile) as lock:
                Logger.Debug('Lock \'' + lockFile + '\' acquired')
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
        if self._isClientInitialized():
            raise CommandHandlerError('Error: Client is already initialized')

        # Download the XML config file
        self._getXmlConfig()

        # Parse the XML config file
        self._parseXmlConfig()

        # Get the Client Spec corresponding to the Command line argument
        clientSpec = self._getClientSpec(args.clientSpec)

        # Process each repo in the Client Spec
        for repo in clientSpec.repoList:
            git = GitWrapper(self._currentDir)
            git.clone(repo.url, repo.branch, repo.destination)

        # Create the client file, writing the following
        # The config file name
        # The client spec chosen
        self._storeClientInfo(args.clientSpec)

        return

    def _execStatus(self, args):
        if not self._isClientInitialized():
            raise CommandHandlerError(
                    'Error: Uninitialized client, ' +
                    'please run init to initialize the client first')

        # Parse the XML config file
        self._parseXmlConfig()

        # Get the client spec name from client info
        client = self._getClientSpec(self._getClientInfo())

        # Process each repo in the Client Spec
        for repo in client.repoList:
            git = GitWrapper(_os.path.join(self._currentDir, repo.destination))
            Logger.Msg('####################################################')
            Logger.Msg('Repo: ' + repo.destination)
            Logger.Msg('Remote URL: ' + repo.url)
            currentBranch = git.getCurrentBranch()
            dirty = False

            if currentBranch is None:
                currentBranch = 'Detached HEAD'

            if currentBranch != repo.branch:
                Logger.Msg('Original Branch: ' + repo.branch)
                Logger.Msg('Current Branch: ' + currentBranch + '\n')
            else:
                Logger.Msg('Branch: ' + repo.branch + '\n')

            untrackedFiles = git.getUntrackedFiles()
            if not untrackedFiles is None:
                Logger.Msg('Untracked Files: \n' + untrackedFiles + '\n')
                dirty = True
                
            unstagedFiles = git.getUnstagedFiles()
            if not unstagedFiles is None:
                Logger.Msg('Unstaged Files: \n' + unstagedFiles + '\n')
                dirty = True

            uncommittedStagedFiles = git.getUncommittedStagedFiles()
            if not uncommittedStagedFiles is None:
                Logger.Msg('Uncommitted Changes: \n' + uncommittedStagedFiles + '\n')
                dirty = True

            if not dirty:
                Logger.Msg('No uncommitted changes')
        Logger.Msg('####################################################')
        return

    def __init__(self):
        self._currentDir = _os.getcwd()
        self._repoBuddyDir = _os.path.join(self._currentDir, '.repobuddy')
        self._configFile = _os.path.join(self._repoBuddyDir, 'config.xml')
        self._clientInfoFile = _os.path.join(self._repoBuddyDir, 'client.config')
        return

    def getHandlers(self):
        handlers = { }
        handlers['init'] = self.initCommandHandler
        handlers['status'] = self.statusCommandHandler
        return handlers

    def initCommandHandler(self, args):
        self._execWithLock(self._execInit, args)
        return

    def statusCommandHandler(self, args):
        self._execWithLock(self._execStatus, args)
        return

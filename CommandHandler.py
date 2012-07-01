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

class CommandHandlerError(Exception):
    def __init__(self, errorStr):
        self._errorStr = errorStr
        return

    def __str__(self):
        return str(self._errorStr)

    def __repr__(self):
        return repr(self._errorStr)

class CommandHandler(object):
    def __init__(self, xmlConfig):
        self._xmlConfig = xmlConfig
        return

    def getHandlers(self):
        handlers = { }
        handlers['init'] = self.initCommandHandler
        handlers['status'] = self.statusCommandHandler
        handlers['help'] = self.helpCommandHandler
        return handlers

    def initCommandHandler(self, args):
        foundClientSpec = False
        clientSpec = None
        for spec in self._xmlConfig.clientSpecList:
            if spec.name == args.clientSpec:
                clientSpec = spec
                break
        if clientSpec == None:
            raise CommandHandlerError(
                    'Unable to find the Client Spec: \'' +
                    args.clientSpec + '\'')
        currentDir = os.getcwd()
        for repo in clientSpec.repoList:
            git = GitWrapper(currentDir)
            try:
                git.clone(repo.url, repo.branch, repo.destination)
            except GitWrapperError as err:
                raise CommandHandlerError('Error: Git said => ' + str(err))
        return

    def statusCommandHandler(self, args):
        print 'status command'
        return

    def helpCommandHandler(self, args):
        print 'help ' + args.command
        return

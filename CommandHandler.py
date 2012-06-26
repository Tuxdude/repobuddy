#
#   Copyright (C) 2012 Ash (Tuxdude)
#   tuxdude.github@gmail.com
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

class CommandHandler:
    def __init__(self, xmlConfig):
        self._xmlConfig = xmlConfig
        return

    def GetHandlers(self):
        handlers = { }
        handlers['init'] = self.InitCommandHandler
        handlers['status'] = self.StatusCommandHandler
        handlers['help'] = self.HelpCommandHandler
        return handlers

    def InitCommandHandler(self, args):
        print 'init ' + args.clientSpec
        return

    def StatusCommandHandler(self, args):
        print 'status command'
        return

    def HelpCommandHandler(self, args):
        print 'help ' + args.command
        return

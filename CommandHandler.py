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

class CommandHandler:
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
        print 'init ' + args.clientSpec
        return

    def statusCommandHandler(self, args):
        print 'status command'
        return

    def helpCommandHandler(self, args):
        print 'help ' + args.command
        return

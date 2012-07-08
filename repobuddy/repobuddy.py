#! /usr/bin/env python
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

import sys as _sys
from arg_parser import ArgParser, ArgParserError, ArgParserExitNoError
from command_handler import CommandHandler, CommandHandlerError
from utils import Logger

def main():
    # Initialize the Command Handler core
    command_handler = CommandHandler()
    handlers = command_handler.get_handlers()

    # Parse the command line arguments and invoke the handler
    arg_parser = ArgParser(handlers)
    try:
        arg_parser.parse(_sys.argv[1:])
    except (CommandHandlerError, ArgParserError) as err:
        err_msg = str(err)
        if not err_msg is 'None':
            Logger.error(err_msg)
        _sys.exit(1)
    except ArgParserExitNoError:
        pass

    _sys.exit(0)

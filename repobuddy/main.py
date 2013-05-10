#
#   Copyright (C) 2013 Ash (Tuxdude) <tuxdude.github@gmail.com>
#
#   This file is part of repobuddy.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
.. module: repobuddy.main
   :platform: Unix, Windows
   :synopsis: Module to define the entry point for ``repobuddy``.
.. moduleauthor: Ash <tuxdude.github@gmail.com>

"""

import sys as _sys

from repobuddy.arg_parser import ArgParser, ArgParserError
from repobuddy.command_handler import CommandHandler, CommandHandlerError
from repobuddy.utils import Logger


def run_repobuddy():
    """Invoke repobuddy with the command line arguments.

    The application exits with status ``1`` on errors, ``0`` otherwise.

    returns: None

    """
    # Initialize the Command Handler core
    command_handler = CommandHandler()
    handlers = command_handler.get_handlers()

    # Parse the command line arguments and invoke the handler
    arg_parser = ArgParser(handlers)
    try:
        arg_parser.parse(_sys.argv[1:])
    except (CommandHandlerError, ArgParserError) as err:
        if isinstance(err, CommandHandlerError) or \
           (not err.exit_prog_without_error):
            err_msg = str(err)
            if not err_msg is 'None':
                Logger.error(err_msg)
            _sys.exit(1)

    _sys.exit(0)

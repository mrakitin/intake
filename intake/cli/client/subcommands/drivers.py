#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2018, Anaconda, Inc. and Intake contributors
# All rights reserved.
#
# The full license is in the LICENSE file, distributed with this software.
#-----------------------------------------------------------------------------
'''
CLI for listing, enabling, disabling intake drivers
'''

import logging
log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
import errno
from importlib import import_module
import inspect
import os
import sys

# External imports

# Intake imports
from intake import __version__
from intake.cli.util import Subcommand
from intake.source.discovery import autodiscover, autodiscover_all, enable, disable
from intake.config import confdir

#-----------------------------------------------------------------------------
# API
#-----------------------------------------------------------------------------

class Drivers(Subcommand):
    '''
    List, enable, and disable intake drivers.
    '''

    name = "drivers"

    def initialize(self):
        sub_parser = self.parser.add_subparsers()

        list = sub_parser.add_parser('list', help='Show all intake drivers.')
        list.add_argument('-v', '--verbose', action='store_true', help='Show module path.')
        list.set_defaults(invoke=self._list)

        enable = sub_parser.add_parser('enable', help='Enable an intake driver.')
        enable.add_argument('name', type=str, help='Driver name')
        enable.add_argument('driver', type=str, help='Module path and class name, as in package.submodule.ClassName')
        enable.set_defaults(invoke=self._enable)

        disable = sub_parser.add_parser('disable', help='Disable one or more intake drivers.')
        disable.add_argument('names', type=str, help='Driver names', nargs='+')
        disable.set_defaults(invoke=self._disable)

    def invoke(self, args):
        self.parser.print_help()

    def _list(self, args):
        if args.verbose:
            fmt = '{name:<30}{cls.__module__}.{cls.__name__} @ {file}'
        else:
            fmt = '{name:<30}{cls.__module__}.{cls.__name__}'
        drivers_by_name = autodiscover()   # dict mapping name to driver
        all_drivers = autodiscover_all()  # listof (name, driver)
        print("Enabled:", file=sys.stderr)
        for name, cls in drivers_by_name.items():
            print(fmt.format(name=name, cls=cls, file=inspect.getfile(cls)),
                  file=sys.stderr)
        print("\nNot enabled:", file=sys.stderr)
        for name, cls in all_drivers:
            if drivers_by_name[name] is not cls:
                print(fmt.format(name=name, cls=cls, file=inspect.getfile(cls)),
                    file=sys.stderr)

    def _enable(self, args):
        enable(args.name, args.driver)

    def _disable(self, args):
        for name in args.names:
            disable(name)

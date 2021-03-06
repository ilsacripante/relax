###############################################################################
#                                                                             #
# Copyright (C) 2016 Troels Schwarz-Linnet                                    #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for various os and sys python module purposes."""

# Python module imports.
from os import chdir, getcwd

# relax module imports.
import lib.arg_check
from status import Status; status = Status()


def cd(path, verbose=False):
    """The equivalent of python module os.chdir(path).  Change the current working directory to the specified path.

    @keyword verbose:  A flag which if True will cause the previous directory to be printed.
    @type verbose:     bool
    @param path:       The path to the directory for the current working directory.
    @type  path:       str
    """

    # Check that the path is a string.
    lib.arg_check.is_str(path, name="path", can_be_none=False, raise_error=True)

    # Replace any remains of " and '
    path = path.replace('"', '').replace("'", "")

    # Print previous current working directory.
    if verbose:
        print("The current working directory was: %s"%getcwd())

    # Change the current working directory.
    chdir(path)

    # Print current working directory.
    print("The current working directory is now changed to: %s"%getcwd())

    # Notify observers that the current working directory has changed.
    status.observers.system_cwd_path.notify()


def pwd(verbose=True):
    """Print and return string of the current working directory.  Equivalent of python module os.getcwd(). 

    @keyword verbose:   A flag which if True will cause the current directory to be printed.
    @type verbose:      bool
    @return:            Path to the current working directory.
    @rtype:             str
    """

    # Get the current working directory.
    cwd = getcwd()

    # Print previous current working directory.
    if verbose:
        print("The current working directory is: %s"%cwd)

    return cwd

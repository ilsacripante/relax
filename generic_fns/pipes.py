###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2009 Edward d'Auvergne                             #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for manipulating data pipes."""


# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import RelaxError, RelaxNoPipeError, RelaxPipeError

# Relaxation curve fitting modules compilation test.
C_module_exp_fn = True
try:
    from maths_fns.relax_fit import func
except ImportError:
    C_module_exp_fn = False


def copy(pipe_from=None, pipe_to=None):
    """Copy the contents of the source data pipe to a new target data pipe.

    If the 'pipe_from' argument is None then the current data pipe is assumed as the source.  The
    data pipe corresponding to 'pipe_to' cannot exist.

    @param pipe_from:   The name of the source data pipe to copy the data from.
    @type pipe_from:    str
    @param pipe_to:     The name of the target data pipe to copy the data to.
    @type pipe_to:      str
    """

    # Test if the pipe already exists.
    if pipe_to in ds.keys():
        raise RelaxPipeError, pipe_to

    # The current data pipe.
    if pipe_from == None:
        pipe_from = cdp_name()

    # Copy the data.
    ds[pipe_to] = ds[pipe_from].__clone__()


def create(pipe_name=None, pipe_type=None, switch=True):
    """Create a new data pipe.

    The current data pipe will be changed to this new data pipe.


    @keyword pipe_name: The name of the new data pipe.
    @type pipe_name:    str
    @keyword pipe_type: The new data pipe type which can be one of the following:
        'ct':  Consistency testing,
        'frame order':  The Frame Order theories.
        'jw':  Reduced spectral density mapping,
        'hybrid':  The hybridised data pipe.
        'mf':  Model-free analysis,
        'N-state':  N-state model of domain dynamics,
        'noe':  Steady state NOE calculation,
        'relax_fit':  Relaxation curve fitting,
        'relax_disp':  Relaxation dispersion,
        'srls':  SRLS analysis.
    @type pipe_type:    str
    @keyword switch:    If True, this new pipe will be switched to, otherwise the current data pipe
                        will remain as is.
    @type switch:       bool
    """

    # List of valid data pipe types.
    valid = ['ct', 'frame order', 'jw', 'hybrid', 'mf', 'N-state', 'noe', 'relax_fit', 'relax_disp', 'srls']

    # Test if pipe_type is valid.
    if not pipe_type in valid:
        raise RelaxError, "The data pipe type " + repr(pipe_type) + " is invalid and must be one of the strings in the list " + repr(valid) + "."

    # Test that the C modules have been loaded.
    if pipe_type == 'relax_fit' and not C_module_exp_fn:
        raise RelaxError, "Relaxation curve fitting is not available.  Try compiling the C modules on your platform."

    # Add the data pipe.
    ds.add(pipe_name=pipe_name, pipe_type=pipe_type)


def cdp_name():
    """Return the name of the current data pipe.
    
    @return:        The name of the current data pipe.
    @rtype:         str
    """

    return ds.current_pipe


def delete(pipe_name=None):
    """Delete a data pipe.

    @param pipe_name:   The name of the data pipe to delete.
    @type pipe_name:    str
    """

    # Test if the data pipe exists.
    if pipe_name != None:
        test(pipe_name)

    # Delete the data pipe.
    del ds[pipe_name]

    # Set the current data pipe to None if it is the deleted data pipe.
    if ds.current_pipe == pipe_name:
        ds.current_pipe = None


def get_pipe(name=None):
    """Return a data pipe.

    @keyword name:  The name of the data pipe to return.  If None, the current data pipe is
                    returned.
    @type name:     str or None
    @return:        The current data pipe.
    @rtype:         PipeContainer instance
    """

    # The name of the data pipe.
    if name == None:
        name = cdp_name()

    # Test if the data pipe exists.
    test(name)

    return ds[name]


def get_type(name=None):
    """Return the type of the data pipe.

    @keyword name:  The name of the data pipe.  If None, the current data pipe is used.
    @type name:     str or None
    @return:        The current data pipe type.
    @rtype:         str
    """

    # The name of the data pipe.
    if name == None:
        name = cdp_name()

    # Get the data pipe.
    pipe = get_pipe(name)

    return pipe.pipe_type


def has_pipe(name):
    """Determine if the relax data store contains the data pipe.

    @param name:    The name of the data pipe.
    @type name:     str
    @return:        True if the data pipe exists, False otherwise.
    @rtype:         bool
    """

    # Check.
    if name in ds:
        return True
    else:
        return False


def list():
    """Print the details of all the data pipes."""

    # Heading.
    print("%-20s%-20s" % ("Data pipe name", "Data pipe type"))

    # Loop over the data pipes.
    for pipe_name in ds:
        print("%-20s%-20s" % (pipe_name, get_type(pipe_name)))


def pipe_loop(name=False):
    """Generator function for looping over and yielding the data pipes.

    @keyword name:  A flag which if True will cause the name of the pipe to be returned.
    @type name:     bool
    @return:        The data pipes, and optionally the pipe names.
    @rtype:         PipeContainer instance or tuple of PipeContainer instance and str if name=True
    """

    # Loop over the keys.
    for key in ds.keys():
        # Return the pipe and name.
        if name:
            yield ds[key], key

        # Return just the pipe.
        else:
            yield ds[key]


def pipe_names():
    """Return the list of all data pipes.

    @return:        The list of data pipes.
    @rtype:         list of str
    """

    return ds.keys()


def switch(pipe_name=None):
    """Switch the current data pipe to the given data pipe.

    @param pipe_name:   The name of the data pipe to switch to.
    @type pipe_name:    str
    """

    # Test if the data pipe exists.
    test(pipe_name)

    # Switch the current data pipe.
    ds.current_pipe = pipe_name


def test(pipe_name=None):
    """Function for testing the existence of the current or supplied data pipe.

    @param pipe_name:   The name of the data pipe to switch to.
    @type pipe_name:    str
    @return:            The answer to the question of whether the pipe exists.
    @rtype:             Boolean
    """

    # No supplied data pipe and no current data pipe.
    if pipe_name == None:
        # Get the current pipe.
        pipe_name = cdp_name()

        # Still no luck.
        if pipe_name == None:
            raise RelaxNoPipeError

    # Test if the data pipe exists.
    if pipe_name not in ds:
        raise RelaxNoPipeError, pipe_name


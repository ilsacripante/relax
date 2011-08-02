###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module containing the class for threaded and non-threaded analysis execution."""

# Python module imports.
import sys
from threading import Thread
from traceback import print_exc
import wx

# relax module imports.
from relax_errors import RelaxImplementError
from status import Status; status = Status()


class Execute(Thread):
    """The analysis execution object."""

    def __init__(self, gui, data, data_index, results_display=True, thread=True):
        """Set up the analysis execution object.

        @param gui:                 The GUI object.
        @type gui:                  wx object
        @param data:                The data container with all data for the analysis.
        @type data:                 class instance
        @param data_index:          The index of the analysis in the relax data store.
        @type data_index:           int
        @keyword results_display:   A flag which if True will cause the results display window to be shown at then end of the execution.
        @type results_display:      bool
        @keyword thread:            The flag for turning threading on and off.
        @type thread:               bool
        """

        # Store the args.
        self.gui = gui
        self.data = data
        self.data_index = data_index
        self.results_display = results_display

        # Threaded execution.
        if thread:
            # Set up the thread object.
            Thread.__init__(self)

        # No treaded execution.
        else:
            # Alias the a few dummy methods.
            self.join = self._join
            self.start = self._start


    def _join(self):
        """Dummy join() method for non-threaded execution."""


    def _start(self):
        """Replacement start() method for when execution is not threaded."""

        # Execute the run() method.
        self.run()


    def run(self):
        """Execute the thread (or pseudo-thread)."""

        # Execute the analysis, catching errors.
        try:
            self.run_analysis()

        # Handle all errors.
        except:
            # Place the analysis index and execution info into the exception queue.
            status.exception_queue.put([self.data_index, sys.exc_info()])

            # Print the exception.
            print("Exception raised in thread.\n")
            print_exc()
            print("\n\n")

            # Unlock the execution lock, if needed.
            if status.exec_lock.locked():
                status.exec_lock.release()

        # Display the results viewer.
        if self.results_display:
            wx.CallAfter(self.gui.analysis.results_viewer.update_window, None)
            wx.CallAfter(self.gui.analysis.show_results_viewer, None)


    def run_analysis(self):
        """Execute the analysis
        
        This method must be overridden.
        """

        raise RelaxImplementError

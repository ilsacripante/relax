###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from generic_fns.thread import RelaxThread

from math import pi
from LinearAlgebra import inverse
from Numeric import Float64, array, matrixmultiply, zeros
from re import match


class Minimise:
    def __init__(self, relax):
        """Class containing the calc, grid_search, minimise, and set functions."""

        self.relax = relax


    def calc(self, run=None, print_flag=1):
        """Function for calculating the function value."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific calculate function setup.
        calculate = self.relax.specific_setup.setup('calculate', function_type)

        # Monte Carlo simulation calculation.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[run]):
                if print_flag:
                    print "Simulation " + `i+1`
                calculate(run=run, print_flag=print_flag-1, sim_index=i)

        # Minimisation.
        else:
            calculate(run=run, print_flag=print_flag)


    def grid_search(self, run=None, lower=None, upper=None, inc=None, constraints=1, print_flag=1):
        """The grid search function."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific grid search function.
        grid_search = self.relax.specific_setup.setup('grid_search', function_type)

        # Monte Carlo simulation grid search.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[run]):
                if print_flag:
                    print "Simulation " + `i+1`
                grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag-1, sim_index=i)

        # Grid search.
        else:
            grid_search(run=run, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=1, scaling=1, print_flag=1):
        """Minimisation function."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific minimisation function.
        minimise = self.relax.specific_setup.setup('minimise', function_type)

        # Monte Carlo simulation minimisation.
        if hasattr(self.relax.data, 'sim_state') and self.relax.data.sim_state[run] == 1:
            # Initialise the job and results queues and finished hosts array.
            job_queue = Queue()
            results_queue = Queue()
            finished_thread = []

            # Fill the job queue.
            for i in xrange(self.relax.data.sim_number[run]):
                job_queue.put(i)

            # Loop over all threads.
            for i in xrange(len(self.relax.data.thread.host_data)):
                # Fill in the finished thread array with zeros.
                finished_thread.append(0)

                # Start thread i.
                RelaxMinimiseThread(self.relax, job_queue, results_queue).start()

            # The main loop.
            terminated = 0
            num_fin = 0
            while not terminated:
                # Get the next results off the results_queue.
                job_index = results_queue.get()
                num_fin = num_fin + 1

                # Test which host job has finished.
                finished_thread[job_index] = 1

                # Print the results.
                print "\n\nThread " + `job_index` + "\n"
                for line in results:
                    print line

                # Add all good hosts to self.relax.data.thread
                if not fail:
                    self.add_host(self.host_data[job_index])

                # All jobs have finished.
                if num_fin == self.relax.data.sim_number[run]:
                    # Add None to the job_queue to signal the threads to finish.
                    job_queue.put(None)

                    # Set the terminate flag to 1 to stop this main loop.
                    terminated = 1

            # Loop over the simulations.
            for i in xrange(self.relax.data.sim_number[run]):
                if print_flag:
                    print "Simulation " + `i+1`
                minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag-1, sim_index=i)

        # Minimisation.
        else:
            minimise(run=run, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, print_flag=print_flag)

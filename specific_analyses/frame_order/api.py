###############################################################################
#                                                                             #
# Copyright (C) 2009-2011,2013-2014,2017 Edward d'Auvergne                    #
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
"""The frame order API object."""

# Python module imports.
from copy import deepcopy
from math import pi
from minfx.grid import grid_split_array
from numpy import float64, zeros
from random import shuffle
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoModelError
from lib.frame_order.variables import MODEL_ISO_CONE_FREE_ROTOR
from lib.warnings import RelaxWarning
from multi import Processor_box
from pipe_control import pipes
from pipe_control.interatomic import interatomic_loop, return_interatom
from pipe_control.mol_res_spin import return_spin, spin_loop
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.frame_order.checks import check_pivot
from specific_analyses.frame_order.data import domain_moving
from specific_analyses.frame_order.optimisation import Frame_order_grid_command, Frame_order_memo, Frame_order_minimise_command, count_sobol_points, grid_row, store_bc_data, target_fn_data_setup
from specific_analyses.frame_order.parameter_object import Frame_order_params
from specific_analyses.frame_order.parameters import assemble_param_vector, linear_constraints, param_num, update_model
from target_functions import frame_order


class Frame_order(API_base, API_common):
    """Class containing the specific methods of the Frame Order theories."""

    # Class variable for storing the class instance (for the singleton design pattern).
    instance = None

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.deselect = self._deselect_global
        self.get_model_container = self._get_model_container_cdp
        self.is_spin_param = self._is_spin_param_false
        self.model_loop = self._model_loop_single_global
        self.model_type = self._model_type_global
        self.print_model_title = self._print_model_title_global
        self.return_conversion_factor = self._return_no_conversion_factor
        self.set_param_values = self._set_param_values_global

        # Place a copy of the parameter list object in the instance namespace.
        self._PARAMS = Frame_order_params()


    def base_data_loop(self):
        """Generator method for looping over the base data - RDCs and PCSs.

        This loop yields the following:

            - The RDC identification data for the interatomic data container and alignment.
            - The PCS identification data for the spin data container and alignment.

        @return:    The base data type ('rdc' or 'pcs'), the spin or interatomic data container information (either one or two spin hashes), and the alignment ID string.
        @rtype:     list of str
        """

        # Loop over the interatomic data containers for the moving domain (for the RDC data).
        for interatom in interatomic_loop(selection1=domain_moving()):
            # Skip deselected containers.
            if not interatom.select:
                continue

            # No RDC, so skip.
            if not hasattr(interatom, 'rdc'):
                continue

            # Loop over the alignment IDs.
            for align_id in cdp.rdc_ids:
                # Yield the info set.
                if align_id in interatom.rdc and interatom.rdc[align_id] != None:
                    yield ['rdc', interatom._spin_hash1, interatom._spin_hash2, align_id]

        # Loop over the spin containers for the moving domain (for the PCS data).
        for spin, spin_id in spin_loop(selection=domain_moving(), return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # No PCS, so skip.
            if not hasattr(spin, 'pcs'):
                continue

            # Loop over the alignment IDs.
            for align_id in cdp.pcs_ids:
                # Yield the info set.
                if align_id in spin.pcs and spin.pcs[align_id] != None:
                    yield ['pcs', spin_id, align_id]


    def calculate(self, spin_id=None, scaling_matrix=None, verbosity=1, sim_index=None):
        """Calculate the chi-squared value for the current parameter values.

        @keyword spin_id:           The spin identification string (unused).
        @type spin_id:              None
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The optional MC simulation index (unused).
        @type sim_index:            None or int
        """

        # Set up the data structures for the target function.
        param_vector, full_tensors, full_in_ref_frame, rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, pcs, pcs_err, pcs_weight, atomic_pos, temp, frq, paramag_centre, com, ave_pos_pivot, pivot, pivot_opt = target_fn_data_setup(sim_index=sim_index, verbosity=verbosity, unset_fail=True)

        # The numeric integration information.
        if not hasattr(cdp, 'quad_int'):
            cdp.quad_int = False
        sobol_max_points, sobol_oversample = None, None
        if hasattr(cdp, 'sobol_max_points'):
            sobol_max_points = cdp.sobol_max_points
            sobol_oversample = cdp.sobol_oversample

        # Set up the optimisation target function class.
        target_fn = frame_order.Frame_order(model=cdp.model, init_params=param_vector, full_tensors=full_tensors, full_in_ref_frame=full_in_ref_frame, rdcs=rdcs, rdc_errors=rdc_err, rdc_weights=rdc_weight, rdc_vect=rdc_vect, dip_const=rdc_const, pcs=pcs, pcs_errors=pcs_err, pcs_weights=pcs_weight, atomic_pos=atomic_pos, temp=temp, frq=frq, paramag_centre=paramag_centre, com=com, ave_pos_pivot=ave_pos_pivot, pivot=pivot, pivot_opt=pivot_opt, sobol_max_points=sobol_max_points, sobol_oversample=sobol_oversample, quad_int=cdp.quad_int)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        chi2 = target_fn.func(param_vector)

        # Set the chi2.
        cdp.chi2 = chi2

        # Store the back-calculated data.
        store_bc_data(A_5D_bc=target_fn.A_5D_bc, pcs_theta=target_fn.pcs_theta, rdc_theta=target_fn.rdc_theta)

        # Feedback on the number of integration points used.
        if not cdp.quad_int:
            count_sobol_points(target_fn=target_fn, verbosity=verbosity)

        # Printout.
        if verbosity:
            print("Chi2:  %s" % chi2)


    def constraint_algorithm(self):
        """Return the 'Log barrier' optimisation constraint algorithm.

        @return:    The 'Log barrier' constraint algorithm.
        @rtype:     str
        """

        # The log barrier algorithm, as required by minfx.
        return 'Log barrier'


    def create_mc_data(self, data_id=None):
        """Create the Monte Carlo data by back calculating the RDCs or PCSs.

        @keyword data_id:   The data set as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Initialise the MC data structure.
        mc_data = []

        # The RDC data.
        if data_id[0] == 'rdc':
            # Unpack the set.
            data_type, spin_hash1, spin_hash2, align_id = data_id

            # Get the interatomic data container.
            interatom = return_interatom(spin_hash1=spin_hash1, spin_hash2=spin_hash2)

            # Does back-calculated data exist?
            if not hasattr(interatom, 'rdc_bc'):
                self.calculate()

            # The data.
            if not hasattr(interatom, 'rdc_bc') or align_id not in interatom.rdc_bc:
                data = None
            else:
                data = interatom.rdc_bc[align_id]

            # Append the data.
            mc_data.append(data)

        # The PCS data.
        elif data_id[0] == 'pcs':
            # Unpack the set.
            data_type, spin_id, align_id = data_id

            # Get the spin container.
            spin = return_spin(spin_id=spin_id)

            # Does back-calculated data exist?
            if not hasattr(spin, 'pcs_bc'):
                self.calculate()

            # The data.
            if not hasattr(spin, 'pcs_bc') or align_id not in spin.pcs_bc:
                data = None
            else:
                data = spin.pcs_bc[align_id]

            # Append the data.
            mc_data.append(data)

        # Return the data.
        return mc_data


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single frame order data pipe.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       Unused.
        @type verbose:          bool
        """

        # Check that the data pipe does not exist.
        if pipes.has_pipe(pipe_to):
            raise RelaxError("The data pipe '%s' already exists." % pipe_to)

        # Create the pipe_to data pipe by copying.
        pipes.copy(pipe_from=pipe_from, pipe_to=pipe_to)


    def eliminate(self, name, value, args, sim=None, model_info=None):
        """Model elimination method.

        @param name:            The parameter name.
        @type name:             str
        @param value:           The parameter value.
        @type value:            float
        @param args:            The elimination constant overrides.
        @type args:             None or tuple of float
        @keyword sim:           The Monte Carlo simulation index.
        @type sim:              int
        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @return:                True if the model is to be eliminated, False otherwise.
        @rtype:                 bool
        """

        # Text to print out if a model failure occurs.
        text = "The %s parameter of %.5g is %s than %.5g, eliminating "
        if sim == None:
            text += "the model."
        else:
            text += "simulation %i." % sim

        # Isotropic cone angle out of range.
        if name == 'cone_theta' and hasattr(cdp, 'cone_theta'):
            if cdp.cone_theta >= pi:
                print(text % ("cone opening angle theta", cdp.cone_theta, "greater", pi))
                return True
            if cdp.cone_theta < 0.0:
                print(text % ("cone opening angle theta", cdp.cone_theta, "less", 0))
                return True

        # Pseudo-ellipse cone angles out of range (0.001 instead of 0.0 because of truncation in the numerical integration).
        if name == 'cone_theta_x' and hasattr(cdp, 'cone_theta_x'):
            if cdp.cone_theta_x >= pi:
                print(text % ("cone opening angle theta x", cdp.cone_theta_x, "greater", pi))
                return True
            if cdp.cone_theta_x < 0.001:
                print(text % ("cone opening angle theta x", cdp.cone_theta_x, "less", 0.001))
                return True
        if name == 'cone_theta_y' and hasattr(cdp, 'cone_theta_y'):
            if cdp.cone_theta_y >= pi:
                print(text % ("cone opening angle theta y", cdp.cone_theta_y, "greater", pi))
                return True
            if cdp.cone_theta_y < 0.001:
                print(text % ("cone opening angle theta y", cdp.cone_theta_y, "less", 0.001))
                return True

        # Torsion angle out of range.
        if name == 'cone_sigma_max' and hasattr(cdp, 'cone_sigma_max'):
            if cdp.cone_sigma_max >= pi:
                print(text % ("torsion angle sigma_max", cdp.cone_sigma_max, "greater", pi))
                return True
            if cdp.cone_sigma_max < 0.0:
                print(text % ("torsion angle sigma_max", cdp.cone_sigma_max, "less", 0.0))
                return True

        # No failure.
        return False


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # First update the model, if needed.
        update_model(verbosity=0)

        # Return the parameter list object.
        return cdp.params


    def get_param_values(self, model_info=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Assemble the values and return it.
        return assemble_param_vector(sim_index=sim_index)


    def grid_search(self, lower=None, upper=None, inc=None, scaling_matrix=None, constraints=False, verbosity=0, sim_index=None):
        """Perform a grid search.

        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:                list of lists of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:                list of lists of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.
        @type inc:                  list of lists of int
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @keyword constraints:       If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:          bool
        @keyword verbosity:         A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The Monte Carlo simulation index.
        @type sim_index:            None or int
        """

        # Test if the Frame Order model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('Frame Order')

        # Test if the pivot has been set.
        check_pivot()

        # The number of parameters.
        n = param_num()

        # Alias the single model grid bounds and increments.
        lower = lower[0]
        upper = upper[0]
        inc = inc[0]

        # Initialise the grid increments structures.
        grid = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension are the grid node positions."""

        # Generate the grid.
        for i in range(n):
            # Fixed parameter.
            if inc[i] == None:
                grid.append(None)
                continue

            # Reset.
            dist_type = None
            end_point = True

            # Arccos grid from 0 to pi.
            if cdp.params[i] in ['ave_pos_beta', 'eigen_beta', 'axis_theta']:
                # Change the default increment numbers.
                if not isinstance(inc, list):
                    inc[i] = int(inc[i] / 2) + 1

                # The distribution type and end point.
                dist_type = 'acos'
                end_point = False

            # Append the grid row.
            row = grid_row(inc[i], lower[i], upper[i], dist_type=dist_type, end_point=end_point)
            grid.append(row)

            # Remove an inc if the end point has been removed.
            if not end_point:
                inc[i] -= 1

        # Total number of points.
        total_pts = 1
        for i in range(n):
            # Fixed parameter.
            if grid[i] == None:
                continue

            total_pts = total_pts * len(grid[i])

        # Check the number.
        max_pts = 50e6
        if total_pts > max_pts:
            raise RelaxError("The total number of grid points '%s' exceeds the maximum of '%s'." % (total_pts, int(max_pts)))

        # Build the points array.
        pts = zeros((total_pts, n), float64)
        indices = zeros(n, int)
        for i in range(total_pts):
            # Loop over the dimensions.
            for j in range(n):
                # Fixed parameter.
                if grid[j] == None:
                    # Get the current parameter value.
                    pts[i, j] = getattr(cdp, cdp.params[j]) / scaling_matrix[0][j, j]

                # Add the point coordinate.
                else:
                    pts[i, j] = grid[j][indices[j]] / scaling_matrix[0][j, j]

            # Increment the step positions.
            for j in range(n):
                if inc[j] != None and indices[j] < inc[j]-1:
                    indices[j] += 1
                    break    # Exit so that the other step numbers are not incremented.
                else:
                    indices[j] = 0

        # Linear constraints.
        A, b = None, None
        if constraints:
            # Obtain the constraints.
            A, b = linear_constraints(scaling_matrix=scaling_matrix[0])

            # Constraint flag set but no constraints present.
            if A is None:
                if verbosity:
                    warn(RelaxWarning("The '%s' model parameters are not constrained, turning the linear constraint algorithm off." % cdp.model))
                constraints = False

        # The numeric integration information.
        if not hasattr(cdp, 'quad_int'):
            cdp.quad_int = False
        sobol_max_points, sobol_oversample = None, None
        if hasattr(cdp, 'sobol_max_points'):
            sobol_max_points = cdp.sobol_max_points
            sobol_oversample = cdp.sobol_oversample

        # Set up the data structures for the target function.
        param_vector, full_tensors, full_in_ref_frame, rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, pcs, pcs_err, pcs_weight, atomic_pos, temp, frq, paramag_centre, com, ave_pos_pivot, pivot, pivot_opt = target_fn_data_setup(sim_index=sim_index, verbosity=verbosity)

        # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
        processor_box = Processor_box() 
        processor = processor_box.processor

        # Set up for multi-processor execution.
        if processor.processor_size() > 1:
            # Printout.
            print("Parallelised grid search.")
            print("Randomising the grid points to equalise the time required for each grid subdivision.\n")

            # Randomise the points.
            shuffle(pts)

        # Loop over each grid subdivision, with all points violating constraints being eliminated.
        for subdivision in grid_split_array(divisions=processor.processor_size(), points=pts, A=A, b=b, verbosity=verbosity):
            # Set up the memo for storage on the master.
            memo = Frame_order_memo(sim_index=sim_index, scaling_matrix=scaling_matrix[0])

            # Set up the command object to send to the slave and execute.
            command = Frame_order_grid_command(points=subdivision, scaling_matrix=scaling_matrix[0], sim_index=sim_index, model=cdp.model, param_vector=param_vector, full_tensors=full_tensors, full_in_ref_frame=full_in_ref_frame, rdcs=rdcs, rdc_err=rdc_err, rdc_weight=rdc_weight, rdc_vect=rdc_vect, rdc_const=rdc_const, pcs=pcs, pcs_err=pcs_err, pcs_weight=pcs_weight, atomic_pos=atomic_pos, temp=temp, frq=frq, paramag_centre=paramag_centre, com=com, ave_pos_pivot=ave_pos_pivot, pivot=pivot, pivot_opt=pivot_opt, sobol_max_points=sobol_max_points, sobol_oversample=sobol_oversample, verbosity=verbosity, quad_int=cdp.quad_int)

            # Add the slave command and memo to the processor queue.
            processor.add_to_queue(command, memo)

        # Execute the queued elements.
        processor.run_queue()


    def map_bounds(self, param, spin_id=None):
        """Create bounds for the OpenDX mapping function.

        @param param:       The name of the parameter to return the lower and upper bounds of.
        @type param:        str
        @param spin_id:     The spin identification string (unused).
        @type spin_id:      None
        @return:            The upper and lower bounds of the parameter.
        @rtype:             list of float
        """

        # Average domain position.
        if param in ['ave_pos_x', 'ave_pos_y', 'ave_pos_z']:
            return [-100.0, 100]
        if param in ['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma']:
            return [0.0, 2*pi]

        # Axis spherical coordinate theta.
        if param == 'axis_theta':
            return [0.0, pi]

        # Axis spherical coordinate phi.
        if param == 'axis_phi':
            return [0.0, 2*pi]

        # Axis alpha angle.
        if param == 'axis_alpha':
            return [0.0, 2*pi]

        # Cone angle.
        if param == 'cone_theta':
            return [0.0, pi]


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling_matrix=None, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Minimisation function.

        @param min_algor:           The minimisation algorithm to use.
        @type min_algor:            str
        @param min_options:         An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @param func_tol:            The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @param grad_tol:            The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @param max_iterations:      The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @param constraints:         If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling_matrix:    The per-model list of diagonal and square scaling matrices.
        @type scaling_matrix:       list of numpy rank-2, float64 array or list of None
        @param verbosity:           A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @param sim_index:           The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The per-model lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                list of lists of numbers
        @keyword upper:             The per-model upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                list of lists of numbers
        @keyword inc:               The per-model increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  list of lists of int
        """

        # Check the optimisation algorithm.
        algor = min_algor
        if min_algor == 'Log barrier':
            algor = min_options[0]
        allowed = ['simplex']
        if algor not in allowed:
            raise RelaxError("Only the 'simplex' minimisation algorithm is supported for the relaxation dispersion analysis as function gradients are not implemented.")

        # Set up the data structures for the target function.
        param_vector, full_tensors, full_in_ref_frame, rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, pcs, pcs_err, pcs_weight, atomic_pos, temp, frq, paramag_centre, com, ave_pos_pivot, pivot, pivot_opt = target_fn_data_setup(sim_index=sim_index, verbosity=verbosity, unset_fail=True)

        # The numeric integration information.
        if not hasattr(cdp, 'quad_int'):
            cdp.quad_int = False
        sobol_max_points, sobol_oversample = None, None
        if hasattr(cdp, 'sobol_max_points'):
            sobol_max_points = cdp.sobol_max_points
            sobol_oversample = cdp.sobol_oversample

        # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
        processor_box = Processor_box() 
        processor = processor_box.processor

        # Set up the memo for storage on the master.
        memo = Frame_order_memo(sim_index=sim_index, scaling_matrix=scaling_matrix[0])

        # Set up the command object to send to the slave and execute.
        command = Frame_order_minimise_command(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, scaling_matrix=scaling_matrix[0], constraints=constraints, sim_index=sim_index, model=cdp.model, param_vector=param_vector, full_tensors=full_tensors, full_in_ref_frame=full_in_ref_frame, rdcs=rdcs, rdc_err=rdc_err, rdc_weight=rdc_weight, rdc_vect=rdc_vect, rdc_const=rdc_const, pcs=pcs, pcs_err=pcs_err, pcs_weight=pcs_weight, atomic_pos=atomic_pos, temp=temp, frq=frq, paramag_centre=paramag_centre, com=com, ave_pos_pivot=ave_pos_pivot, pivot=pivot, pivot_opt=pivot_opt, sobol_max_points=sobol_max_points, sobol_oversample=sobol_oversample, verbosity=verbosity, quad_int=cdp.quad_int)

        # Add the slave command and memo to the processor queue.
        processor.add_to_queue(command, memo)


    def model_desc(self, model_info=None):
        """Return a description of the model.

        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @return:                The model description.
        @rtype:                 str
        """

        return ""


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @keyword spin_id:       Unused.
        @type spin_id:          None
        @keyword global_stats:  Unused.
        @type global_stats:     None
        @return:                The optimisation statistics, in tuple format, of the number of parameters (k), the number of data points (n), and the chi-squared value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Count the number of parameters.
        k = len(cdp.params)

        # The number of data points (RDCs + PCSs).
        n = 0
        for data in self.base_data_loop():
            n += 1

        # Check for the chi2 value.
        if not hasattr(cdp, 'chi2'):
            raise RelaxError("Statistics are not available, most likely because the model has not been optimised.")

        # Return the data.
        return k, n, cdp.chi2


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Nothing to do.
        if not data_check:
            return

        # Loop over spin data, checking for PCS data.
        ids = []
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            if not hasattr(spin, 'pcs'):
                spin.select = False
                ids.append(spin_id)
        if verbose and len(ids):
            warn(RelaxWarning("No PCS data is present, deselecting the spins %s." % ids))

        # Loop over the interatomic data containers, checking for RDC data.
        ids = []
        for interatom in interatomic_loop(selection1=domain_moving()):
            if not hasattr(interatom, 'rdc'):
                interatom.select = False
                ids.append("%s - %s" % (interatom.spin_id1, interatom.spin_id2))
        if verbose and len(ids):
            warn(RelaxWarning("No RDC data is present, deselecting the interatomic data containers between spin pairs %s." % ids))


    def return_error(self, data_id):
        """Return the RDC or PCS error structure.

        @param data_id:     The data set as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @return:            The array of RDC or PCS error values.
        @rtype:             list of float
        """

        # Initialise the MC data structure.
        mc_errors = []

        # The RDC data.
        if data_id[0] == 'rdc':
            # Unpack the set.
            data_type, spin_hash1, spin_hash2, align_id = data_id

            # Get the interatomic data container.
            interatom = return_interatom(spin_hash1=spin_hash1, spin_hash2=spin_hash2)

            # Do errors exist?
            if not hasattr(interatom, 'rdc_err'):
                raise RelaxError("The RDC errors are missing for interatomic data container between spins '%s' and '%s'." % (spin_id1, spin_id2))

            # Handle missing data.
            if align_id not in interatom.rdc_err:
                mc_errors.append(None)

            # Append the data.
            else:
                mc_errors.append(interatom.rdc_err[align_id])

        # The PCS data.
        elif data_id[0] == 'pcs':
            # Unpack the set.
            data_type, spin_id, align_id = data_id

            # Get the spin container.
            spin = return_spin(spin_id=spin_id)

            # Do errors exist?
            if not hasattr(spin, 'pcs_err'):
                raise RelaxError("The PCS errors are missing for spin '%s'." % spin_id)

            # Handle missing data.
            if align_id not in spin.pcs_err:
                mc_errors.append(None)

            # Append the data.
            else:
                mc_errors.append(spin.pcs_err[align_id])

        # Return the errors.
        return mc_errors


    def set_error(self, index, error, model_info=None):
        """Set the parameter errors.

        @param index:           The index of the parameter to set the errors for.
        @type index:            int
        @param error:           The error value.
        @type error:            float
        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        """

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Not a parameter of the model.
            if param not in cdp.params:
                continue

            # Return the parameter array.
            if index == inc:
                setattr(cdp, param + "_err", error)

            # Increment.
            inc = inc + 1

        # Add some additional parameters.
        if cdp.model == MODEL_ISO_CONE_FREE_ROTOR and inc == index:
            setattr(cdp, 'cone_theta_err', error)


    def set_selected_sim(self, select_sim, model_info=None):
        """Set the simulation selection flag for the spin.

        @param select_sim:      The selection flag for the simulations.
        @type select_sim:       bool
        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        """

        # Set the array.
        cdp.select_sim = deepcopy(select_sim)


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # The model parameters.
        model_params = deepcopy(cdp.params)

        # Add some additional parameters.
        if cdp.model == MODEL_ISO_CONE_FREE_ROTOR:
            param_names.append('cone_theta')
            model_params.append('cone_theta')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')

        # Loop over all the data names.
        for object_name in param_names:
            # Not a parameter of the model.
            if object_name not in model_params:
                continue

            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(cdp, sim_object_name, [])

            # Get the simulation object.
            sim_object = getattr(cdp, sim_object_name)

            # Loop over the simulations.
            for j in range(cdp.sim_number):
                # Copy and append the data.
                sim_object.append(deepcopy(getattr(cdp, object_name)))

        # Loop over all the minimisation object names.
        for object_name in min_names:
            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(cdp, sim_object_name, [])

            # Get the normal and simulation object.
            object = None
            if hasattr(cdp, object_name):
                object = getattr(cdp, object_name)
            sim_object = getattr(cdp, sim_object_name)

            # Loop over the simulations.
            for j in range(cdp.sim_number):
                # Copy and append the data.
                sim_object.append(deepcopy(object))


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param data_id:     The data set as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # The RDC data.
        if data_id[0] == 'rdc':
            # Unpack the set.
            data_type, spin_hash1, spin_hash2, align_id = data_id

            # Get the interatomic data container.
            interatom = return_interatom(spin_hash1=spin_hash1, spin_hash2=spin_hash2)

            # Initialise.
            if not hasattr(interatom, 'rdc_sim'):
                interatom.rdc_sim = {}
                    
            # Store the data structure.
            interatom.rdc_sim[align_id] = []
            for i in range(cdp.sim_number):
                interatom.rdc_sim[align_id].append(sim_data[i][0])

        # The PCS data.
        elif data_id[0] == 'pcs':
            # Unpack the set.
            data_type, spin_id, align_id = data_id

            # Get the spin container.
            spin = return_spin(spin_id=spin_id)

            # Initialise.
            if not hasattr(spin, 'pcs_sim'):
                spin.pcs_sim = {}
                
            # Store the data structure.
            spin.pcs_sim[data_id[2]] = []
            for i in range(cdp.sim_number):
                spin.pcs_sim[data_id[2]].append(sim_data[i][0])


    def sim_return_param(self, index, model_info=None):
        """Return the array of simulation parameter values.

        @param index:           The index of the parameter to return the array of values for.
        @type index:            int
        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @return:                The array of simulation parameter values.
        @rtype:                 list of float
        """

        # Parameter increment counter.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Loop over the parameters.
        for param in param_names:
            # Not a parameter of the model.
            if param not in cdp.params:
                continue

            # Return the parameter array.
            if index == inc:
                return getattr(cdp, param + "_sim")

            # Increment.
            inc = inc + 1

        # Add some additional parameters.
        if cdp.model == MODEL_ISO_CONE_FREE_ROTOR and inc == index:
            return getattr(cdp, 'cone_theta_sim')


    def sim_return_selected(self, model_info=None):
        """Return the array of selected simulation flags for the spin.

        @keyword model_info:    The model information from model_loop().  This is unused.
        @type model_info:       None
        @return:                The array of selected simulation flags.
        @rtype:                 list of int
        """

        # Return the array.
        return cdp.select_sim

###############################################################################
#                                                                             #
# Copyright (C) 2009-2011,2013-2014 Edward d'Auvergne                         #
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
"""Module for handling the geometric representation of the frame order motions."""

# Python module imports.
from copy import deepcopy
from math import pi
from numpy import cross, dot, eye, float64, zeros
from numpy.linalg import norm
import sys
from warnings import warn

# relax module imports.
from lib.errors import RelaxFault
from lib.frame_order.conversions import create_rotor_axis_alpha, create_rotor_axis_spherical
from lib.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_LIST_DOUBLE, MODEL_LIST_FREE_ROTORS, MODEL_LIST_ISO_CONE, MODEL_LIST_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_ROTOR
from lib.geometry.rotations import euler_to_R_zyz
from lib.io import open_write_file
from lib.structure.cones import Iso_cone, Pseudo_elliptic
from lib.structure.geometric import generate_vector_residues
from lib.structure.internal.object import Internal
from lib.structure.represent.cone import cone
from lib.structure.represent.rotor import rotor
from lib.text.sectioning import subsection, subsubsection
from lib.warnings import RelaxWarning
from pipe_control.structure.mass import pipe_centre_of_mass
from specific_analyses.frame_order.checks import check_parameters
from specific_analyses.frame_order.data import domain_moving, generate_pivot


def add_axes(structure=None, representation=None, size=None, sims=False):
    """Add the axis system for the current frame order model to the structural object.

    @keyword structure:         The internal structural object to add the rotor objects to.
    @type structure:            lib.structure.internal.object.Internal instance
    @keyword representation:    The representation to create.  If this is set to None or 'A', the standard representation will be created.  If set to 'B', the axis system will be inverted.
    @type representation:       None or str
    @keyword size:              The size of the geometric object in Angstroms.
    @type size:                 float
    @keyword sims:              A flag which if True will add the Monte Carlo simulation rotors to the structural object.  There must be one model for each Monte Carlo simulation already present in the structural object.
    @type sims:                 bool
    """

    # Create the molecule.
    mol_name = 'axes'
    structure.add_molecule(name=mol_name)

    # The transformation matrix (identity matrix or inversion matrix).
    if representation == 'B':
        T = -eye(3)
    else:
        T = eye(3)

    # The models to loop over.
    model_nums = [None]
    sim_indices = [None]
    if sims:
        model_nums = [i+1 for i in range(cdp.sim_number)]
        sim_indices = list(range(cdp.sim_number))

    # Loop over the models.
    for i in range(len(model_nums)):
        # Alias the molecule.
        mol = structure.get_molecule(mol_name, model=model_nums[i])

        # The pivot points.
        pivot1 = generate_pivot(order=1, sim_index=sim_indices[i], pdb_limit=True)
        pivot2 = generate_pivot(order=2, sim_index=sim_indices[i], pdb_limit=True)

        # A single z-axis, when no rotor object is present.
        if cdp.model in [MODEL_ISO_CONE_TORSIONLESS]:
            # Print out.
            print("\nGenerating the z-axis system.")

            # The axis.
            if sims:
                axis = create_rotor_axis_spherical(theta=cdp.axis_theta_sim[sim_indices[i]], phi=cdp.axis_phi_sim[sim_indices[i]])
            else:
                axis = create_rotor_axis_spherical(theta=cdp.axis_theta, phi=cdp.axis_phi)
            print(("Central axis: %s." % axis))

            # Transform the central axis.
            axis = dot(T, axis)

            # Generate the axis vectors.
            print("\nGenerating the axis vectors.")
            res_num = generate_vector_residues(mol=mol, vector=axis, atom_name='z-ax', res_name_vect='AXE', res_num=2, origin=pivot1, scale=size)

        # The z-axis connecting two motional modes.
        elif cdp.model in [MODEL_DOUBLE_ROTOR]:
            # Printout.
            print("\nGenerating the z-axis linking the two pivot points.")

            # The axis.
            axis = pivot1 - pivot2
            print(("Interconnecting axis: %s." % axis))

            # Generate the axis vectors.
            print("\nGenerating the axis vectors.")
            res_num = generate_vector_residues(mol=mol, vector=axis, atom_name='z-ax', res_name_vect='AXE', res_num=1, origin=pivot2)

        # The full axis system.
        elif cdp.model in MODEL_LIST_PSEUDO_ELLIPSE:
            # Print out.
            print("\nGenerating the full axis system.")

            # Add the pivot point.
            mol.atom_add(atom_num=1, atom_name='R', res_name='AXE', res_num=1, pos=pivot1, element='C', pdb_record='HETATM')

            # The axis system.
            axes = generate_axis_system(sim_index=sim_indices[i])

            # Rotations and inversions.
            axes = dot(T, axes)

            # The axes to create.
            label = ['x', 'y']
            if cdp.model in [MODEL_PSEUDO_ELLIPSE_TORSIONLESS]:
                label = ['x', 'y', 'z']

            # Generate the axis vectors.
            print("\nGenerating the axis vectors.")
            for j in range(len(label)):
                res_num = generate_vector_residues(mol=mol, vector=axes[:, j], atom_name='%s-ax'%label[j], res_name_vect='AXE', res_num=2, origin=pivot1, scale=size)


def add_cones(structure=None, representation=None, size=None, inc=None, sims=False):
    """Add the cone geometric object for the current frame order model to the structural object.

    @keyword structure:         The internal structural object to add the rotor objects to.
    @type structure:            lib.structure.internal.object.Internal instance
    @keyword representation:    The representation to create.  If this is set to None or 'A', the standard representation will be created.  If set to 'B', the axis system will be inverted.
    @type representation:       str
    @keyword size:              The size of the geometric object in Angstroms.
    @type size:                 float
    @keyword inc:               The number of increments for the filling of the cone objects.
    @type inc:                  int
    @keyword sims:      A flag which if True will add the Monte Carlo simulation pivots to the structural object.  There must be one model for each Monte Carlo simulation already present in the structural object.
    @type sims:         bool
    """

    # Create the molecule.
    structure.add_molecule(name='cones')

    # The transformation matrix (identity matrix or inversion matrix).
    if representation == 'B':
        T = -eye(3)
    else:
        T = eye(3)

    # The models to loop over.
    model_nums = [None]
    sim_indices = [None]
    if sims:
        model_nums = [i+1 for i in range(cdp.sim_number)]
        sim_indices = list(range(cdp.sim_number))

    # Loop over the models.
    for i in range(len(model_nums)):
        # Alias the molecule.
        mol = structure.get_molecule('cones', model=model_nums[i])

        # The 1st pivot point.
        pivot = generate_pivot(order=1, sim_index=sim_indices[i], pdb_limit=True)

        # The rotation matrix (rotation from the z-axis to the cone axis).
        R = generate_axis_system(sim_index=sim_indices[i])
        print(("Rotation matrix:\n%s" % R))

        # The transformation.
        R = dot(T, R)

        # The pseudo-ellipse cone object.
        if cdp.model in MODEL_LIST_PSEUDO_ELLIPSE:
            if sims:
                cone_obj = Pseudo_elliptic(cdp.cone_theta_x_sim[sim_indices[i]], cdp.cone_theta_y_sim[sim_indices[i]])
            else:
                cone_obj = Pseudo_elliptic(cdp.cone_theta_x, cdp.cone_theta_y)

        # The isotropic cone object.
        else:
            # The angle.
            if hasattr(cdp, 'cone_theta'):
                if sims:
                    cone_theta = cdp.cone_theta_sim[sim_indices[i]]
                else:
                    cone_theta = cdp.cone_theta

            # The object.
            cone_obj = Iso_cone(cone_theta)

        # Create the cone.
        cone(mol=mol, cone_obj=cone_obj, start_res=1, apex=pivot, R=R, inc=inc, scale=size, distribution='regular', axis_flag=False)


def add_pivots(structure=None, sims=False):
    """Add the pivots for the current frame order model to the structural object.

    @keyword structure: The internal structural object to add the rotor objects to.
    @type structure:    lib.structure.internal.object.Internal instance
    @keyword sims:      A flag which if True will add the Monte Carlo simulation pivots to the structural object.  There must be one model for each Monte Carlo simulation already present in the structural object.
    @type sims:         bool
    """

    # Initialise.
    pivots = []
    mols = []
    atom_names = []
    atom_nums = []

    # Create the molecule.
    mol_name = 'pivots'
    structure.add_molecule(name=mol_name)

    # The models to loop over.
    model_nums = [None]
    sim_indices = [None]
    if sims:
        model_nums = [i+1 for i in range(cdp.sim_number)]
        sim_indices = list(range(cdp.sim_number))

    # Loop over the models.
    for i in range(len(model_nums)):
        # Alias the molecule.
        mol = structure.get_molecule(mol_name, model=model_nums[i])

        # The pivot points.
        pivot1 = generate_pivot(order=1, sim_index=sim_indices[i], pdb_limit=True)
        pivot2 = generate_pivot(order=2, sim_index=sim_indices[i], pdb_limit=True)

        # Add the pivots for the double motion models.
        if cdp.model in [MODEL_DOUBLE_ROTOR]:
            # The 1st pivot.
            mols.append(mol)
            pivots.append(pivot1)
            atom_names.append('Piv1')
            atom_nums.append(1)

            # The 2nd pivot.
            mols.append(mol)
            pivots.append(pivot2)
            atom_names.append('Piv2')
            atom_nums.append(2)

        # Add the pivot for the single motion models.
        else:
            mols.append(mol)
            pivots.append(pivot1)
            atom_names.append('Piv')
            atom_nums.append(1)

    # Loop over the data, adding all pivots.
    for i in range(len(mols)):
        mols[i].atom_add(atom_num=atom_nums[i], atom_name=atom_names[i], res_name='PIV', res_num=1, pos=pivots[i], element='C', pdb_record='HETATM')


def add_titles(structure=None, representation=None, displacement=40.0, sims=False):
    """Add atoms to be used for the titles for the frame order geometric objects.

    @keyword structure:         The internal structural object to add the rotor objects to.
    @type structure:            lib.structure.internal.object.Internal instance
    @keyword representation:    The representation to title.
    @type representation:       None or str
    @keyword displacement:      The distance away from the pivot point, in Angstrom, to place the title.  The simulation title will be shifted by a few extra Angstrom to avoid clashes.
    @type displacement:         float
    @keyword sims:              A flag which if True will add the Monte Carlo simulation pivots to the structural object.  There must be one model for each Monte Carlo simulation already present in the structural object.
    @type sims:                 bool
    """

    # The title atom names.
    atom_name = None
    if representation == None and sims:
        atom_name = 'mc'
    elif representation == 'A':
        if sims:
            atom_name = 'mc-a'
        else:
            atom_name = 'a'
    elif representation == 'B':
        if sims:
            atom_name = 'mc-b'
        else:
            atom_name = 'b'

    # Nothing to do.
    if atom_name == None:
        return

    # Avoid name overlaps.
    if sims:
        displacement += 3

    # Create the molecule.
    mol_name = 'titles'
    structure.add_molecule(name=mol_name)

    # The transformation matrix (identity matrix or inversion matrix).
    if representation == 'B':
        T = -eye(3)
    else:
        T = eye(3)

    # The pivot points.
    pivot1 = generate_pivot(order=1, pdb_limit=True)
    pivot2 = generate_pivot(order=2, pdb_limit=True)

    # The models to loop over.
    model_nums = [None]
    sim_indices = [None]
    if sims:
        model_nums = [i+1 for i in range(cdp.sim_number)]
        sim_indices = list(range(cdp.sim_number))

    # Loop over the models.
    for i in range(len(model_nums)):
        # Alias the molecule.
        mol = structure.get_molecule(mol_name, model=model_nums[i])

        # The axis system.
        axes = generate_axis_system(sim_index=sim_indices[i])

        # Transform the central axis.
        axis = dot(T, axes[:, 2])

        # The label position.
        pos = pivot1 + displacement*axis

        # Add the atom.
        mol.atom_add(atom_name=atom_name, res_name='TLE', res_num=1, pos=pos, element='Ti', pdb_record='HETATM')


def add_rotors(structure=None, representation=None, size=None, sims=False):
    """Add all rotor objects for the current frame order model to the structural object.

    @keyword structure:         The internal structural object to add the rotor objects to.
    @type structure:            lib.structure.internal.object.Internal instance
    @keyword representation:    The representation to create.  If this is set to None, the rotor will be dumbbell shaped with propellers at both ends.  If set to 'A' or 'B', only half of the rotor will be shown.
    @type representation:       None or str
    @keyword size:              The size of the geometric object in Angstroms.
    @type size:                 float
    @keyword sims:              A flag which if True will add the Monte Carlo simulation rotors to the structural object.  There must be one model for each Monte Carlo simulation already present in the structural object.
    @type sims:                 bool
    """

    # Initialise the list structures for the rotor data.
    axis = []
    span = []
    staggered = []
    pivot = []
    rotor_angle = []
    com = []
    label = []
    models = []

    # The half-rotor flag.
    half_rotor = True
    if representation == None:
        half_rotor = False

    # The transformation matrix (identity matrix or inversion matrix).
    if representation == 'B':
        T = -eye(3)
    else:
        T = eye(3)

    # The models to loop over.
    model_nums = [None]
    sim_indices = [None]
    if sims:
        model_nums = [i+1 for i in range(cdp.sim_number)]
        sim_indices = list(range(cdp.sim_number))

    # Loop over the models.
    for i in range(len(model_nums)):
        # The pivot points.
        pivot1 = generate_pivot(order=1, sim_index=sim_indices[i], pdb_limit=True)
        pivot2 = generate_pivot(order=2, sim_index=sim_indices[i], pdb_limit=True)

        # The single rotor models.
        if cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]:
            # The rotor angle.
            if cdp.model in MODEL_LIST_FREE_ROTORS:
                rotor_angle.append(pi)
            else:
                if sims:
                    rotor_angle.append(cdp.cone_sigma_max_sim[sim_indices[i]])
                else:
                    rotor_angle.append(cdp.cone_sigma_max)

            # Get the CoM of the entire molecule to use as the centre of the rotor.
            if cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR]:
                com.append(pipe_centre_of_mass(verbosity=0, missing_error=False))
            else:
                com.append(pivot1)

            # Generate the rotor axis.
            axes = generate_axis_system(sim_index=sim_indices[i])
            axis.append(axes[:, 2])

            # The size of the rotor (Angstrom), taking the cone representation into account by adding 5 Angstrom.
            if cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR]:
                span.append(size)
            else:
                span.append(size + 5.0)

            # Stagger the propeller blades.
            if cdp.model in MODEL_LIST_FREE_ROTORS:
                staggered.append(False)
            else:
                staggered.append(True)

            # The pivot.
            pivot.append(pivot1)

            # The label.
            label.append('z-ax')

            # The models.
            if sims:
                models.append(model_nums[i])
            else:
                models.append(None)

        # The double rotor models.
        elif cdp.model in [MODEL_DOUBLE_ROTOR]:
            # Add both rotor angles (the 2nd must come first).
            if sims:
                rotor_angle.append(cdp.cone_sigma_max_2_sim[sim_indices[i]])
                rotor_angle.append(cdp.cone_sigma_max_sim[sim_indices[i]])
            else:
                rotor_angle.append(cdp.cone_sigma_max_2)
                rotor_angle.append(cdp.cone_sigma_max)

            # Set the com to the pivot points.
            com.append(pivot2)
            com.append(pivot1)

            # Generate the eigenframe of the motion.
            frame = generate_axis_system(sim_index=sim_indices[i])

            # Add the x and y axes.
            axis.append(frame[:, 0])
            axis.append(frame[:, 1])

            # The rotor size (Angstrom).
            span.append(size)
            span.append(size)

            # Stagger the propeller blades.
            staggered.append(True)
            staggered.append(True)

            # The pivot points.
            pivot.append(pivot2)
            pivot.append(pivot1)

            # The labels.
            label.append('x-ax')
            label.append('y-ax')

            # The models.
            if sims:
                models.append(model_nums[i])
                models.append(model_nums[i])
            else:
                models.append(None)
                models.append(None)

    # Add each rotor to the structure as a new molecule.
    for i in range(len(axis)):
        rotor(structure=structure, rotor_angle=rotor_angle[i], axis=dot(T, axis[i]), axis_pt=pivot[i], label=label[i], centre=com[i], span=span[i]/1e10, blade_length=5e-10, model_num=models[i], staggered=staggered[i], half_rotor=half_rotor)


def average_position(structure=None, models=None, sim=None):
    """Shift the given structural object to the average position.

    @keyword structure: The structural object to operate on.
    @type structure:    lib.structure.internal.object.Internal instance
    @keyword models:    The list of models to shift.
    @type models:       list of int
    @keyword sim:       A flag which if True will use the Monte Carlo simulation results.  In this case, the model list should be set to the simulation indices plus 1 and the structural object should have one model per simulation already set up.
    @type sim:          bool
    """

    # The selection object.
    selection = structure.selection(atom_id=domain_moving())

    # Loop over each model.
    for i in range(len(models)):
        # First rotate the moving domain to the average position.
        R = zeros((3, 3), float64)
        if hasattr(cdp, 'ave_pos_alpha'):
            if sim:
                euler_to_R_zyz(cdp.ave_pos_alpha_sim[i], cdp.ave_pos_beta_sim[i], cdp.ave_pos_gamma_sim[i], R)
            else:
                euler_to_R_zyz(cdp.ave_pos_alpha, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        else:
            if sim:
                euler_to_R_zyz(0.0, cdp.ave_pos_beta_sim[i], cdp.ave_pos_gamma_sim[i], R)
            else:
                euler_to_R_zyz(0.0, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        origin = pipe_centre_of_mass(atom_id=domain_moving(), verbosity=0, missing_error=False)
        structure.rotate(R=R, origin=origin, model=models[i], selection=selection)

        # Then translate the moving domain.
        if sim:
            T = [cdp.ave_pos_x_sim[i], cdp.ave_pos_y_sim[i], cdp.ave_pos_z_sim[i]]
        else:
            T = [cdp.ave_pos_x, cdp.ave_pos_y, cdp.ave_pos_z]
        structure.translate(T=T, model=models[i], selection=selection)


def create_ave_pos(format='PDB', file=None, dir=None, compress_type=0, model=1, force=False):
    """Create a PDB file of the molecule with the moving domains shifted to the average position.

    @keyword format:        The format for outputting the geometric representation.  Currently only the 'PDB' format is supported.
    @type format:           str
    @keyword file:          The name of the file for the average molecule structure.
    @type file:             str
    @keyword dir:           The name of the directory to place the PDB file into.
    @type dir:              str
    @keyword compress_type: The compression type.  The integer values correspond to the compression type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @keyword model:         Only one model from an analysed ensemble can be used for the PDB representation of the Monte Carlo simulations, as these consists of one model per simulation.
    @type model:            int
    @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:            bool
    """

    # Printout.
    subsection(file=sys.stdout, text="Creating a PDB file with the moving domains shifted to the average position.")

    # Checks.
    if not hasattr(cdp, 'structure'):
        warn(RelaxWarning("No structural data is present, cannot create the average position representation."))
        return

    # Initialise.
    titles = []
    sims = []
    file_root = []
    models = []
    structures = []

    # The real average position.
    titles.append("real average position")
    sims.append(False)
    file_root.append(file)
    models.append([None])

    # The positive MC simulation representation.
    if hasattr(cdp, 'sim_number'):
        titles.append("MC simulation representation")
        sims.append(True)
        file_root.append("%s_sim" % file)
        models.append([i+1 for i in range(cdp.sim_number)])

    # Make a copy of the structural object (so as to preserve the original structure).
    structures.append(deepcopy(cdp.structure))
    if hasattr(cdp, 'sim_number'):
        structures.append(deepcopy(cdp.structure))

    # Delete all but the chosen model for the simulations.
    if hasattr(cdp, 'sim_number') and len(structures[-1].structural_data) > 1:
        # Determine the models to delete.
        to_delete = []
        for model_cont in structures[-1].model_loop():
            if model_cont.num != model:
                to_delete.append(model_cont.num)
        to_delete.reverse()

        # Delete them.
        for num in to_delete:
            structures[-1].structural_data.delete_model(model_num=num)

    # Loop over each representation and add the contents.
    for i in range(len(titles)):
        # Printout.
        subsubsection(file=sys.stdout, text="Creating the %s." % titles[i])

        # Loop over each model.
        for j in range(len(models[i])):
            # Create or set the models, if needed.
            if models[i][j] == 1:
                structures[i].set_model(model_new=1)
            elif models[i][j] != None:
                structures[i].add_model(model=models[i][j])

        # Shift to the average position.
        average_position(structure=structures[i], models=models[i], sim=sims[i])

        # Output to PDB format.
        if format == 'PDB':
            pdb_file = open_write_file(file_name=file_root[i]+'.pdb', dir=dir, compress_type=compress_type, force=force)
            structures[i].write_pdb(file=pdb_file)
            pdb_file.close()


def create_geometric_rep(format='PDB', file=None, dir=None, compress_type=0, size=30.0, inc=36, force=False):
    """Create a PDB file containing a geometric object representing the frame order dynamics.

    @keyword format:        The format for outputting the geometric representation.  Currently only the 'PDB' format is supported.
    @type format:           str
    @keyword file:          The name of the file of the PDB representation of the frame order dynamics to create.
    @type file:             str
    @keyword dir:           The name of the directory to place the PDB file into.
    @type dir:              str
    @keyword compress_type: The compression type.  The integer values correspond to the compression type: 0, no compression; 1, Bzip2 compression; 2, Gzip compression.
    @type compress_type:    int
    @keyword size:          The size of the geometric object in Angstroms.
    @type size:             float
    @keyword inc:           The number of increments for the filling of the cone objects.
    @type inc:              int
    @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:            bool
    """

    # Printout.
    subsection(file=sys.stdout, text="Creating a PDB file containing a geometric object representing the frame order dynamics.")

    # Checks.
    check_parameters(escalate=2)

    # Initialise.
    titles = []
    structures = []
    representation = []
    sims = []
    file_root = []

    # Symmetry for inverted representations?
    sym = True
    if cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR, MODEL_DOUBLE_ROTOR]:
        sym = False

    # The standard representation.
    titles.append("Representation A")
    structures.append(Internal())
    if sym:
        representation.append('A')
        file_root.append("%s_A" % file)
    else:
        representation.append(None)
        file_root.append(file)
    sims.append(False)

    # The inverted representation.
    if sym:
        titles.append("Representation A")
        structures.append(Internal())
        representation.append('B')
        file_root.append("%s_B" % file)
        sims.append(False)

    # The standard MC simulation representation.
    if hasattr(cdp, 'sim_number'):
        titles.append("MC simulation representation A")
        structures.append(Internal())
        if sym:
            representation.append('A')
            file_root.append("%s_sim_A" % file)
        else:
            representation.append(None)
            file_root.append("%s_sim" % file)
        sims.append(True)

    # The inverted MC simulation representation.
    if hasattr(cdp, 'sim_number') and sym:
        titles.append("MC simulation representation B")
        structures.append(Internal())
        representation.append('B')
        file_root.append("%s_sim_B" % file)
        sims.append(True)

    # Loop over each structure and add the contents.
    for i in range(len(structures)):
        # Printout.
        subsubsection(file=sys.stdout, text="Creating the %s." % titles[i])

        # Create a model for each Monte Carlo simulation.
        if sims[i]:
            for sim_i in range(cdp.sim_number):
                structures[i].add_model(model=sim_i+1)

        # Add the pivots.
        add_pivots(structure=structures[i], sims=sims[i])

        # Add all rotor objects.
        add_rotors(structure=structures[i], representation=representation[i], size=size, sims=sims[i])

        # Add the axis systems.
        add_axes(structure=structures[i], representation=representation[i], size=size, sims=sims[i])

        # Add the cone objects.
        if cdp.model not in [MODEL_ROTOR, MODEL_FREE_ROTOR, MODEL_DOUBLE_ROTOR]:
            add_cones(structure=structures[i], representation=representation[i], size=size, inc=inc, sims=sims[i])

        # Add atoms for creating titles.
        add_titles(structure=structures[i], representation=representation[i], displacement=size+10, sims=sims[i])

        # Create the PDB file.
        if format == 'PDB':
            pdb_file = open_write_file(file_root[i]+'.pdb', dir, compress_type=compress_type, force=force)
            structures[i].write_pdb(pdb_file)
            pdb_file.close()


def frame_from_axis(axis, frame):
    """Build a full 3D frame from the single axis.

    @param axis:    The Z-axis of the system.
    @type axis:     numpy rank-1, 3D array
    @param frame:   The empty frame to populate.
    @type frame:    numpy rank-2, 3D array
    """

    # Store the Z-axis.
    frame[:, 2] = axis

    # The temporary eigenframe X-axis.
    frame[0, 0] = 1.0

    # The Y-axis (orthonormal to Z and X).
    frame[:, 1] = cross(frame[:, 2], frame[:, 0])
    frame[:, 1] /= norm(frame[:, 1])

    # The orthonormal X-axis.
    frame[:, 0] = cross(frame[:, 1], frame[:, 2])
    frame[:, 0] /= norm(frame[:, 0])


def generate_axis_system(sim_index=None):
    """Generate and return the full 3D axis system for the current frame order model.

    @keyword sim_index: The optional MC simulation index to obtain the frame for a given simulation.
    @type sim_index:    None or int
    @return:            The full 3D axis system for the model.
    @rtype:             numpy rank-2, 3D float64 array
    """

    # Initialise.
    axis = zeros(3, float64)
    frame = zeros((3, 3), float64)

    # The 1st pivot point.
    pivot = generate_pivot(order=1, sim_index=sim_index, pdb_limit=True)

    # The CoM of the system.
    com = pipe_centre_of_mass(verbosity=0, missing_error=False)

    # The system for the rotor models.
    if cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR]:
        # Generate the axis.
        if sim_index == None:
            axis = create_rotor_axis_alpha(alpha=cdp.axis_alpha, pivot=pivot, point=com)
        else:
            axis = create_rotor_axis_alpha(alpha=cdp.axis_alpha_sim[sim_index], pivot=pivot, point=com)

        # Create a full normalised axis system.
        frame_from_axis(axis, frame)

    # The system for the isotropic cones.
    elif cdp.model in MODEL_LIST_ISO_CONE:
        # Generate the axis.
        if sim_index == None:
            axis = create_rotor_axis_spherical(theta=cdp.axis_theta, phi=cdp.axis_phi)
        else:
            axis = create_rotor_axis_spherical(theta=cdp.axis_theta_sim[sim_index], phi=cdp.axis_phi_sim[sim_index])

        # Create a full normalised axis system.
        frame_from_axis(axis, frame)

    # The system for the pseudo-ellipses and double rotor.
    elif cdp.model in MODEL_LIST_PSEUDO_ELLIPSE + MODEL_LIST_DOUBLE:
        # Generate the eigenframe of the motion.
        if sim_index == None:
            euler_to_R_zyz(cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma, frame)
        else:
            euler_to_R_zyz(cdp.eigen_alpha_sim[sim_index], cdp.eigen_beta_sim[sim_index], cdp.eigen_gamma_sim[sim_index], frame)

    # Unknown model.
    else:
        raise RelaxFault

    # Return the full eigenframe.
    return frame

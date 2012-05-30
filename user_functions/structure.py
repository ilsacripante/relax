###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""The structure user function definitions."""

# Python module imports.
from numpy import eye
from os import sep
import wx

# relax module imports.
import generic_fns.structure.geometric
import generic_fns.structure.main
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('structure')
uf_class.title = "Class containing the structural related functions."
uf_class.menu_text = "&structure"
uf_class.gui_icon = "relax.structure"


# The structure.add_atom user function.
uf = uf_info.add_uf('structure.add_atom')
uf.title = "Add an atom."
uf.title_short = "Atom creation."
uf.add_keyarg(
    name = "atom_name",
    py_type = "str",
    desc_short = "atom name",
    desc = "The atom name."
)
uf.add_keyarg(
    name = "res_name",
    py_type = "str",
    desc_short = "residue name",
    desc = "The residue name."
)
uf.add_keyarg(
    name = "res_num",
    py_type = "int",
    min = -10000,
    max = 10000,
    desc_short = "residue number",
    desc = "The residue number."
)
uf.add_keyarg(
    name = "pos",
    default = [None, None, None],
    py_type = "float_array",
    dim = 3,
    desc_short = "atomic position",
    desc = "The atomic coordinates."
)
uf.add_keyarg(
    name = "element",
    py_type = "str",
    desc_short = "element",
    desc = "The element name.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["N", "C", "H", "O", "P"],
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_num",
    py_type = "int",
    desc_short = "atom number",
    desc = "The optional atom number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "chain_id",
    py_type = "str",
    desc_short = "optional chain ID",
    desc = "The optional chain ID string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "segment_id",
    py_type = "str",
    desc_short = "optional segment ID",
    desc = "The optional segment ID string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "pdb_record",
    py_type = "str",
    desc_short = "optional PDB record name",
    desc = "The optional PDB record name, e.g. 'ATOM' or 'HETATM'.",
    can_be_none = True
)
uf.desc = """
This allows atoms to be added to the internal structural object.
"""
uf.backend = generic_fns.structure.main.add_atom
uf.menu_text = "&add_atom"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.connect_atom user function.
uf = uf_info.add_uf('structure.connect_atom')
uf.title = "Connect two atoms."
uf.title_short = "Atom connection."
uf.add_keyarg(
    name = "index1",
    py_type = "int",
    max = 10000,
    desc_short = "index 1",
    desc = "The global index of the first atom."
)
uf.add_keyarg(
    name = "index2",
    py_type = "int",
    max = 10000,
    desc_short = "index 2",
    desc = "The global index of the second atom."
)
uf.desc = """
This allows atoms to be connected in the internal structural object.  The global index is normally equal to the PDB atom number minus 1.
"""
uf.backend = generic_fns.structure.main.connect_atom
uf.menu_text = "co&nnect_atom"
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.create_diff_tensor_pdb user function.
uf = uf_info.add_uf('structure.create_diff_tensor_pdb')
uf.title = "Create a PDB file to represent the diffusion tensor."
uf.title_short = "Diffusion tensor PDB file creation."
uf.add_keyarg(
    name = "scale",
    default = 1.8e-6,
    py_type = "num",
    desc_short = "scaling factor",
    desc = "Value for scaling the diffusion rates."
)
uf.add_keyarg(
    name = "file",
    default = "tensor.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = wx.FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory to place the file into.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will overwrite the any pre-existing file."
)
uf.desc = """
This creates a PDB file containing an artificial geometric structure to represent the diffusion tensor.  A structure must have previously been read into relax.  The diffusion tensor is represented by an ellipsoidal, spheroidal, or spherical geometric object with its origin located at the centre of mass (of the selected residues).  This diffusion tensor PDB file can subsequently read into any molecular viewer.

There are four different types of residue within the PDB.  The centre of mass of the selected residues is represented as a single carbon atom of the residue 'COM'.  The ellipsoidal geometric shape consists of numerous H atoms of the residue 'TNS'.  The axes of the tensor, when defined, are presented as the residue 'AXS' and consist of carbon atoms: one at the centre of mass and one at the end of each eigenvector.  Finally, if Monte Carlo simulations were run and the diffusion tensor parameters were allowed to vary then there will be multiple 'SIM' residues, one for each simulation.  These are essentially the same as the 'AXS' residue, representing the axes of the simulated tensors, and they will appear as a distribution.

As the Brownian rotational diffusion tensor is a measure of the rate of rotation about different axes - the larger the geometric object, the faster the diffusion of a molecule. For example the diffusion tensor of a water molecule is much larger than that of a macromolecule.

The effective global correlation time experienced by an XH bond vector, not to be confused with the Lipari and Szabo parameter tau_e, will be approximately proportional to the component of the diffusion tensor parallel to it.  The approximation is not exact due to the multiexponential form of the correlation function of Brownian rotational diffusion.  If an XH bond vector is parallel to the longest axis of the tensor, it will be unaffected by rotations about that axis, which are the fastest rotations of the molecule, and therefore its effective global correlation time will be maximal.

To set the size of the diffusion tensor within the PDB frame the unit vectors used to generate the geometric object are first multiplied by the diffusion tensor (which has the units of inverse seconds) then by the scaling factor (which has the units of second Angstroms and has the default value of 1.8e-6 s.Angstrom).  Therefore the rotational diffusion rate per Angstrom is equal the inverse of the scale value (which defaults to 5.56e5 s^-1.Angstrom^-1).  Using the default scaling value for spherical diffusion, the correspondence between global correlation time, Diso diffusion rate, and the radius of the sphere for a number of discrete cases will be:

_________________________________________________
|           |               |                   |
| tm (ns)   | Diso (s^-1)   | Radius (Angstrom) |
|___________|_______________|___________________|
|           |               |                   |
| 1         | 1.67e8        | 300               |
|           |               |                   |
| 3         | 5.56e7        | 100               |
|           |               |                   |
| 10        | 1.67e7        | 30                |
|           |               |                   |
| 30        | 5.56e6        | 10                |
|___________|_______________|___________________|


The scaling value has been fixed to facilitate comparisons within or between publications, but can be changed to vary the size of the tensor geometric object if necessary.  Reporting the rotational diffusion rate per Angstrom within figure legends would be useful.

To create the tensor PDB representation, a number of algorithms are utilised.  Firstly the centre of mass is calculated for the selected residues and is represented in the PDB by a C atom.  Then the axes of the diffusion are calculated, as unit vectors scaled to the appropriate length (multiplied by the eigenvalue Dx, Dy, Dz, Dpar, Dper, or Diso as well as the scale value), and a C atom placed at the position of this vector plus the centre of mass.  Finally a uniform distribution of vectors on a sphere is generated using spherical coordinates.  By incrementing the polar angle using an arccos distribution, a radial array of vectors representing latitude are created while incrementing the azimuthal angle evenly creates the longitudinal vectors.  These unit vectors, which are distributed within the PDB frame and are of 1 Angstrom in length, are first rotated into the diffusion frame using a rotation matrix (the spherical diffusion tensor is not rotated).  Then they are multiplied by the diffusion tensor matrix to extend the vector out to the correct length, and finally multiplied by the scale value so that the vectors reasonably superimpose onto the macromolecular structure.  The last set of algorithms place all this information into a PDB file.  The distribution of vectors are represented by H atoms and are all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on the both the longitude and latitude.  This creates a geometric PDB object with longitudinal and latitudinal lines.
"""
uf.backend = generic_fns.structure.geometric.create_diff_tensor_pdb
uf.menu_text = "&create_diff_tensor_pdb"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 800)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'create_diff_tensor_pdb.png'


# The structure.create_vector_dist user function.
uf = uf_info.add_uf('structure.create_vector_dist')
uf.title = "Create a PDB file representation of the distribution of XH bond vectors."
uf.title_short = "XH vector distribution PDB representation."
uf.add_keyarg(
    name = "length",
    default = 2e-9,
    py_type = "num",
    desc_short = "vector length",
    desc = "The length of the vectors in the PDB representation (meters)."
)
uf.add_keyarg(
    name = "file",
    default = "XH_dist.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = wx.FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory to place the file into.",
    can_be_none = True
)
uf.add_keyarg(
    name = "symmetry",
    default = True,
    py_type = "bool",
    desc_short = "symmetry flag",
    desc = "A flag which if True will create a second chain with reversed XH bond orientations."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will overwrite the file if it already exists."
)
uf.desc = """
This creates a PDB file containing an artificial vectors, the length of which default to the length argument of 20 Angstrom.  A structure must have previously been read into relax.  The origin of the vector distribution is located at the centre of mass (of the selected residues).  This vector distribution PDB file can subsequently be read into any molecular viewer.

Because of the symmetry of the diffusion tensor reversing the orientation of the XH bond vector has no effect.  Therefore by setting the symmetry flag two chains 'A' and 'B' will be added to the PDB file whereby chain 'B' is chain 'A' with the XH bonds reversed.
"""
uf.backend = generic_fns.structure.geometric.create_vector_dist
uf.menu_text = "cr&eate_vector_dist"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'create_vector_dist.png'


# The structure.get_pos user function.
uf = uf_info.add_uf('structure.get_pos')
uf.title = "Extract the atomic positions from the loaded structures for the given spins."
uf.title_short = "Atomic position extraction."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "ave_pos",
    default = True,
    py_type = "bool",
    desc_short = "average position flag",
    desc = "A flag specifying if the position of the atom is to be averaged across models."
)
uf.desc = """
This allows the atomic positions of the spins to be extracted from the loaded structures.  This is automatically performed by the structure.load_spins() user function, but if the sequence information is generated in other ways, this user function allows the structural information to be obtained.

If averaging the atomic positions, then average position of all models will be loaded into the spin container.  Otherwise the positions from all models will be loaded separately.
"""
uf.prompt_examples = """
For a model-free backbone amide nitrogen analysis whereby the N spins have already been
created, to obtain the backbone N positions from the file '1F3Y.pdb' (which is a single
protein), type the following two user functions:

relax> structure.read_pdb('1F3Y.pdb')
relax> structure.get_pos(spin_id='@N')
"""
uf.backend = generic_fns.structure.main.get_pos
uf.menu_text = "&get_pos"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.delete user function.
uf = uf_info.add_uf('structure.delete')
uf.title = "Delete all structural information."
uf.title_short = "Structure deletion."
uf.desc = """
This will delete all the structural information from the current data pipe.  All spin and sequence information loaded from these structures will be preserved - this only affects the structural data.
"""
uf.prompt_examples = """
Simply type:

relax> structure.delete()
"""
uf.backend = generic_fns.structure.main.delete
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_size = (600, 400)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.displacement user function.
uf = uf_info.add_uf('structure.displacement')
uf.title = "Determine the rotational and translational displacement between a set of models."
uf.title_short = "Rotational and translational displacement."
uf.add_keyarg(
    name = "model_from",
    py_type = "int",
    desc_short = "model from",
    desc = "The optional model number for the starting position of the displacement.",
    can_be_none = True
)
uf.add_keyarg(
    name = "model_to",
    py_type = "int",
    desc_short = "model to",
    desc = "The optional model number for the ending position of the displacement.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom identification string",
    desc = "The atom identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "centroid",
    py_type = "float_array",
    desc_short = "centroid position",
    desc = "The alternative position of the centroid.",
    can_be_none = True
)
uf.desc = """
This user function allows the rotational and translational displacement between two models of the same structure to be calculated.  The information will be printed out in various formats and held in the relax data store.  This is directional, so there is a starting and ending position for each displacement.  If the starting and ending models are not specified, then the displacements in all directions between all models will be calculated.

The atom ID, which uses the same notation as the spin ID strings, can be used to restrict the displacement calculation to certain molecules, residues, or atoms.  This is useful if studying domain motions, secondary structure rearrangements, amino acid side chain rotations, etc.

By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the motion.  The allows, for example, a pivot of a rotational domain motion to be specified.  This is not a formally correct algorithm, all translations will be zero, but does give an indication to the amplitude of the pivoting angle.
"""
uf.prompt_examples = """
To determine the rotational and translational displacements between all sets of models, type:

relax> structure.displacement()


To determine the displacement from model 5 to all other models, type:

relax> structure.displacement(model_from=5)


To determine the displacement of all models to model 5, type:

relax> structure.displacement(model_to=5)



To determine the displacement of model 2 to model 3, type one of:

relax> structure.displacement(2, 3)
relax> structure.displacement(model_from=2, model_to=3)
"""
uf.backend = generic_fns.structure.main.displacement
uf.menu_text = "displace&ment"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.find_pivot user function.
uf = uf_info.add_uf('structure.find_pivot')
uf.title = "Find the pivot point of the motion of a set of structures."
uf.title_short = "Pivot search."
uf.add_keyarg(
    name = "models",
    py_type = "int_list",
    desc_short = "model list",
    desc = "The list of models to use.",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "init_pos",
    py_type = "float_array",
    desc_short = "initial pivot position",
    desc = "The initial position of the pivot.",
    can_be_none = True
)
uf.desc = """
This is used to find pivot point of motion between a set of structural models.  If the list of models is not supplied, then all models will be used.

The atom ID, which uses the same notation as the spin ID strings, can be used to restrict the search to certain molecules, residues, or atoms.  For example to only use backbone heavy atoms in a protein, use the atom ID of '@N,C,CA,O', assuming those are the names of the atoms from the structural file.

By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the superimposition.  The allows, for example, the superimposition about a pivot point.
"""
uf.backend = generic_fns.structure.main.find_pivot
uf.menu_text = "&find_pivot"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.load_spins user function.
uf = uf_info.add_uf('structure.load_spins')
uf.title = "Load spins from the structure into the relax data store."
uf.title_short = "Loading spins from structure."
uf.add_keyarg(
    name = "spin_id",
    default = "@N",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID string",
    desc = "The spin identification string for the selective loading of certain spins into the relax data store.",
    can_be_none = True
)
uf.add_keyarg(
    name = "ave_pos",
    default = True,
    py_type = "bool",
    desc_short = "average position flag",
    desc = "A flag specifying if the position of the atom is to be averaged across models."
)
uf.desc = """
This allows a sequence to be generated within the relax data store using the atomic information from the structure already associated with this data pipe.  The spin ID string is used to select which molecules, which residues, and which atoms will be recognised as spin systems within relax.  If the spin ID is left unspecified, then all molecules, residues, and atoms will be placed within the data store (and all atoms will be treated as spins).

If averaging the atomic positions, then average position of all models will be loaded into the spin container.  Otherwise the positions from all models will be loaded separately.
"""
uf.prompt_examples = """
For a model-free backbone amide nitrogen analysis, to load just the backbone N sequence from
the file '1F3Y.pdb' (which is a single protein), type the following two user functions:

relax> structure.read_pdb('1F3Y.pdb')
relax> structure.load_spins(spin_id='@N')


For an RNA analysis of adenine C8 and C2, guanine C8 and N1, cytidine C5 and C6, and uracil
N3, C5, and C6, type the following series of commands (assuming that the PDB file with this
atom naming has already been read):

relax> structure.load_spins(spin_id=":A@C8")
relax> structure.load_spins(spin_id=":A@C2")
relax> structure.load_spins(spin_id=":G@C8")
relax> structure.load_spins(spin_id=":G@N1")
relax> structure.load_spins(spin_id=":C@C5")
relax> structure.load_spins(spin_id=":C@C6")
relax> structure.load_spins(spin_id=":U@N3")
relax> structure.load_spins(spin_id=":U@C5")
relax> structure.load_spins(spin_id=":U@C6")

Alternatively using some Python programming:

relax> for id in [":A@C8", ":A@C2", ":G@C8", ":G@N1", ":C@C5", ":C@C6", ":U@N3", ":U@C5", ":U@C6"]:
relax>     structure.load_spins(spin_id=id)
"""
uf.backend = generic_fns.structure.main.load_spins
uf.menu_text = "&load_spins"
uf.gui_icon = "relax.spin"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'load_spins.png'


# The structure.read_pdb user function.
uf = uf_info.add_uf('structure.read_pdb')
uf.title = "Reading structures from PDB files."
uf.title_short = "PDB reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "read_mol",
    py_type = "int_or_int_list",
    desc_short = "read molecule number",
    desc = "If set, only the given molecule(s) will be read.  The molecules are determined differently by the different parsers, but are numbered consecutively from 1.  If unset, then all molecules will be loaded.  By providing a list of numbers such as [1, 2], multiple molecules will be read.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_mol_name",
    py_type = "str_or_str_list",
    desc_short = "set molecule names",
    desc = "Set the names of the read molecules.  If unset, then the molecules will be automatically labelled based on the file name or other information.  This can either be a single name or a list of names.",
    can_be_none = True
)
uf.add_keyarg(
    name = "read_model",
    py_type = "int_or_int_list",
    desc_short = "read model",
    desc = "If set, only the given model number(s) from the PDB file will be read.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_model_num",
    py_type = "int_or_int_list",
    desc_short = "set model numbers",
    desc = "Set the model numbers of the loaded molecules.  If unset, then the PDB model numbers will be preserved if they exist.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "parser",
    default = "internal",
    py_type = "str",
    desc_short = "PDB parser",
    desc = "The PDB parser used to read the file.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["Fast internal PDB parser", "Scientific Python PDB parser"],
    wiz_combo_data = ["internal", "scientific"],
    wiz_read_only = True
)
uf.desc = """
The reading of PDB files into relax is quite a flexible procedure allowing for both models, defined as an ensemble of the same molecule but with different atomic positions, and different molecules within the same model.  One of more molecules can exist in one or more models.  The flexibility allows PDB models to be converted into different molecules and different PDB files loaded as the same molecule but as different models.

A few different PDB parsers can be used to read the structural data.  The choice of which to use depends on whether your PDB file is supported by that reader.  These are selected by setting the 'parser' argument to one of:

    'internal' - a fast PDB parser built into relax.
    'scientific' - the Scientific Python PDB parser.

In a PDB file, the models are specified by the MODEL PDB record.  All the supported PDB readers in relax recognise this.  The molecule level is quite different between the Scientific Python and internal readers.  For how Scientific Python defines molecules, please see its documentation.  The internal reader is far simpler as it defines molecules using the TER PDB record.  In both cases, the molecules will be numbered consecutively from 1.

Setting the molecule name allows the molecule within the PDB (within one model) to have a custom name.  If not set, then the molecules will be named after the file name, with the molecule number appended if more than one exists.

Note that relax will complain if it cannot work out what to do.

This is able to handle uncompressed, bzip2 compressed files, or gzip compressed files automatically.  The full file name including extension can be supplied, however, if the file cannot be found, this function will search for the file name with '.bz2' appended followed by the file name with '.gz' appended.
"""
uf.prompt_examples = """
To load all structures from the PDB file 'test.pdb' in the directory '~/pdb', including all
models and all molecules, type one of:

relax> structure.read_pdb('test.pdb', '~/pdb')
relax> structure.read_pdb(file='test.pdb', dir='pdb')


To load the 10th model from the file 'test.pdb' using the Scientific Python PDB parser and
naming it 'CaM', use one of:

relax> structure.read_pdb('test.pdb', read_model=10, set_mol_name='CaM',
                          parser='scientific')
relax> structure.read_pdb(file='test.pdb', read_model=10, set_mol_name='CaM',
                          parser='scientific')


To load models 1 and 5 from the file 'test.pdb' as two different structures of the same
model, type one of:

relax> structure.read_pdb('test.pdb', read_model=[1, 5], set_model_num=[1, 1])
relax> structure.read_pdb('test.pdb', set_mol_name=['CaM_1', 'CaM_2'], read_model=[1, 5],
                          set_model_num=[1, 1])

To load the files 'lactose_MCMM4_S1_1.pdb', 'lactose_MCMM4_S1_2.pdb',
'lactose_MCMM4_S1_3.pdb' and 'lactose_MCMM4_S1_4.pdb' as models, type the following sequence
of commands:

relax> structure.read_pdb('lactose_MCMM4_S1_1.pdb', set_mol_name='lactose_MCMM4_S1',
                          set_model_num=1)
relax> structure.read_pdb('lactose_MCMM4_S1_2.pdb', set_mol_name='lactose_MCMM4_S1',
                          set_model_num=2)
relax> structure.read_pdb('lactose_MCMM4_S1_3.pdb', set_mol_name='lactose_MCMM4_S1',
                          set_model_num=3)
relax> structure.read_pdb('lactose_MCMM4_S1_4.pdb', set_mol_name='lactose_MCMM4_S1',
                          set_model_num=4)
"""
uf.backend = generic_fns.structure.main.read_pdb
uf.menu_text = "read_&pdb"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'read_pdb.png'


# The structure.read_xyz user function.
uf = uf_info.add_uf('structure.read_xyz')
uf.title = "Reading structures from XYZ files."
uf.title_short = "XYZ reading."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the XYZ file.",
    wiz_filesel_wildcard = "XYZ files (*.xyz)|*.xyz;*.XYZ",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "read_mol",
    py_type = "int_or_int_list",
    desc_short = "read molecule number",
    desc = "If set, only the given molecule(s) will be read.  The molecules are determined differently by the different parsers, but are numbered consecutively from 1.  If unset, then all molecules will be loaded.  By providing a list of numbers such as [1, 2], multiple molecules will be read.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_mol_name",
    py_type = "str_or_str_list",
    desc_short = "set molecule names",
    desc = "Set the names of the read molecules.  If unset, then the molecules will be automatically labelled based on the file name or other information.  This can either be a single name or a list of names.",
    can_be_none = True
)
uf.add_keyarg(
    name = "read_model",
    py_type = "int_or_int_list",
    desc_short = "read model",
    desc = "If set, only the given model number(s) from the PDB file will be read.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "set_model_num",
    py_type = "int_or_int_list",
    desc_short = "set model numbers",
    desc = "Set the model numbers of the loaded molecules.  If unset, then the PDB model numbers will be preserved if they exist.  This can be a single number or list of numbers.",
    can_be_none = True
)
uf.desc = """
The XYZ files with different models, which defined as an ensemble of the same molecule but with different atomic positions, can be read into relax. If there are several molecules in one xyz file, please seperate them into different files and then load them individually. Loading different models and different molecules is controlled by the four keyword arguments 'read_mol', 'set_mol_name', 'read_model', and 'set_model_num'.

The 'set_mol_name' argument is used to name the molecules within the XYZ (within one model).  If not set, then the molecules will be named after the file name, with the molecule number appended if more than one exists.

Note that relax will complain if it cannot work out what to do.
"""
uf.prompt_examples = """
To load all structures from the XYZ file 'test.xyz' in the directory '~/xyz', including all
models and all molecules, type one of:

relax> structure.read_xyz('test.xyz', '~/xyz')
relax> structure.read_xyz(file='test.xyz', dir='xyz')


To load the 10th model from the file 'test.xyz' and
naming it 'CaM', use one of:

relax> structure.read_xyz('test.xyz', read_model=10, set_mol_name='CaM')
relax> structure.read_xyz(file='test.xyz', read_model=10, set_mol_name='CaM')


To load models 1 and 5 from the file 'test.xyz' as two different structures of the same
model, type one of:

relax> structure.read_xyz('test.xyz', read_model=[1, 5], set_model_num=[1, 1])
relax> structure.read_xyz('test.xyz', set_mol_name=['CaM_1', 'CaM_2'], read_model=[1, 5],
                          set_model_num=[1, 1])

To load the files 'test_1.xyz', 'test_2.xyz', 'test_3.xyz' and 'test_4.xyz' as models, type the 
following sequence of commands:

relax> structure.read_xyz('test_1.xyz', set_mol_name='test_1',
                          set_model_num=1)
relax> structure.read_xyz('test_2.xyz', set_mol_name='test_2',
                          set_model_num=2)
relax> structure.read_xyz('test_3.xyz', set_mol_name='test_3',
                          set_model_num=3)
relax> structure.read_xyz('test_4.xyz', set_mol_name='test_4',
                          set_model_num=4)
"""
uf.backend = generic_fns.structure.main.read_xyz
uf.menu_text = "read_&xyz"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.rotate user function.
uf = uf_info.add_uf('structure.rotate')
uf.title = "Rotate the internal structural object about the given origin by the rotation matrix."
uf.title_short = "Structure rotation."
uf.add_keyarg(
    name = "R",
    py_type = "float_matrix",
    default = eye(3),
    dim = (3, 3),
    desc_short = "rotation matrix",
    desc = "The rotation matrix in forwards rotation notation."
)
uf.add_keyarg(
    name = "origin",
    py_type = "float_array",
    dim = 3,
    desc_short = "origin of rotation",
    desc = "The origin or pivot of the rotation.",
    can_be_none = True
)
uf.add_keyarg(
    name = "model",
    py_type = "int",
    desc_short = "model",
    desc = "The model to rotate (which if not set will cause all models to be rotated).",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
uf.desc = """
This is used to rotate the internal structural data by the given rotation matrix.  If the origin is supplied, then this will act as the pivot of the rotation.  Otherwise, all structural data will be rotated about the point [0, 0, 0].  The model argument can be used to rotate specific models.
"""
uf.backend = generic_fns.structure.main.rotate
uf.menu_text = "&rotate"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.superimpose user function.
uf = uf_info.add_uf('structure.superimpose')
uf.title = "Superimpose a set of models of the same structure."
uf.title_short = "Structural superimposition."
uf.add_keyarg(
    name = "models",
    py_type = "int_list",
    desc_short = "model list",
    desc = "The list of models to superimpose.",
    can_be_none = True
)
uf.add_keyarg(
    name = "method",
    default = "fit to mean",
    py_type = "str",
    desc_short = "superimposition method",
    desc = "The superimposition method.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["fit to mean", "fit to first"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "centroid",
    py_type = "float_array",
    desc_short = "centroid position",
    desc = "The alternative position of the centroid.",
    can_be_none = True
)
uf.desc = """
This allows a set of models of the same structure to be superimposed to each other.  Two superimposition methods are currently supported:

    'fit to mean':  All models are fit to the mean structure.  This is the default and most accurate method for an ensemble description.  It is an iterative method which first calculates a mean structure and then fits each model to the mean structure using the Kabsch algorithm.  This is repeated until convergence.
    'fit to first':  This is quicker but is not as accurate for an ensemble description.  The Kabsch algorithm is used to rotate and translate each model to be superimposed onto the first model.

If the list of models is not supplied, then all models will be superimposed.

The atom ID, which uses the same notation as the spin ID strings, can be used to restrict the superimpose calculation to certain molecules, residues, or atoms.  For example to only superimpose backbone heavy atoms in a protein, use the atom ID of '@N,C,CA,O', assuming those are the names of the atoms from the structural file.

By supplying the position of the centroid, an alternative position than the standard rigid body centre is used as the focal point of the superimposition.  The allows, for example, the superimposition about a pivot point.
"""
uf.prompt_examples = """
To superimpose all sets of models, type one of:

relax> structure.superimpose()
relax> structure.superimpose(method='fit to mean')


To superimpose the models 1, 2, 3, 5 onto model 4, type:

relax> structure.superimpose(models=[4, 1, 2, 3, 5], method='fit to first')


To superimpose an ensemble of protein structures using only the backbone heavy atoms, type
one of:

relax> structure.superimpose(atom_id='@N,C,CA,O')
relax> structure.superimpose(method='fit to mean', atom_id='@N,C,CA,O')


To superimpose model 2 onto model 3 using backbone heavy atoms, type one of:

relax> structure.superimpose([3, 2], 'fit to first', '@N,C,CA,O')
relax> structure.superimpose(models=[3, 2], method='fit to first', atom_id='@N,C,CA,O')
"""
uf.backend = generic_fns.structure.main.superimpose
uf.menu_text = "&superimpose"
uf.wizard_apply_button = False
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.translate user function.
uf = uf_info.add_uf('structure.translate')
uf.title = "Laterally displace the internal structural object by the translation vector."
uf.title_short = "Structure translation."
uf.add_keyarg(
    name = "T",
    py_type = "float_array",
    dim = 3,
    desc_short = "translation vector",
    desc = "The translation vector."
)
uf.add_keyarg(
    name = "model",
    py_type = "int",
    desc_short = "model",
    desc = "The model to translate (which if not set will cause all models to be translate).",
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom identification string.",
    can_be_none = True
)
uf.desc = """
This is used to translate the internal structural data by the given translation vector.  The model argument can be used to translate specific models.
"""
uf.backend = generic_fns.structure.main.translate
uf.menu_text = "&translate"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.vectors user function.
uf = uf_info.add_uf('structure.vectors')
uf.title = "Extract and store the bond vectors from the loaded structures in the spin container."
uf.title_short = "Bond vector extraction."
uf.add_keyarg(
    name = "attached",
    default = "H",
    py_type = "str",
    desc_short = "attached atom",
    desc = "The name of the second atom which attached to the spin of interest.  Regular expression is allowed, for example 'H*'."
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "model",
    py_type = "int",
    desc_short = "model",
    desc = "The model to extract bond vectors from (which if not set will cause the vectors of all models to be extracted).",
    can_be_none = True
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print to screen.  Zero corresponds to minimal output while higher values increase the amount of output.  The default value is 1."
)
uf.add_keyarg(
    name = "ave",
    default = True,
    py_type = "bool",
    desc_short = "average vector flag",
    desc = "A flag which if True will cause the bond vectors from all models to be averaged.  If vectors from only one model is extracted, this argument will have no effect."
)
uf.add_keyarg(
    name = "unit",
    default = True,
    py_type = "bool",
    desc_short = "unit vector flag",
    desc = "A flag which if True will cause the unit vector to calculated rather than the full length bond vector."
)
uf.desc = """
For a number of types of analysis, bond vectors or unit bond vectors are required for the calculations.  This user function allows these vectors to be extracted from the loaded structures.  The bond vector will be that from the atom associated with the spin system loaded in relax to the bonded atom specified by the 'attached' argument.  For example if the attached atom is set to 'H' and the protein backbone amide spins 'N' are loaded, the all 'N-H' vectors will be extracted.  But if set to 'CA', all atoms named 'CA' in the structures will be searched for and all 'N-Ca' bond vectors will be extracted.

The extraction of vectors can occur in a number of ways.  For example if an NMR structure with N models is loaded or if multiple molecules, from any source, of the same compound are loaded as different models, there are three options for extracting the bond vector.  Firstly the bond vector of a single model can be extracted by setting the model number. Secondly the bond vectors from all models can be extracted if the model number is not set and the average vector flag is not set.  Thirdly, if the model number is not set and the average vector flag is set, then a single vector which is the average for all models will be calculated.
"""
uf.prompt_examples = """
To extract the XH vectors of the backbone amide nitrogens where in the PDB file the backbone
nitrogen is called 'N' and the attached atom is called 'H', assuming multiple types of
spin have already been loaded, type one of:

relax> structure.vectors(spin_id='@N')
relax> structure.vectors('H', spin_id='@N')
relax> structure.vectors(attached='H', spin_id='@N')

If the attached atom is called 'HN', type:

relax> structure.vectors(attached='HN', spin_id='@N')

For the 'CA' spin bonded to the 'HA' proton, type:

relax> structure.vectors(attached='HA', spin_id='@CA')


If you are working with RNA, you can use the residue name identifier to calculate the
vectors for each residue separately.  For example to calculate the vectors for all possible
spins in the bases, type:

relax> structure.vectors('H2', spin_id=':A')
relax> structure.vectors('H8', spin_id=':A')
relax> structure.vectors('H1', spin_id=':G')
relax> structure.vectors('H8', spin_id=':G')
relax> structure.vectors('H5', spin_id=':C')
relax> structure.vectors('H6', spin_id=':C')
relax> structure.vectors('H3', spin_id=':U')
relax> structure.vectors('H5', spin_id=':U')
relax> structure.vectors('H6', spin_id=':U')

Alternatively, assuming the desired spins have been loaded, regular expression can be used:

relax> structure.vectors('H*')
"""
uf.backend = generic_fns.structure.main.vectors
uf.menu_text = "&vectors"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + '2JK4.png'


# The structure.write_pdb user function.
uf = uf_info.add_uf('structure.write_pdb')
uf.title = "Writing structures to a PDB file."
uf.title_short = "PDB writing."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = wx.FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "model_num",
    py_type = "int",
    desc_short = "model number",
    desc = "Restrict the writing of structural data to a single model in the PDB file.",
    can_be_none = True
)
uf.add_keyarg(
    name = "compress_type",
    default = 0,
    py_type = "int",
    desc_short = "compression type",
    desc = "The type of compression to use when creating the file.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "No compression",
        "bzip2 compression",
        "gzip compression"
    ],
    wiz_combo_data = [
        0,
        1,
        2
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if set to True will cause any pre-existing files to be overwritten."
)
uf.desc = """
This will write all of the structural data loaded in the current data pipe to be converted to the PDB format and written to file.  Specifying the model number allows single models to be output.

The default behaviour of this function is to not compress the file.  The compression can, however, be changed to either bzip2 or gzip compression.  If the '.bz2' or '.gz' extension is not included in the file name, it will be added.  This behaviour is controlled by the compress_type argument which can be set to

    0:  No compression (no file extension).
    1:  bzip2 compression ('.bz2' file extension).
    2:  gzip compression ('.gz' file extension).
"""
uf.prompt_examples = """
To write all models and molecules to the PDB file 'ensemble.pdb' within the directory '~/pdb', type
one of:

relax> structure.write_pdb('ensemble.pdb', '~/pdb')
relax> structure.write_pdb(file='ensemble.pdb', dir='pdb')


To write model number 3 into the new file 'test.pdb', use one of:

relax> structure.write_pdb('test.pdb', model_num=3)
relax> structure.write_pdb(file='test.pdb', model_num=3)
"""
uf.backend = generic_fns.structure.main.write_pdb
uf.menu_text = "&write_pdb"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 700)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'structure' + sep + 'write_pdb.png'

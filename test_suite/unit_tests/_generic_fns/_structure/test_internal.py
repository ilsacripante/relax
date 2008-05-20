###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
import sys
from numpy import fromstring
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store
from generic_fns.mol_res_spin import Selection
from generic_fns.structure.internal import Internal


class Test_internal(TestCase):
    """Unit tests for the functions of the 'generic_fns.structure.internal' module."""

    def setUp(self):
        """Set up for all the internal relax structural object unit tests."""

        # Get the relative path of relax.
        self.path = sys.path[0]
        if self.path == '.':
            self.path = sys.path[-1]

        # The path to a PDB file.
        self.test_pdb_path = self.path+'/test_suite/shared_data/structures/Ap4Aase_res1-12.pdb'

        # Instantiate the structural data object.
        self.data = Internal()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Delete the structural data object.
        del self.data

        # Reset.
        relax_data_store.__reset__()


    def test___molecule_loop(self):
        """Test the private Internal.__molecule_loop() method."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the molecules.
        mol_count = 0
        for mol, mol_name, mol_type in self.data._Internal__molecule_loop(self.data.structural_data[0]):
            mol_count = mol_count + 1

        # Test the number of molecules looped over.
        self.assertEqual(mol_count, 1)

        # Test the molecular data.
        self.assertEqual(mol_name, None)
        self.assertEqual(mol_type, 'protein')
        self.assertEqual(len(mol.residues), 12)
        self.assertEqual(mol.sequence(), ['GLY', 'PRO', 'LEU', 'GLY', 'SER', 'MET', 'ASP', 'SER', 'PRO', 'PRO', 'GLU', 'GLY'])


    def test___molecule_loop_selection(self):
        """Test the private Internal.__molecule_loop() method with a selection object."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Create the selection object (which should match the molecule name of None).
        sel_obj = Selection('@1')

        # Loop over the molecules.
        mol_count = 0
        for mol, mol_name, mol_type in self.data._Internal__molecule_loop(self.data.structural_data[0], sel_obj):
            mol_count = mol_count + 1

        # Test the number of molecules looped over.
        self.assertEqual(mol_count, 1)

        # Test the molecular data.
        self.assertEqual(mol_name, None)
        self.assertEqual(mol_type, 'protein')
        self.assertEqual(len(mol.residues), 12)
        self.assertEqual(mol.sequence(), ['GLY', 'PRO', 'LEU', 'GLY', 'SER', 'MET', 'ASP', 'SER', 'PRO', 'PRO', 'GLU', 'GLY'])


    def test___molecule_loop_selection_no_match(self):
        """Test the Internal.__molecule_loop() method with a non-matching selection object."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Create the non-matching selection object.
        sel_obj = Selection('#XXX')

        # Loop over the molecules.
        mol_count = 0
        for mol, mol_name, mol_type in self.data._Internal__molecule_loop(self.data.structural_data[0], sel_obj):
            mol_count = mol_count + 1

        # Test the number of molecules looped over.
        self.assertEqual(mol_count, 0)


    def test___residue_loop(self):
        """Test the private Internal.__residue_loop() method."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the residues.
        res_count = 0
        for res, res_num, res_name in self.data._Internal__residue_loop(self.data.structural_data[0].peptide_chains[0], None, 'protein'):
            res_count = res_count + 1

        # Test the number of residues looped over.
        self.assertEqual(res_count, 12)

        # Test the data of the last residue.
        self.assertEqual(res_num, 12)
        self.assertEqual(res_name, 'GLY')
        self.assertEqual(len(res.atoms), 7)
        self.assertEqual(res.atoms.keys(), ['C', 'H', 'CA', 'O', 'N', '1HA', '2HA'])


    def test___residue_loop_selection(self):
        """Test the private Internal.__residue_loop() method with a selection object."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Create the selection object (which should match the residue name of None).
        sel_obj = Selection('#Ap4Aase')

        # Loop over the residues.
        res_count = 0
        for res, res_num, res_name in self.data._Internal__residue_loop(self.data.structural_data[0].peptide_chains[0], 'Ap4Aase', 'protein', sel_obj):
            res_count = res_count + 1

        # Test the number of residues looped over.
        self.assertEqual(res_count, 12)

        # Test the data of the last residue.
        self.assertEqual(res_num, 12)
        self.assertEqual(res_name, 'GLY')
        self.assertEqual(len(res.atoms), 7)
        self.assertEqual(res.atoms.keys(), ['C', 'H', 'CA', 'O', 'N', '1HA', '2HA'])


    def test___residue_loop_selection_no_match(self):
        """Test the Internal.__residue_loop() method with a non-matching selection object."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Create the non-matching selection object.
        sel_obj = Selection(':XXX')

        # Loop over the residues.
        res_count = 0
        for res, res_num, res_name in self.data._Internal__residue_loop(self.data.structural_data[0].peptide_chains[0], None, 'protein', sel_obj):
            res_count = res_count + 1

        # Test the number of residues looped over.
        self.assertEqual(res_count, 0)


    def test_atom_loop(self):
        """Test the Internal.atom_loop() method."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for atom in self.data.atom_loop():
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 150)


    def test_atom_loop_mol_selection(self):
        """Test the Internal.atom_loop() method with the '#XXX' mol selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for atom in self.data.atom_loop(atom_id='#XXX'):
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 0)


    def test_atom_loop_res_selection1(self):
        """Test the Internal.atom_loop() method with the ':8' res selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for res_num, res_name in self.data.atom_loop(atom_id=':8', res_num_flag=True, res_name_flag=True):
            # Test the residue name and number.
            self.assertEqual(res_num, 8)
            self.assertEqual(res_name, 'SER')

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 11)


    def test_atom_loop_res_selection2(self):
        """Test the Internal.atom_loop() method with the ':PRO' res selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for atom in self.data.atom_loop(atom_id=':PRO', res_name_flag=True):
            # Test the residue name.
            self.assertEqual(atom[0], 'PRO')

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 42)


    def test_atom_loop_spin_selection1(self):
        """Test the Internal.atom_loop() method with the '@CA' spin selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for spin_name in self.data.atom_loop(atom_id='@CA', atom_name_flag=True):
            # Test the spin name.
            self.assertEqual(spin_name[0], 'CA')

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 12)


    def test_atom_loop_spin_selection2(self):
        """Test the Internal.atom_loop() method with the '@163' spin selection."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Loop over the atoms.
        atom_count = 0
        for model_num, mol_name, res_num, res_name, spin_num, spin_name, element, pos in self.data.atom_loop(atom_id='@163', model_num_flag=True, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True):
            # Test the spin info.
            self.assertEqual(model_num, 1)
            self.assertEqual(mol_name, None)
            self.assertEqual(res_num, 11)
            self.assertEqual(res_name, 'GLU')
            self.assertEqual(spin_num, 163)
            self.assertEqual(spin_name, 'OE1')
            self.assertEqual(element, 'O')
            self.assertEqual(pos.tostring(), '\\\x8f\xc2\xf5(\x1c$@\xecQ\xb8\x1e\x85\xeb\x05\xc0\x89A`\xe5\xd0b*\xc0')

            # Increment the atom count.
            atom_count = atom_count + 1

        # Test the number of atoms looped over.
        self.assertEqual(atom_count, 1)


    def test_load_pdb(self):
        """Load a PDB file using Internal.load_pdb()."""

        # Load the PDB file.
        self.data.load_pdb(self.test_pdb_path)

        # Test the structural data.
        self.assertEqual(self.data.file_name, self.test_pdb_path)
        self.assertEqual(self.data.model, None)
        self.assertEqual(len(self.data.structural_data), 1)
        self.assertEqual(type(self.data.structural_data), list)
        self.assertEqual(self.data.structural_data[0].filename, self.test_pdb_path)

###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007 Edward d'Auvergne                             #
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

# relax module imports.
from data import Data as relax_data_store
from generic_fns.selection import count_spins, parse_token, spin_loop, tokenise
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoPdbChainError, RelaxNoPipeError, RelaxNoSequenceError, RelaxSequenceError
from relax_io import extract_data, open_write_file, strip
import sys



def display(mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None):
    """Function for displaying the molecule, residue, and/or spin sequence data.

    This calls the write_body() function to do most of the work.


    @param mol_name_col:    The column to contain the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column to contain the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column to contain the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column to contain the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column to contain the spin number information.
    @type spin_num_col:     int or None
    @param sep:             The column seperator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if the sequence data is loaded.
    if not count_spins():
        raise RelaxNoSequenceError

    # Write the data.
    write_body(file=sys.stdout, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep)


def load_PDB_sequence(spin_id=None):
    """Function for loading the sequence out of a PDB file.

    @param spin_id: The molecule, residue, and spin identifier string.
    @type spin_id:  str
    """

    # Print out.
    print "\nLoading the sequence from the PDB file.\n"

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Reassign the sequence of the first structure.
    if cdp.structure.structures[0].peptide_chains:
        chains = cdp.structure.structures[0].peptide_chains
        molecule = 'protein'
    elif cdp.structure.structures[0].nucleotide_chains:
        chains = cdp.structure.structures[0].nucleotide_chains
        molecule = 'nucleic acid'
    else:
        raise RelaxNoPdbChainError

    # Split up the selection string.
    mol_token, res_token, spin_token = tokenise(spin_id)

    # Parse the tokens.
    molecules = parse_token(mol_token)
    residues = parse_token(res_token)
    spins = parse_token(spin_token)

    # Init some indecies.
    mol_index = 0
    res_index = 0
    spin_index = 0

    # Loop over the molecules.
    for chain in chains:
        # The name of the molecule.
        if chain.chain_id:
            mol_name = chain.chain_id
        elif chain.segment_id:
            mol_name = chain.segment_id
        else:
            mol_name = None

        # Skip non-matching molecules.
        if mol_token and mol_name not in molecules:
            continue

        # Add the molecule if there is a molecule name (otherwise everything goes into the default first MolecularContainer).
        if mol_name:
            # Replace the first empty molecule.
            if mol_index == 0 and cdp.mol[0].name == None:
                cdp.mol[0].name = mol_name

            # Create a new molecule.
            else:
                # Add the molecule.
                cdp.mol.add_item(mol_name=mol_name)

        # Loop over the residues.
        for res in chain.residues:
            # The residue name and number.
            if molecule == 'nucleic acid':
                res_name = res.name[-1]
            else:
                res_name = res.name
            res_num = res.number

            # Skip non-matching residues.
            if res_token and not (res_name in residues or res_num in residues):
                continue

            # Replace the first empty residue.
            if res_index == 0 and cdp.mol[mol_index].res[0].name == None:
                cdp.mol[mol_index].res[0].name = res_name
                cdp.mol[mol_index].res[0].num = res_num

            # Create a new residue.
            else:
                # Add the residue.
                cdp.mol[mol_index].res.add_item(res_name=res_name, res_num=res_num)

            # Loop over the spins.
            for atom in res.atom_list:
                # The spin name and number.
                spin_name = atom.name
                spin_num = atom.properties['serial_number']

                # Skip non-matching spins.
                if spin_token and not (spin_name in spins or spin_num in spins):
                    continue

                # Replace the first empty residue.
                if spin_index == 0 and cdp.mol[mol_index].res[res_index].spin[0].name == None:
                    cdp.mol[mol_index].res[res_index].spin[0].name = spin_name
                    cdp.mol[mol_index].res[res_index].spin[0].num = spin_num

                # Create a new residue.
                else:
                    # Add the residue.
                    cdp.mol[mol_index].res[res_index].spin.add_item(spin_name=spin_name, spin_num=spin_num)

                # Increment the residue index.
                spin_index = spin_index + 1

            # Increment the residue index.
            res_index = res_index + 1

        # Increment the molecule index.
        mol_index = mol_index + 1


def read(file=None, dir=None, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, sep=None):
    """Function for reading molecule, residue, and/or spin sequence data.

    @param file:            The name of the file to open.
    @type file:             str
    @param dir:             The directory containing the file (defaults to the current directory if
                            None).
    @type dir:              str or None
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    @param sep:             The column seperator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if sequence data already exists.
    if sequence_exists():
        raise RelaxSequenceError

    # Extract the data from the file.
    file_data = extract_data(file, dir)

    # Count the number of header lines.
    header_lines = 0
    for i in xrange(len(file_data)):
        # Residue number.
        if res_num_col != None:
            try:
                int(file_data[i][res_num_col])
            except ValueError:
                header_lines = header_lines + 1
            else:
                break

        # Spin number.
        elif spin_num_col != None:
            try:
                int(file_data[i][spin_num_col])
            except ValueError:
                header_lines = header_lines + 1
            else:
                break

    # Remove the header.
    file_data = file_data[header_lines:]

    # Strip data.
    file_data = strip(file_data)

    # Do nothing if the file does not exist.
    if not file_data:
        raise RelaxFileEmptyError

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the sequence data is valid.
    validate_sequence(file_data, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col)

    # Init some indecies.
    mol_index = 0
    res_index = 0

    # Fill the molecule-residue-spin data.
    for i in xrange(len(file_data)):
        # A new molecule.
        if mol_name_col and cdp.mol[mol_index].name != file_data[i][mol_name_col]:
            # Replace the first empty molecule.
            if mol_index == 0 and cdp.mol[0].name == None:
                cdp.mol[0].name = file_data[i][mol_name_col]

            # Create a new molecule.
            else:
                # Add the molecule.
                cdp.mol.add_item(mol_name=file_data[i][mol_name_col])

                # Increment the molecule index.
                mol_index = mol_index + 1

        # A new residue.
        if res_name_col and cdp.mol[mol_index].res[res_index].num != file_data[i][res_num_col]:
            # Replace the first empty residue.
            if res_index == 0 and cdp.mol[mol_index].res[0].name == None:
                cdp.mol[mol_index].res[0].name = file_data[i][res_name_col]
                cdp.mol[mol_index].res[0].num = int(file_data[i][res_num_col])

            # Create a new residue.
            else:
                # Add the residue.
                cdp.mol[mol_index].res.add_item(res_name=file_data[i][res_name_col], res_num=int(file_data[i][res_num_col]))

                # Increment the residue index.
                res_index = res_index + 1

        # A new spin.
        if spin_num_col:
            cdp.mol[mol_index].res[res_index].spin.add_item(spin_name=file_data[i][spin_name_col], spin_num=int(file_data[i][spin_num_col]))


def validate_sequence(data, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None):
    """Function for testing if the sequence data is valid.

    The only function this performs is to raise a RelaxError if the data is invalid.


    @param data:            The sequence data.
    @type data:             list of lists.
    @param mol_name_col:    The column containing the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column containing the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column containing the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column containing the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column containing the spin number information.
    @type spin_num_col:     int or None
    """

    # Loop over the data.
    for i in xrange(len(data)):
        # Molecule name data.
        if mol_name_col != None:
            try:
                data[i][mol_name_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

        # Residue number data.
        if res_num_col != None:
            # No data in column.
            try:
                data[i][res_num_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

            # Bad data in column.
            try:
                int(data[i][res_num_col])
            except ValueError:
                raise RelaxInvalidSeqError, data[i]

        # Residue name data.
        if res_name_col != None:
            try:
                data[i][res_name_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

        # Spin number data.
        if spin_num_col != None:
            # No data in column.
            try:
                data[i][spin_num_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]

            # Bad data in column.
            try:
                int(data[i][spin_num_col])
            except ValueError:
                raise RelaxInvalidSeqError, data[i]

        # Spin name data.
        if spin_name_col != None:
            try:
                data[i][spin_name_col]
            except IndexError:
                raise RelaxInvalidSeqError, data[i]


def write(file=None, dir=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None, force=0):
    """Function for writing molecule, residue, and/or sequence data.

    This calls the write_body() function to do most of the work.


    @param file:            The name of the file to write the data to.
    @type file:             str
    @param dir:             The directory to contain the file (defaults to the current directory if
                            None).
    @type dir:              str or None
    @param mol_name_col:    The column to contain the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column to contain the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column to contain the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column to contain the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column to contain the spin number information.
    @type spin_num_col:     int or None
    @param sep:             The column seperator which, if None, defaults to whitespace.
    @type sep:              str or None
    @param force:           A flag which if set to 1 will cause an existing file to be overwritten.
    @type force:            bin
    """

    # Test if the sequence data is loaded.
    if not count_spins():
        raise RelaxNoSequenceError

    # Open the file for writing.
    seq_file = open_write_file(file, dir, force)

    # Write the data.
    write_body(file=seq_file, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep)

    # Close the results file.
    seq_file.close()



def write_body(file=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, sep=None):
    """Function for writing to the given file object the molecule, residue, and/or sequence data.

    @param file:            The file object to write the data to.
    @type file:             file object
    @param mol_name_col:    The column to contain the molecule name information.
    @type mol_name_col:     int or None
    @param res_name_col:    The column to contain the residue name information.
    @type res_name_col:     int or None
    @param res_num_col:     The column to contain the residue number information.
    @type res_num_col:      int or None
    @param spin_name_col:   The column to contain the spin name information.
    @type spin_name_col:    int or None
    @param spin_num_col:    The column to contain the spin number information.
    @type spin_num_col:     int or None
    @param sep:             The column seperator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # No special seperator character.
    if sep == None:
        sep = ''

    # Write a header.
    if mol_name_col != None:
        file.write("%-10s " % ("Mol_name"+sep))
    if res_num_col != None:
        file.write("%-10s " % ("Res_num"+sep))
    if res_name_col != None:
        file.write("%-10s " % ("Res_name"+sep))
    if spin_num_col != None:
        file.write("%-10s " % ("Spin_num"+sep))
    if spin_name_col != None:
        file.write("%-10s " % ("Spin_name"+sep))
    file.write('\n')

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        if mol_name_col != None:
            file.write("%-10s " % (str(mol_name)+sep))
        if res_num_col != None:
            file.write("%-10s " % (str(res_num)+sep))
        if res_name_col != None:
            file.write("%-10s " % (str(res_name)+sep))
        if spin_num_col != None:
            file.write("%-10s " % (str(spin.num)+sep))
        if spin_name_col != None:
            file.write("%-10s " % (str(spin.name)+sep))
        file.write('\n')

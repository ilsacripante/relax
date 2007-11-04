###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

# relax module imports.
import help
from generic_fns import molecule
from relax_errors import RelaxBinError, RelaxIntError, RelaxNoneStrError, RelaxStrError


class Molecule:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the residue data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def create(self, mol_name=None):
        """Function for creating a new molecule.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        mol_name:  The name of the molecule.


        Description
        ~~~~~~~~~~~

        This function will add a new molecule data container to the relax data storage object.  The
        same molecule name cannot be used more than once.


        Examples
        ~~~~~~~~

        To create the molecules 'Ap4Aase', 'ATP', and 'MgF4', type:

        relax> molecule.create('Ap4Aase')
        relax> molecule.create('ATP')
        relax> molecule.create('MgF4')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "molecule.create("
            text = text + "mol_name=" + `mol_name` + ")"
            print text

        # Molecule name.
        if type(mol_name) != str:
            raise RelaxStrError, ('molecule name', mol_name)

        # Execute the functional code.
        molecule.create(mol_name=mol_name)


    def copy(self, run1=None, run2=None):
        """Function for copying the sequence from run1 to run2.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run1:  The name of the run to copy the sequence from.

        run2:  The name of the run to copy the sequence to.


        Description
        ~~~~~~~~~~~

        This function will copy the sequence from 'run1' to 'run2'.  'run1' must contain sequence
        information, while 'run2' must have no sequence loaded.


        Examples
        ~~~~~~~~

        To copy the sequence from the run 'm1' to the run 'm2', type:

        relax> sequence.copy('m1', 'm2')
        relax> sequence.copy(run1='m1', run2='m2')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.copy("
            text = text + "run1=" + `run1`
            text = text + ", run2=" + `run2` + ")"
            print text

        # The run1 argument.
        if type(run1) != str:
            raise RelaxStrError, ('run1', run1)

        # The run2 argument.
        if type(run2) != str:
            raise RelaxStrError, ('run2', run2)

        # Execute the functional code.
        self.__relax__.generic.sequence.copy(run1=run1, run2=run2)


    def delete(self, res_id=None):
        """Function for deleting residues.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        res_id:  The residue identifier string.


        Description
        ~~~~~~~~~~~

        This function can be used to delete a single or sets of residues.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "residue.delete("
            text = text + "res_id=" + `res_id` + ")"
            print text

        # The residue identifier argument.
        if type(res_id) != str:
            raise RelaxStrError, ('residue identifier', res_id)

        # Execute the functional code.
        residue.delete(res_id=res_id)


    def display(self, run=None):
        """Function for displaying the sequence.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "sequence.display("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.sequence.display(run=run)

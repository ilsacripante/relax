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

# Python module imports.
from re import match

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxInvalidError


# The relax data storage object.



class Nuclei:
    def __init__(self, relax):
        """Class containing the function to set the gyromagnetic ratio of the heteronucleus."""

        self.relax = relax


    def find_nucleus(self):
        """Function for finding the nucleus corresponding to 'relax_data_store.gx'."""

        # Not set.
        if not hasattr(relax_data_store, 'gx'):
            return

        # Nitrogen.
        if relax_data_store.gx == self.gn():
            return 'N'

        # Carbon
        if relax_data_store.gx == self.gc():
            return 'C'

        # Oxygen.
        if relax_data_store.gx == self.go():
            return 'O'

        # Phosphate.
        if relax_data_store.gx == self.gp():
            return 'P'


    def set_values(self, heteronuc):
        """Function for setting the gyromagnetic ratio of the heteronucleus."""

        # Nitrogen.
        if match('[Nn]', heteronuc):
            relax_data_store.gx = self.gn()

        # Carbon
        elif match('[Cc]', heteronuc):
            relax_data_store.gx = self.gc()

        # Oxygen.
        elif match('[Oo]', heteronuc):
            relax_data_store.gx = self.go()

        # Phosphate.
        elif match('[Pp]', heteronuc):
            relax_data_store.gx = self.gp()

        # Incorrect arguement.
        else:
            raise RelaxInvalidError, ('heteronucleus', heteronuc)

        # Set the proton gyromagnetic ratio.
        relax_data_store.gh = self.gh()

        # Calculate the ratio of the gyromagnetic ratios.
        relax_data_store.g_ratio = relax_data_store.gh / relax_data_store.gx

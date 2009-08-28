###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2009 Edward d'Auvergne                        #
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
from base_class import Basic_class
import generic_fns.reset


class Reset(Basic_class):
    """Class containing the function for reinitialising the relax data storage object."""

    def reset(self):
        """Reset relax.

        All of the data of the relax data storage object will be erased and hence relax will return
        to its initial state.
        """

        # Execute the functional code.
        generic_fns.reset.reset()

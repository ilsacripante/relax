###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""The relaxation data BMRB API interface."""


# relax module imports.
from bmrblib.kinetics.general_relaxation import GeneralRelaxationSaveframe
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESaveframe
from bmrblib.kinetics.heteronucl_NOEs_v3_1 import HeteronuclNOESaveframe_v3_1
from bmrblib.kinetics.heteronucl_T1_relaxation import HeteronuclT1Saveframe
from bmrblib.kinetics.heteronucl_T1_relaxation_v3_1 import HeteronuclT1Saveframe_v3_1
from bmrblib.kinetics.heteronucl_T2_relaxation import HeteronuclT2Saveframe
from bmrblib.kinetics.heteronucl_T2_relaxation_v3_1 import HeteronuclT2Saveframe_v3_1


class Relaxation:
    """Class for the relaxation data part of the BMRB API."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.__datanodes = datanodes

        # Initialise the kinetic saveframe supergroups.
        self.__heteronucl_NOEs = HeteronuclNOESaveframe(self.__datanodes)
        self.__heteronucl_T1_relaxation = HeteronuclT1Saveframe(self.__datanodes)
        self.__heteronucl_T2_relaxation = HeteronuclT2Saveframe(self.__datanodes)


class Relaxation_v3_0(Relaxation):
    """Class for the relaxation data part of the BMRB API (v3.0)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.__datanodes = datanodes

        # Initialise the kinetic saveframe supergroups.
        self.__heteronucl_NOEs = HeteronuclNOESaveframe_v3_0(self.__datanodes)
        self.__heteronucl_T1_relaxation = HeteronuclT1Saveframe_v3_0(self.__datanodes)
        self.__heteronucl_T2_relaxation = HeteronuclT2Saveframe_v3_0(self.__datanodes)



class Relaxation_v3_1(Relaxation_v3_0):
    """Class for the relaxation data part of the BMRB API (v3.1)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.__datanodes = datanodes

        # Initialise the kinetic saveframe supergroups.
        self.__heteronucl_NOEs = HeteronuclNOESaveframe_v3_1(self.__datanodes)
        self.__heteronucl_T1_relaxation = HeteronuclT1Saveframe_v3_1(self.__datanodes)
        self.__heteronucl_T2_relaxation = HeteronuclT2Saveframe_v3_1(self.__datanodes)


    def add(self, data_type=None, frq=None, res_nums=None, res_names=None, atom_names=None, isotope=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword data_type:     The relaxation data type (one of 'NOE', 'R1', or 'R2').
        @type data_type:        str
        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword isotope:       The isotope type list, ie 15 for '15N'.
        @type isotope:          list of int
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Pack specific the data.
        if data_type == 'R1':
            self.__heteronucl_T1_relaxation.add(frq=frq, res_nums=res_nums, res_names=res_names, atom_names=atom_names, isotope=isotope, data=data, errors=errors)
        elif data_type == 'R2':
            star.__heteronucl_T2_relaxation.add(frq=frq, res_nums=res_nums, res_names=res_names, atom_names=atom_names, isotope=isotope, data=data, errors=errors)
        elif data_type == 'NOE':
            star.__heteronucl_NOEs.add(frq=frq, res_nums=res_nums, res_names=res_names, atom_names=atom_names, isotope=isotope, data=data, errors=errors)


class Relaxation_v3_2(Relaxation_v3_1):
    """Class for the relaxation data part of the BMRB API (v3.2)."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.__datanodes = datanodes

        # Initialise the kinetic saveframe supergroups.
        self.__general_relaxation = GeneralRelaxationSaveframe(self.__datanodes)


    def add(self, data_type=None, frq=None, res_nums=None, res_names=None, atom_names=None, isotope=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword data_type:     The relaxation data type (one of 'NOE', 'R1', or 'R2').
        @type data_type:        str
        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword isotope:       The isotope type list, ie 15 for '15N'.
        @type isotope:          list of int
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Pack specific the data.
        if data_type in ['R1', 'R2']:
            self.__general_relaxation.add(data_type=data_type, frq=frq, res_nums=res_nums, res_names=res_names, atom_names=atom_names, isotope=isotope, data=data, errors=errors)
        elif data_type == 'NOE':
            star.__heteronucl_NOEs.add(frq=frq, res_nums=res_nums, res_names=res_names, atom_names=atom_names, isotope=isotope, data=data, errors=errors)



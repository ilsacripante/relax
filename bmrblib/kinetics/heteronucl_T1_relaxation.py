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
"""The Heteronuclear T1 data saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_T1_relaxation.
"""

# relax module imports.
from bmrblib.tag_category import TagCategory
from pystarlib.SaveFrame import SaveFrame
from pystarlib.TagTable import TagTable


class HeteronuclT1Saveframe:
    """The Heteronuclear T1 data saveframe class."""

    # Saveframe variables.
    label = 'T1'


    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of relaxation data sets.
        self.r1_inc = 0

        # The tag category objects.
        self.heteronuclT1list = HeteronuclT1List(self)
        self.heteronuclT1experiment = HeteronuclT1Experiment(self)
        self.heteronuclT1software = HeteronuclT1Software(self)


    def add(self, frq=None, res_nums=None, res_names=None, atom_names=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Place the args into the namespace.
        self.frq = frq
        self.res_nums = res_nums
        self.res_names = res_names
        self.atom_names = atom_names
        self.data = data
        self.errors = errors

        # Init.
        tag_cat = ''

        # Set up the R1 specific variables.
        self.r1_inc = self.r1_inc + 1
        ri_inc = self.r1_inc
        coherence = 'Nz'

        # Initialise the save frame.
        self.frame = SaveFrame(title='heteronuclear_'+self.label+'_list_'+`ri_inc`)

        # Create the tag categories.
        self.heteronuclT1list.create()
        self.heteronuclT1experiment.create()
        self.heteronuclT1software.create()

        # The relaxation tag names.
        tag_names = ['_Residue_seq_code', '_Residue_label', '_Atom_name', '_'+self.label+'_value', '_'+self.label+'_value_error']

        # Add the data.
        table = TagTable(tagnames=tag_names, tagvalues=[res_nums, res_names, atom_names, data, errors])

        # Add the tag table to the save frame.
        self.frame.tagtables.append(table)

        # Add the relaxation data save frame.
        self.datanodes.append(self.frame)



class HeteronuclT1List(TagCategory):
    """Base class for the HeteronuclT1List tag category."""

    # Tag category label.
    HeteronuclT1List = None

    # Tag names for the relaxation data.
    SfCategory = '_Saveframe_category'
    SampleConditionListLabel = '_Sample_conditions_label'
    SpectrometerFrequency1H = '_Spectrometer_frequency_1H'
    T1CoherenceType = '_T1_coherence_type'
    T1ValUnits = '_T1_value_units'

    # Class variables.
    coherence = 'Nz'


    def create(self):
        """Create the HeteronuclT1List tag category."""

        # Tag category label.
        tag_cat = ''
        if self.HeteronuclT1List:
            tag_cat = self.HeteronuclT1List + '.'

        # The save frame category.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SfCategory], tagvalues=[[self.sf.label+'_relaxation']]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SampleConditionListLabel], tagvalues=[['$conditions_1']]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SpectrometerFrequency1H], tagvalues=[[str(self.sf.frq/1e6)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.T1CoherenceType], tagvalues=[[self.coherence]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.T1ValUnits], tagvalues=[['1/s']]))



class HeteronuclT1Experiment(TagCategory):
    """Base class for the HeteronuclT1Experiment tag category."""

    # Tag category label.
    HeteronuclT1Experiment = None

    # Tag names for experiment setup.
    SampleLabel = '_Sample_label'


    def create(self, frame=None):
        """Create the HeteronuclT1Experiment tag category."""

        # Tag category label.
        tag_cat = ''
        if self.HeteronuclT1Experiment:
            tag_cat = self.HeteronuclT1Experiment + '.'

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SampleLabel], tagvalues=[['$sample_1']]))



class HeteronuclT1Software(TagCategory):
    """Base class for the HeteronuclT1Software tag category."""

    # Tag category label.
    HeteronuclT1Software = None


    def create(self):
        """Create the HeteronuclT1Software tag category."""

        # Tag category label.
        tag_cat = ''
        if self.HeteronuclT1Software:
            tag_cat = self.HeteronuclT1Software + '.'

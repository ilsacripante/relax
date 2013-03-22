###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
"""Module for the reading of Bruker Dynamics Centre (DC) files."""

# Python module imports.
from re import search, split

# relax module imports.
from generic_fns import pipes
from generic_fns import value
from generic_fns.exp_info import software_select
from generic_fns.mol_res_spin import exists_mol_res_spin_data, name_spin, set_spin_isotope, spin_loop
from generic_fns.relax_data import pack_data, peak_intensity_type
from lib.errors import RelaxError, RelaxNoSequenceError
from lib.io import open_read_file
from physical_constants import element_from_isotope


def convert_relax_data(data):
    """Determine the relaxation data from the given DC data.

    @param data:    The list of Tx, Tx error, and scaling factor for a given residue from the DC file.
    @type data:     list of str
    """

    # Convert the value from Tx to Rx.
    rx = 1.0 / float(data[0])

    # Remove the scaling.
    rx_err = float(data[1]) / float(data[2])

    # Convert the Tx error to an Rx error.
    rx_err = rx**2 * rx_err

    # Return the value and error.
    return rx, rx_err


def get_res_num(data):
    """Determine the residue number from the given DC data.

    @param data:    The list of residue info, split by whitespace, from the DC file.
    @type data:     list of str
    """

    # Init.
    res_num = None

    # Split the data.
    row = split('([0-9]+)', data)

    # Loop over the new list.
    for j in range(len(row)):
        try:
            res_num = int(row[j])
        except ValueError:
            pass

    # Return the value.
    return ":%s" % res_num


def read(ri_id=None, file=None, dir=None):
    """Read the DC data file and place all the data into the relax data store.

    @keyword ri_id: The relaxation data ID string.
    @type ri_id:    str
    @keyword file:  The name of the file to open.
    @type file:     str
    @keyword dir:   The directory containing the file (defaults to the current directory if None).
    @type dir:      str or None
    """

    # Test if the current pipe exists.
    pipes.test()

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Extract the data from the file.
    file_handle = open_read_file(file, dir)
    lines = file_handle.readlines()
    file_handle.close()

    # Init.
    values = []
    errors = []
    res_nums = []
    int_type = None

    # Loop over the data.
    in_ri_data = False
    for line in lines:
        # Split the line.
        row = split("\t", line)

        # Strip the rubbish.
        for j in range(len(row)):
            row[j] = row[j].strip()

        # Empty line.
        if len(row) == 0:
            continue

        # The DC version.
        if row[0] == 'generated by:':
            version = row[1]

        # Check for bad errors.
        if row[0] == 'Systematic error estimation of data:':
            # Badness.
            if row[1] == 'worst case per peak scenario':
                raise RelaxError("The errors estimation method \"worst case per peak scenario\" is not suitable for model-free analysis.  Please go back to the DC and switch to \"average variance calculation\".")

        # The data type.
        if row[0] == 'Project:':
            if search('T1', row[1]):
                ri_type = 'R1'
            elif search('T2', row[1]):
                ri_type = 'R2'
            elif search('NOE', row[1]):
                ri_type = 'NOE'

        # Get the frequency, converting to Hz.
        elif row[0] == 'Proton frequency[MHz]:':
            frq = float(row[1]) * 1e6

        # Inside the relaxation data section.
        elif row[0] == 'SECTION:' and row[1] == 'results':
            in_ri_data = True

        # The relaxation data.
        elif in_ri_data:
            # Skip the header.
            if row[0] == 'Peak name':
                # Catch old PDC files (to fix https://gna.org/bugs/?20152).
                pdc_file = False
                if ri_type == 'R1' and not search('R1', line):
                    pdc_file = True
                elif ri_type == 'R2' and not search('R2', line):
                    pdc_file = True
                if pdc_file:
                    raise RelaxError("The old Protein Dynamics Center (PDC) files are not supported")

                # Skip.
                continue

            # The residue info.
            res_nums.append(get_res_num(row[0]))

            # Get the relaxation data.
            if ri_type != 'NOE':
                #rx, rx_err = convert_relax_data(row[3:])
                rx = float(row[-2])
                rx_err = float(row[-1])
            else:
                rx = float(row[-3])
                rx_err = float(row[-2])

            # Append the data.
            values.append(rx)
            errors.append(rx_err)

        # The temperature.
        elif row[0] == 'Temperature (K):':
            # Set the value (not implemented yet).
            pass

        # The labelling.
        elif row[0] == 'Labelling:':
            # Store the isotope for later use.
            isotope = row[1]

            # Set the isotope value.
            set_spin_isotope(isotope=isotope, force=None)

            # Name the spins.
            name = split('([A-Z]+)', row[1])[1]
            name_spin(name=name, force=None)

        # The integration method.
        elif row[0] == 'Used integrals:':
            # Peak heights.
            if row[1] == 'peak intensities':
                int_type = 'height'

            # Peak volumes:
            if row[1] == 'area integral':
                int_type = 'volume'

    # Modify the residue numbers by adding the heteronucleus name.
    atom_name = element_from_isotope(isotope)
    for i in range(len(res_nums)):
        res_nums[i] += '@' + atom_name

    # Pack the data.
    pack_data(ri_id, ri_type, frq, values, errors, spin_ids=res_nums)

    # Set the integration method.
    peak_intensity_type(ri_id=ri_id, type=int_type)

    # Set the DC as used software.
    software_select('Bruker DC', version=version)

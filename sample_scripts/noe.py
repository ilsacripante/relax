###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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

# Script for calculating NOEs.
##############################


# Create the NOE data pipe.
pipe.create('NOE', 'noe')

# Load the backbone amide 15N spins from a PDB file.
structure.read_pdb('Ap4Aase_new_3.pdb')
structure.load_spins(spin_id='@N')

# Load the reference spectrum and saturated spectrum peak intensities.
noe.read(file='ref.list', spectrum_type='ref')
noe.read(file='sat.list', spectrum_type='sat')

# Set the errors.
noe.error(error=3600, spectrum_type='ref')
noe.error(error=3000, spectrum_type='sat')

# Individual residue errors.
noe.error(error=122000, spectrum_type='ref', res_num=114)
noe.error(error=8500, spectrum_type='sat', res_num=114)

# Deselect unresolved residues.
deselect.read(file='unresolved')

# Calculate the NOEs.
calc()

# Save the NOEs.
value.write(param='noe', file='noe.out', force=True)

# Create grace files.
grace.write(y_data_type='ref', file='ref.agr', force=True)
grace.write(y_data_type='sat', file='sat.agr', force=True)
grace.write(y_data_type='noe', file='noe.agr', force=True)

# View the grace files.
grace.view(file='ref.agr')
grace.view(file='sat.agr')
grace.view(file='noe.agr')

# Write the results.
results.write(file='results', dir=None, force=True)

# Save the program state.
state.save('save', force=True)

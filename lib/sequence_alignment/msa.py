###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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
"""Multiple sequence alignment (MSA) algorithms."""

# Python module imports.
from numpy import float64, int16, zeros
import sys

# relax module imports.
from lib.errors import RelaxError
from lib.sequence_alignment.align_protein import align_pairwise


def central_star(sequences, algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=1.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0):
    """Align multiple protein sequences to one reference by fusing multiple pairwise alignments.

    @param sequences:                   The list of residue sequences as one letter codes.
    @type sequences:                    list of str
    @keyword algorithm:                 The pairwise sequence alignment algorithm to use.
    @type algorithm:                    str
    @keyword matrix:                    The substitution matrix to use.
    @type matrix:                       str
    @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
    @type gap_open_penalty:             float
    @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
    @type gap_extend_penalty:           float
    @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
    @type end_gap_open_penalty:         float
    @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
    @type end_gap_extend_penalty:       float
    @return:                            The list of alignment strings and the gap matrix.
    @rtype:                             list of str, numpy rank-2 int array
    """

    # Initialise.
    N = len(sequences)
    scores = zeros((N, N), float64)

    # Set up lists of lists for storing all alignment strings.
    align1_matrix = []
    align2_matrix = []
    for i in range(N):
        align1_matrix.append([])
        align2_matrix.append([])
        for j in range(N):
            if i == j:
                align1_matrix[i].append(sequences[i])
                align2_matrix[i].append(sequences[i])
            else:
                align1_matrix[i].append(None)
                align2_matrix[i].append(None)

    # Printout.
    sys.stdout.write("\nCentral Star multiple sequence alignment.\n\n")
    sys.stdout.write("%-30s %s\n" % ("Pairwise algorithm:", algorithm))
    sys.stdout.write("%-30s %s\n" % ("Substitution matrix:", matrix))
    sys.stdout.write("%-30s %s\n" % ("Gap opening penalty:", gap_open_penalty))
    sys.stdout.write("%-30s %s\n" % ("Gap extend penalty:", gap_extend_penalty))
    sys.stdout.write("Initial sequences:\n")
    for i in range(N):
        sys.stdout.write("%3i %s\n" % (i+1, sequences[i]))

    # All pairwise alignments.
    sys.stdout.write("\nDetermining the scores for all pairwise alignments:\n")
    for i in range(N):
        for j in range(i+1, N):
            # Align the pair.
            sys.stdout.write("%-30s " % ("Sequences %i-%i:" % (i+1, j+1)))
            score, align1, align2, gaps = align_pairwise(sequences[i], sequences[j], algorithm=algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty, verbosity=0)
            sys.stdout.write("%10.1f\n" % score)

            # Store the score and alignment strings.
            scores[i, j] = scores[j, i] = score
            align1_matrix[i][j] = align1_matrix[j][i] = align1
            align2_matrix[i][j] = align2_matrix[j][i] = align2

    # The central sequence.
    sys.stdout.write("\nDetermining the central sequence:\n")
    sum_scores = scores.sum(0)
    Sc_sum_score = 1e100
    Sc_index = 0
    for i in range(N):
        if sum_scores[i] < Sc_sum_score:
            Sc_sum_score = sum_scores[i]
            Sc_index = i
        sys.stdout.write("%-30s %10.1f\n" % (("Sum of scores, sequence %i:" % (i+1)), sum_scores[i]))
    sys.stdout.write("%-30s %i\n" % ("Central sequence:", Sc_index+1))

    # Partition the sequences.
    Sc = sequences[Sc_index]
    Si = []
    for i in range(N):
        if i != Sc_index:
            Si.append(sequences[i])

    # Optimal alignments.
    sys.stdout.write("\nDetermining the iterative optimal alignments:\n")
    Sc_prime = Sc
    string_lists = []
    for i in range(N-1):
        # Update the string lists.
        string_lists.append([])

        # Perform the pairwise alignment between Sc' and Si, replacing all '-' with 'X'.
        score, Sc_prime, Si_prime, gaps = align_pairwise(Sc_prime.replace('-', 'X'), Si[i].replace('-', 'X'), algorithm=algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty, verbosity=0)
        sys.stdout.write("\n%-30s %s\n" % ("Sequence Sc':", Sc_prime.replace('X', '-')))
        sys.stdout.write("%-30s %s\n" % (("Sequence S%i':" % (i+1)), Si_prime.replace('X', '-')))

        # Store the Si alignment.
        for j in range(len(Sc_prime)):
            string_lists[i].append(Si_prime[j])

        # Add spaces to the lists for all previous alignments.
        else:
            # Find gaps in the central sequence.
            for j in range(len(Sc_prime)):
                if Sc_prime[j] == '-':
                    # Pad the previous alignments.
                    for k in range(0, i):
                        string_lists[k].insert(j, '-')

    # Rebuild the alignment lists and create a gap matrix.
    strings = []
    M = len(Sc_prime)
    strings.append(Sc_prime)
    for i in range(N-1):
        strings.append(''.join(string_lists[i]))
    for i in range(N):
        strings[i] = strings[i].replace('X', '-')

    # Restore the original sequence ordering.
    string = strings.pop(0)
    strings.insert(Sc_index, string)

    # Create the gap matrix.
    gaps = zeros((N, M), int16)
    for i in range(N):
        for j in range(M):
            if strings[i][j] == '-':
                gaps[i, j] = 1

    # Final printout.
    sys.stdout.write("\nFinal MSA:\n")
    for i in range(N):
        sys.stdout.write("%3i %s\n" % (i+1, strings[i]))

    # Return the results.
    return strings, gaps


def msa_general(sequences, residue_numbers=None, msa_algorithm='Central Star', pairwise_algorithm='NW70', matrix='BLOSUM62', gap_open_penalty=1.0, gap_extend_penalty=1.0, end_gap_open_penalty=0.0, end_gap_extend_penalty=0.0):
    """General interface for multiple sequence alignments (MSA).

    This can be used to select between the following MSA algorithms:

        - 'Central Star', to use the central_star() function.
        - 'residue number', to use the msa_residue_numbers() function.


    @param sequences:                   The list of residue sequences as one letter codes.
    @type sequences:                    list of str
    @keyword residue_numbers:           The list of residue numbers for each sequence.
    @type residue_numbers:              list of list of int
    @keyword msa_algorithm:             The multiple sequence alignment (MSA) algorithm to use.
    @type msa_algorithm:                str
    @keyword pairwise_algorithm:        The pairwise sequence alignment algorithm to use.
    @type pairwise_algorithm:           str
    @keyword matrix:                    The substitution matrix to use.
    @type matrix:                       str
    @keyword gap_open_penalty:          The penalty for introducing gaps, as a positive number.
    @type gap_open_penalty:             float
    @keyword gap_extend_penalty:        The penalty for extending a gap, as a positive number.
    @type gap_extend_penalty:           float
    @keyword end_gap_open_penalty:      The optional penalty for opening a gap at the end of a sequence.
    @type end_gap_open_penalty:         float
    @keyword end_gap_extend_penalty:    The optional penalty for extending a gap at the end of a sequence.
    @type end_gap_extend_penalty:       float
    @return:                            The list of alignment strings and the gap matrix.
    @rtype:                             list of str, numpy rank-2 int array
    """

    # Check the MSA algorithm.
    allowed_msa = ['Central Star', 'residue number']
    if msa_algorithm not in allowed_msa:
        raise RelaxError("The MSA algorithm must be one of %s." % allowed_msa)

    # Check the penalty arguments.
    if gap_open_penalty != None:
        if gap_open_penalty < 0.0:
            raise RelaxError("The gap opening penalty %s must be a positive number." % gap_open_penalty)
    if gap_extend_penalty != None:
        if gap_extend_penalty < 0.0:
            raise RelaxError("The gap extension penalty %s must be a positive number." % gap_extend_penalty)
    if end_gap_open_penalty != None:
        if end_gap_open_penalty < 0.0:
            raise RelaxError("The end gap opening penalty %s must be a positive number." % end_gap_open_penalty)
    if end_gap_extend_penalty != None:
        if end_gap_extend_penalty < 0.0:
            raise RelaxError("The end gap extension penalty %s must be a positive number." % end_gap_extend_penalty)

    # Use the central star multiple alignment algorithm.
    if msa_algorithm == 'Central Star':
        strings, gaps = central_star(sequences, algorithm=pairwise_algorithm, matrix=matrix, gap_open_penalty=gap_open_penalty, gap_extend_penalty=gap_extend_penalty, end_gap_open_penalty=end_gap_open_penalty, end_gap_extend_penalty=end_gap_extend_penalty)

    # Alignment by residue number.
    elif msa_algorithm == 'residue number':
        strings, gaps = msa_residue_numbers(sequences, residue_numbers=residue_numbers)

    # Return the alignment strings and gap matrix.
    return strings, gaps


def msa_residue_numbers(sequences, residue_numbers=None):
    """Align multiple sequences based on the residue numbering.

    @param sequences:                   The list of residue sequences as one letter codes.
    @type sequences:                    list of str
    @keyword residue_numbers:           The list of residue numbers for each sequence.
    @type residue_numbers:              list of list of int
    @return:                            The list of alignment strings and the gap matrix.
    @rtype:                             list of str, numpy rank-2 int array
    """

    # Initialise.
    N = len(sequences)
    strings = []
    for i in range(N):
        strings.append('')

    # Printout.
    sys.stdout.write("\nResidue number based multiple sequence alignment.\n\n")
    sys.stdout.write("Initial sequences:\n")
    for i in range(N):
        sys.stdout.write("%3i %s\n" % (i+1, sequences[i]))

    # The maximum and minimum residue numbers.
    res_min = 1e100
    res_max = -1e100
    for i in range(N):
        if min(residue_numbers[i]) < res_min:
            res_min = min(residue_numbers[i])
        if max(residue_numbers[i]) > res_max:
            res_max = max(residue_numbers[i])

    # The total number of residues.
    M = res_max - res_min + 1

    # Loop over the molecules and residues and determine if the residue is present.
    for i in range(N):
        for res_num in range(res_min, res_max+1):
            # The residue is present.
            if res_num in residue_numbers[i]:
                index = residue_numbers[i].index(res_num)
                strings[i] += sequences[i][index]

            # A gap.
            else:
                strings[i] += '-'

    # Create the gap matrix.
    gaps = zeros((N, M), int16)
    for i in range(N):
        for j in range(M):
            if strings[i][j] == '-':
                gaps[i, j] = 1

    # Final printout.
    sys.stdout.write("\nFinal MSA:\n")
    for i in range(N):
        sys.stdout.write("%3i %s\n" % (i+1, strings[i]))

    # Return the results.
    return strings, gaps


def msa_residue_skipping(strings=None, gaps=None):
    """Create the residue skipping data structure. 

    @keyword strings:   The list of alignment strings.
    @type strings:      list of str
    @keyword gaps:      The gap matrix.
    @type gaps:         numpy rank-2 int array
    @return:            The residue skipping data structure.  The first dimension is the molecule and the second is the residue.  As opposed to zero, a value of one means the residue should skipped.
    @rtype:             list of lists of int
    # 
    """

    # initialise.
    skip = []
    num_mols = len(strings)

    # Loop over each molecule.
    for mol_index in range(num_mols):
        skip.append([])
        for i in range(len(strings[0])):
            # Create the empty residue skipping data structure.
            if strings == None:
                skip[mol_index].append(0)
                continue

            # No residue in the current sequence.
            if gaps[mol_index][i]:
                continue

            # A gap in one of the other sequences.
            gap = False
            for mol_index2 in range(num_mols):
                if gaps[mol_index2][i]:
                    gap = True

            # Skip the residue.
            if gap:
                skip[mol_index].append(1)
            else:
                skip[mol_index].append(0)

    # Return the data structure.
    return skip

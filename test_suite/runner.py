###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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

# Import the test suite categories.
from system_tests.main import System_tests
from unit_tests.unit_test_runner import Run_unit_tests


class Test_suite_runner:
    """Class for running all components of the relax test suite.

    This currently includes the following categories of tests:
        System/functional tests.
        Unit tests.
    """

    def __init__(self, relax):
        """Run the system/functional and unit test suite components.

        @param relax:   The relax namespace.
        @type relax:    instance
        """

        self.relax = relax

        # Execute the system/functional tests.
        system_result = System_tests(self.relax)

        # Execute the unit tests.
        runner = Run_unit_tests()
        unit_result = runner.run()

        # Print out a summary of the test suite.
        ########################################

        # Heading.
        print "\n\n\n"
        print "###################################"
        print "# Summary of the relax test suite #"
        print "###################################"

        # System/functional tests.
        print "System/functional tests: " + `system_result`

        # Unit tests.
        print "Unit tests: " + `unit_result`

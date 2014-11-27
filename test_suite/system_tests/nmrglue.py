##############################################################################
#                                                                             #
# Copyright (C) 2011-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Python module imports.
from os import sep
from tempfile import mkdtemp, NamedTemporaryFile

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase
from extern import nmrglue


class Nmrglue(SystemTestCase):
    """TestCase class for the functionality of the external module nmrglue.
    This is from U{Task #7873<https://gna.org/task/index.php?7873>}: Write wrapper function to nmrglue, to read .ft2 files and process them."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')

        # Create a temporary directory for dumping files.
        ds.tmpdir = mkdtemp()

        # Create path to nmrglue test data.
        ds.ng_test = status.install_path +sep+ 'extern' +sep+ 'nmrglue' +sep+ 'nmrglue_0_4' +sep+ 'tests' +sep+ 'pipe_proc_tests'


    def test_nmrglue_read(self):
        """Test the userfunction spectrum.nmrglue_read."""

        # Read the spectrum.
        fname = 'freq_real.ft2'
        sp_id = 'test'
        self.interpreter.spectrum.nmrglue_read(file=fname, dir=ds.ng_test, spectrum_id=sp_id)

        # Test that the spectrum id has been stored.
        self.assertEqual(cdp.spectrum_ids[0], sp_id)

        # Extract the data.
        dic  = cdp.ngdata[sp_id].dic
        udic  = cdp.ngdata[sp_id].udic
        data = cdp.ngdata[sp_id].data

        # Test the data.
        self.assertEqual(udic[0]['label'], '15N')
        self.assertEqual(udic[1]['label'], '13C')
        self.assertEqual(udic[0]['freq'], True)
        self.assertEqual(udic[1]['freq'], True)
        self.assertEqual(udic[0]['size'], 512)
        self.assertEqual(udic[1]['size'], 4096)


    def test_version(self):
        """Test version of nmrglue."""

        # Test version.
        ng_vers = nmrglue.__version__
        print("Version of nmrglue is %s"%ng_vers)

        # Assert the version to be 0.4.
        self.assertEqual(ng_vers, '0.4')

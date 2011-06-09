###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
"""Module containing the base class for the automatic NOE analysis frames."""

# Python module imports.
from os import sep
from string import replace
import sys
import thread
import time
import wx

# relax module imports.
from auto_analyses.noe import NOE_calc
from data import Relax_data_store; ds = Relax_data_store()
from relax_io import DummyFileObject
from status import Status; status = Status()

# relaxGUI module imports.
from gui.analyses.base import Base_frame
from gui.analyses.results_analysis import color_code_noe
from gui.base_classes import Container
from gui.controller import Redirect_text, Thread_container
from gui.derived_wx_classes import StructureTextCtrl
from gui.filedialog import opendir, openfile
from gui.message import error_message, missing_data
from gui.paths import IMAGE_PATH
from gui.settings import load_sequence



class Auto_noe(Base_frame):
    """The base class for the noe frames."""

    # Hardcoded variables.
    analysis_type = None
    bitmap = None
    label = None

    def __init__(self, gui, notebook, hardcoded_index=None):
        """Build the automatic NOE analysis GUI frame elements.

        @param gui:                 The main GUI class.
        @type gui:                  gui.relax_gui.Main instance
        @param notebook:            The notebook to pack this frame into.
        @type notebook:             wx.Notebook instance
        @keyword hardcoded_index:   Kludge for the current GUI layout.
        @type hardcoded_index:      int
        """

        # Store the main class.
        self.gui = gui

        # The NOE image
        self.bitmap = IMAGE_PATH + 'noe.png'

        # Alias the storage container in the relax data store.
        self.data = ds.relax_gui.analyses[hardcoded_index]

        # The parent GUI element for this class.
        self.parent = wx.Panel(notebook, -1)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        main_box = self.build_main_box()
        self.parent.SetSizer(main_box)


    def add_execute_relax(self, box):
        """Create and add the relax execution GUI element to the given box.

        @param box:     The box element to pack the relax execution GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # A horizontal sizer for the contents.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        label.SetMinSize((118, 17))
        label.SetFont(self.gui.font_normal)
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.BitmapButton(self.parent, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        button.SetName('hello')
        button.SetSize(button.GetBestSize())
        self.gui.Bind(wx.EVT_BUTTON, self.execute, button)
        sizer.Add(button, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALIGN_RIGHT, 0)


    def assemble_data(self):
        """Assemble the data required for the Auto_noe class.

        See the docstring for auto_analyses.relax_fit for details.  All data is taken from the relax data store, so data upload from the GUI to there must have been previously performed.

        @return:    A container with all the data required for the auto-analysis, i.e. its keyword arguments seq_args, file_names, relax_times, int_method, mc_num.  Also a flag stating if the data is complete and a list of missing data types.
        @rtype:     class instance, bool, list of str
        """

        # The data container and flag.
        data = Container()
        complete = True
        missing = []

        # The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        if hasattr(self.data, 'sequence_file'):
            data.seq_args = [self.data.sequence_file, None, None, 1, None, None, None, None]
        else:
            data.seq_args = None

        # Reference peak list and background noe.
        data.ref_file = self.data.ref_file
        if not data.ref_file:
            complete = False
            missing.append('Reference peak list')
        data.ref_rmsd = int(self.data.ref_rmsd)

        # Saturated peak list and background noe.
        data.sat_file = self.data.sat_file
        if not data.sat_file:
            complete = False
            missing.append('Saturated peak list')
        data.sat_rmsd = int(self.data.sat_rmsd)

        # Results directory.
        data.save_dir = self.data.save_dir

        # Filename.
        data.filename = 'noe.' + str(self.field_nmr_frq.GetValue()) + '.out'

        # The integration method.
        data.int_method = 'height'

        # Import golbal settings.
        global_settings = ds.relax_gui.global_setting

        # Hetero nucleus name.
        data.heteronuc = global_settings[2]

        # Proton name.
        data.proton = global_settings[3]

        # Unresolved spins.
        file = DummyFileObject()
        entries = self.data.unresolved
        entries = replace(entries, ',', '\n')
        file.write(entries)
        file.close()
        data.unresolved = file

        # Structure file.
        if hasattr(self.data, 'structure_file') and self.data.structure_file != self.gui.structure_file_pdb_msg:
            data.structure_file = self.data.structure_file
        else:
            data.structure_file = None

        # Set Structure file as None if a sequence file is loaded.
        if data.structure_file == '!!! Sequence file selected !!!':
            data.structure_file = None

        # No sequence data.
        if not data.seq_args and not data.structure_file:
            complete = False
            missing.append('Sequence data files (text or PDB)')

        # Return the container, flag, and list of missing data.
        return data, complete, missing


    def build_main_box(self):
        """Construct the highest level box to pack into the automatic NOE analysis frame.

        @return:    The main box element containing all Rx GUI elements to pack directly into the automatic Rx analysis frame.
        @rtype:     wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        box = wx.BoxSizer(wx.HORIZONTAL)

        # Add the model-free bitmap picture.
        self.bitmap_1_copy_copy = wx.StaticBitmap(self.parent, -1, wx.Bitmap(self.bitmap, wx.BITMAP_TYPE_ANY))
        box.Add(self.bitmap_1_copy_copy, 0, wx.ADJUST_MINSIZE, 10)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 0, 0, 0)

        # Return the box.
        return box


    def build_right_box(self):
        """Construct the right hand box to pack into the main NOE box.

        @return:    The right hand box element containing all NOE GUI elements (excluding the bitmap) to pack into the main Rx box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_title(box, "Setup for steady-state NOE analysis")

        # Add the frequency selection GUI element.
        self.field_nmr_frq = self.add_text_sel_element(box, self.parent, text="NMR Frequency [MHz]", default=str(self.data.frq), width_text=230, width_control=350, width_button=103)

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self.parent, text="Results directory", default=self.data.save_dir, width_text=230, width_control=350, width_button=103, fn=self.results_directory, button=True)

        # Add the sequence file selection GUI element.
        self.field_sequence = self.add_text_sel_element(box, self.parent, text="Sequence file", default=str(self.gui.sequence_file_msg), width_text=230, width_control=350, width_button=103, fn=self.load_sequence, editable=False, button=True)

        # Add the structure file selection GUI element.
        self.field_structure = self.add_text_sel_element(box, self.parent, text="Sequence from PDB structure file", default=self.gui.structure_file_pdb_msg, control=StructureTextCtrl, width_text=230, width_control=350, width_button=103, fn='open_file', editable=False, button=True)

        # Add the unresolved spins GUI element.
        self.field_unresolved = self.add_text_sel_element(box, self.parent, text="Unresolved residues", width_text=230, width_control=350, width_button=103)

        # Add peak list selection header.
        self.add_subtitle(box, "NOE peak lists")

        # Add the saturated NOE peak list selection GUI element.
        self.field_sat_noe = self.add_text_sel_element(box, self.parent, text="Saturated NOE peak list", default=self.data.sat_file, width_text=230, width_control=350, width_button=103, fn=self.sat_file, button=True)

        # Add the saturated RMSD background GUI element:
        self.field_sat_rmsd = self.add_text_sel_element(box, self.parent, text="Baseplane RMSD", default=str(self.data.sat_rmsd), width_text=230, width_control=350, width_button=103)

        # Add the reference NOE peak list selection GUI element.
        self.field_ref_noe = self.add_text_sel_element(box, self.parent, text="Reference NOE peak list", default=self.data.ref_file, width_text=230, width_control=350, width_button=103, fn=self.ref_file, button=True)

        # Add the reference RMSD background GUI element:
        self.field_ref_rmsd = self.add_text_sel_element(box, self.parent, text="Baseplane RMSD", default=str(self.data.ref_rmsd), width_text=230, width_control=350, width_button=103)

        # Add the execution GUI element.
        self.add_execute_relax(box)

        # Return the box.
        return box


    def execute(self, event):
        """Set up, execute, and process the automatic Rx analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # relax execution lock.
        status = Status()
        if status.exec_lock.locked():
            error_message("relax is currently executing.", "relax execution lock")
            event.Skip()
            return

        # Synchronise the frame data to the relax data store.
        self.sync_ds(upload=True)

        # Display the relax controller (if not debugging).
        if not status.debug:
            self.gui.controller.Show()

        # Start the thread (if not debugging).
        if status.debug:
            self.execute_thread()
        else:
            id = thread.start_new_thread(self.execute_thread, ())

        # Terminate the event.
        event.Skip()


    def execute_thread(self):
        """Execute the calculation in a thread."""

        # Controller.
        if not status.debug:
            # Redirect relax output and errors to the controller.
            redir = Redirect_text(self.gui.controller)
            sys.stdout = redir
            sys.stderr = redir

            # Print a header in the controller.
            header = 'Starting NOE calculation'
            underline = '-' * len(header)
            wx.CallAfter(self.gui.controller.log_panel.AppendText, (header+'\n\n'))
            time.sleep(0.5)

        # Assemble all the data needed for the auto-analysis.
        data, complete, missing = self.assemble_data()

        # Incomplete.
        if not complete:
            print 'Aborting NOE caclulation as the following informations are missing:\n'
            for i in range(len(missing)):
                print '\t'+missing[i]
            print ''
            return

        # Execute.
        NOE_calc(seq_args=data.seq_args, pipe_name='noe'+'_'+str(time.asctime(time.localtime())), noe_ref=data.ref_file, noe_ref_rmsd=data.ref_rmsd, noe_sat=data.sat_file, noe_sat_rmsd=data.sat_rmsd, unresolved=data.unresolved, pdb_file=data.structure_file, output_file=data.filename, results_dir=data.save_dir, int_method='height', heteronuc=data.heteronuc, proton=data.proton, heteronuc_pdb='@N')

        # Feedback about success.
        if not status.debug:
            wx.CallAfter(self.gui.controller.log_panel.AppendText, '\n\n__________________________________________________________\n\nSuccessfully calculated NOE values\n__________________________________________________________')

        # Add noe grace plot to results list.
        self.gui.list_noe.Append(data.save_dir+sep+'grace'+sep+'noe.agr')

        # Add noe grace plot to relax data store.
        ds.relax_gui.results_noe.append(data.save_dir+sep+'grace'+sep+'noe.agr')

        # Create color coded structure pymol macro.
        color_code_noe(self, data.save_dir, data.structure_file)

        # add macro to results tab
        self.gui.list_noe.Append(data.save_dir+sep+'noe.pml')

        # Add noe macro to relax data store.
        ds.relax_gui.results_noe.append(data.save_dir+sep+'noe.pml')


    def load_sequence(self, event):
        """The sequence loading GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Select the file.
        file = load_sequence()

        # Nothing selected.
        if file == None:
            return

        # Store the file.
        self.data.sequence_file = file

        # Sync.
        self.sync_ds(upload=False)

        # Terminate the event.
        event.Skip()


    def link_data(self, data):
        """Re-alias the storage container in the relax data store.

        @keyword data:      The data storage container.
        @type data:         class instance
        """

        # Re-alias.
        self.data = data


    def ref_file(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original directory.
        backup = self.field_ref_noe.GetValue()

        # Select the file.
        self.data.ref_file = openfile('Select reference NOE peak list', directory=self.field_ref_noe.GetValue(), default = 'all files (*.*)|*')

        # Restore the backup file if no file was chosen.
        if not self.data.ref_file:
            self.data.ref_file = backup

        # Place the path in the text box.
        self.field_ref_noe.SetValue(self.data.ref_file)

        # Terminate the event.
        event.Skip()


    def results_directory(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original directory.
        backup = self.field_results_dir.GetValue()

        # Select the file.
        self.data.save_dir = opendir('Select results directory', default=self.field_results_dir.GetValue())

        # Restore the backup file if no file was chosen.
        if not self.data.save_dir:
            self.data.save_dir = backup

        # Place the path in the text box.
        self.field_results_dir.SetValue(self.data.save_dir)

        # Terminate the event.
        event.Skip()


    def sat_file(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original directory.
        backup = self.field_sat_noe.GetValue()

        # Select the file.
        self.data.sat_file = openfile('Select saturated NOE peak list', directory=self.field_sat_noe.GetValue(), default = 'all files (*.*)|*')

        # Restore the backup file if no file was chosen.
        if not self.data.sat_file:
            self.data.sat_file = backup

        # Place the path in the text box.
        self.field_sat_noe.SetValue(self.data.sat_file)

        # Terminate the event.
        event.Skip()


    def sync_ds(self, upload=False):
        """Synchronise the noe analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The frequency.
        if upload:
            self.data.frq = str(self.field_nmr_frq.GetValue())
        else:
            self.field_nmr_frq.SetValue(str(self.data.frq))

        # The results directory.
        if upload:
            self.data.save_dir = str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str(self.data.save_dir))

        # The sequence file.
        if upload:
            file = str(self.field_sequence.GetValue())
            if file != self.gui.sequence_file_msg:
                self.data.sequence_file = str(self.field_sequence.GetValue())
        elif hasattr(self.data, 'sequence_file'):
            self.field_sequence.SetValue(str(self.data.sequence_file))

        # The structure file.
        if upload:
            file = str(self.field_structure.GetValue())
            if file != self.gui.structure_file_pdb_msg:
                self.data.structure_file = str(self.field_structure.GetValue())
        elif hasattr(self.data, 'structure_file'):
            self.field_structure.SetValue(str(self.data.structure_file))

        # Unresolved residues.
        if upload:
            self.data.unresolved = str(self.field_unresolved.GetValue())
        elif hasattr(self.data, 'unresolved'):
            self.field_unresolved.SetValue(str(self.data.unresolved))

        # Reference peak file.
        if upload:
            self.data.ref_file = str(self.field_ref_noe.GetValue())
        elif hasattr(self.data, 'ref_file'):
            self.field_ref_noe.SetValue(str(self.data.ref_file))

        # Reference rmsd.
        if upload:
            self.data.ref_rmsd = str(self.field_ref_rmsd.GetValue())
        elif hasattr(self.data, 'ref_rmsd'):
            self.field_ref_rmsd.SetValue(str(self.data.ref_rmsd))

        # Saturated peak file.
        if upload:
            self.data.sat_file = str(self.field_sat_noe.GetValue())
        elif hasattr(self.data, 'sat_file'):
            self.field_sat_noe.SetValue(str(self.data.sat_file))

        # Saturated rmsd.
        if upload:
            self.data.sat_rmsd = str(self.field_sat_rmsd.GetValue())
        elif hasattr(self.data, 'sat_rmsd'):
            self.field_sat_rmsd.SetValue(str(self.data.sat_rmsd))

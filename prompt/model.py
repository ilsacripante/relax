###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

import sys

import help


class Model:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for holding the preset model functions."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def create_mf(self, run=None, model=None, equation=None, params=None, scaling=1, res_num=None):
        """Function to create a model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        model:  The name of the model-free model.

        equation:  The model-free equation.

        params:  The array of parameter names of the model.

        scaling:  The diagonal scaling flag.

        res_num:  The residue number.


        Description
        ~~~~~~~~~~~

        Model-free equation.

        'mf_orig' selects the original model-free equations with parameters {S2, te}.
        'mf_ext' selects the extended model-free equations with parameters {S2f, tf, S2, ts}.
        'mf_ext2' selects the extended model-free equations with parameters {S2f, tf, S2s, ts}.


        Model-free parameters.

        The following parameters are accepted for the original model-free equation:
            S2:     The square of the generalised order parameter.
            te:     The effective correlation time.
        The following parameters are accepted for the extended model-free equation:
            S2f:    The square of the generalised order parameter of the faster motion.
            tf:     The effective correlation time of the faster motion.
            S2:     The square of the generalised order parameter S2 = S2f*S2s.
            ts:     The effective correlation time of the slower motion.
        The following parameters are accepted for the extended 2 model-free equation:
            S2f:    The square of the generalised order parameter of the faster motion.
            tf:     The effective correlation time of the faster motion.
            S2s:    The square of the generalised order parameter of the slower motion.
            ts:     The effective correlation time of the slower motion.
        The following parameters are accepted for all equations:
            Rex:    The chemical exchange relaxation.
            r:      The average bond length <r>.
            CSA:    The chemical shift anisotropy.


        Diagonal scaling.

        This is the scaling of parameter values with the intent of having the same order of
        magnitude for all parameters values.  For example, if S2 = 0.5, te = 200 ps, and
        Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18]
        (Rex is divided by (2*pi*600,000,000)**2 to make it field strength independent).  The
        scaling vector for this model is [1.0, 1e-10, 1/(2*pi*6*1e8)**2].  By dividing the unscaled
        parameter vector by the scaling vector the scaled parameter vector is [0.5, 2.0, 15.0].  To
        revert to the original unscaled parameter vector, the scaled parameter vector and scaling
        vector are multiplied.  The reason for diagonal scaling is that certain minimisation
        techniques fail when the model is not properly scaled.


        Residue number.

        If 'res_num' is supplied as an integer then the model will only be created for that residue,
        otherwise the model will be created for all residues.


        Examples
        ~~~~~~~~

        The following commands will create the model-free model 'm1' which is based on the original
        model-free equation and contains the single parameter 'S2'.

        relax> model.create_mf('m1', 'm1', 'mf_orig', ['S2'])
        relax> model.create_mf(run='m1', model='m1', params=['S2'], equation='mf_orig')


        The following commands will create the model-free model 'large_model' which is based on the
        extended model-free equation and contains the seven parameters 'S2f', 'tf', 'S2', 'ts',
        'Rex', 'CSA', 'r'.

        relax> model.create_mf('test', 'large_model', 'mf_ext', ['S2f', 'tf', 'S2', 'ts', 'Rex',
                               'CSA', 'r'])
        relax> model.create_mf(run='test', model='large_model', params=['S2f', 'tf', 'S2', 'ts',
                               'Rex', 'CSA', 'r'], equation='mf_ext')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "model.create_mf("
            text = text + "run=" + `run`
            text = text + ", model=" + `model`
            text = text + ", equation=" + `equation`
            text = text + ", params=" + `params`
            text = text + ", scaling=" + `scaling`
            text = text + ", res_num=" + `res_num` + ")"
            print text

        # Run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Equation.
        if type(equation) != str:
            raise RelaxStrError, ('model-free equation', equation)

        # Parameter types.
        if type(params) != list:
            raise RelaxListError, ('parameter types', params)
        for i in xrange(len(params)):
            if type(params[i]) != str:
                raise RelaxListStrError, ('parameter types', params)

        # Scaling.
        if type(scaling) != int or (scaling != 0 and scaling != 1):
            raise RelaxBinError, ('scaling', scaling)

        # Residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Execute the functional code.
        self.__relax__.specific.model_free.create(run=run, model=model, equation=equation, params=params, scaling=scaling, res_num=res_num)


    def select_mf(self, run=None, model=None, scaling=1, res_num=None):
        """Function for the selection of a preset model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        model:  The name of the preset model.

        scaling:  The diagonal scaling flag.


        Description
        ~~~~~~~~~~~

        The preset model-free models are:
            'm0'    => []
            'm1'    => [S2]
            'm2'    => [S2, te]
            'm3'    => [S2, Rex]
            'm4'    => [S2, te, Rex]
            'm5'    => [S2f, S2, ts]
            'm6'    => [S2f, tf, S2, ts]
            'm7'    => [S2f, S2, ts, Rex]
            'm8'    => [S2f, tf, S2, ts, Rex]
            'm9'    => [Rex]

            'm10'   => [CSA]
            'm11'   => [CSA, S2]
            'm12'   => [CSA, S2, te]
            'm13'   => [CSA, S2, Rex]
            'm14'   => [CSA, S2, te, Rex]
            'm15'   => [CSA, S2f, S2, ts]
            'm16'   => [CSA, S2f, tf, S2, ts]
            'm17'   => [CSA, S2f, S2, ts, Rex]
            'm18'   => [CSA, S2f, tf, S2, ts, Rex]
            'm19'   => [CSA, Rex]

            'm20'   => [r]
            'm21'   => [r, S2]
            'm22'   => [r, S2, te]
            'm23'   => [r, S2, Rex]
            'm24'   => [r, S2, te, Rex]
            'm25'   => [r, S2f, S2, ts]
            'm26'   => [r, S2f, tf, S2, ts]
            'm27'   => [r, S2f, S2, ts, Rex]
            'm28'   => [r, S2f, tf, S2, ts, Rex]
            'm29'   => [r, CSA, Rex]

            'm30'   => [r, CSA]
            'm31'   => [r, CSA, S2]
            'm32'   => [r, CSA, S2, te]
            'm33'   => [r, CSA, S2, Rex]
            'm34'   => [r, CSA, S2, te, Rex]
            'm35'   => [r, CSA, S2f, S2, ts]
            'm36'   => [r, CSA, S2f, tf, S2, ts]
            'm37'   => [r, CSA, S2f, S2, ts, Rex]
            'm38'   => [r, CSA, S2f, tf, S2, ts, Rex]
            'm39'   => [r, CSA, Rex]

        Warning:  The models in the thirties range fail when using standard R1, R2, and NOE
        relaxation data.  This is due to the extreme flexibly of these models where a change in the
        parameter 'r' is compensated by a corresponding change in the parameter 'CSA' and
        vice versa.


        Additional preset model-free models, which are simply extensions of the above models with
        the addition of a local tm parameter are:
            'tm0'   => [tm]
            'tm1'   => [tm, S2]
            'tm2'   => [tm, S2, te]
            'tm3'   => [tm, S2, Rex]
            'tm4'   => [tm, S2, te, Rex]
            'tm5'   => [tm, S2f, S2, ts]
            'tm6'   => [tm, S2f, tf, S2, ts]
            'tm7'   => [tm, S2f, S2, ts, Rex]
            'tm8'   => [tm, S2f, tf, S2, ts, Rex]
            'tm9'   => [tm, Rex]

            'tm10'  => [tm, CSA]
            'tm11'  => [tm, CSA, S2]
            'tm12'  => [tm, CSA, S2, te]
            'tm13'  => [tm, CSA, S2, Rex]
            'tm14'  => [tm, CSA, S2, te, Rex]
            'tm15'  => [tm, CSA, S2f, S2, ts]
            'tm16'  => [tm, CSA, S2f, tf, S2, ts]
            'tm17'  => [tm, CSA, S2f, S2, ts, Rex]
            'tm18'  => [tm, CSA, S2f, tf, S2, ts, Rex]
            'tm19'  => [tm, CSA, Rex]

            'tm20'  => [tm, r]
            'tm21'  => [tm, r, S2]
            'tm22'  => [tm, r, S2, te]
            'tm23'  => [tm, r, S2, Rex]
            'tm24'  => [tm, r, S2, te, Rex]
            'tm25'  => [tm, r, S2f, S2, ts]
            'tm26'  => [tm, r, S2f, tf, S2, ts]
            'tm27'  => [tm, r, S2f, S2, ts, Rex]
            'tm28'  => [tm, r, S2f, tf, S2, ts, Rex]
            'tm29'  => [tm, r, CSA, Rex]

            'tm30'  => [tm, r, CSA]
            'tm31'  => [tm, r, CSA, S2]
            'tm32'  => [tm, r, CSA, S2, te]
            'tm33'  => [tm, r, CSA, S2, Rex]
            'tm34'  => [tm, r, CSA, S2, te, Rex]
            'tm35'  => [tm, r, CSA, S2f, S2, ts]
            'tm36'  => [tm, r, CSA, S2f, tf, S2, ts]
            'tm37'  => [tm, r, CSA, S2f, S2, ts, Rex]
            'tm38'  => [tm, r, CSA, S2f, tf, S2, ts, Rex]
            'tm39'  => [tm, r, CSA, Rex]



        Diagonal scaling.

        This is the scaling of parameter values with the intent of having the same order of
        magnitude for all parameters values.  For example, if S2 = 0.5, te = 200 ps, and
        Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18]
        (Rex is divided by (2*pi*600,000,000)**2 to make it field strength independent).  The
        scaling vector for this model is [1.0, 1e-10, 1/(2*pi*6*1e8)**2].  By dividing the unscaled
        parameter vector by the scaling vector the scaled parameter vector is [0.5, 2.0, 15.0].  To
        revert to the original unscaled parameter vector, the scaled parameter vector and scaling
        vector are multiplied.  The reason for diagonal scaling is that certain minimisation
        techniques fail when the model is not properly scaled.


        Residue number.

        If 'res_num' is supplied as an integer then the model will only be selected for that
        residue, otherwise the model will be selected for all residues.



        Examples
        ~~~~~~~~

        To pick model 'm1' for all selected residues and assign it to the run 'mixed', type:

        relax> model.select_mf('mixed', 'm1')
        relax> model.select_mf(run='mixed', model='m1', scaling=1)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "model.select_mf("
            text = text + "run=" + `run`
            text = text + ", model=" + `model`
            text = text + ", scaling=" + `scaling` + ")"
            print text

        # Run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Model argument.
        elif type(model) != str:
            raise RelaxStrError, ('model', model)

        # Scaling.
        if type(scaling) != int or (scaling != 0 and scaling != 1):
            raise RelaxBinError, ('scaling', scaling)

        # Residue number.
        if res_num != None and type(res_num) != int:
            raise RelaxNoneIntError, ('residue number', res_num)

        # Execute the functional code.
        self.__relax__.specific.model_free.select(run=run, model=model, scaling=scaling, res_num=res_num)

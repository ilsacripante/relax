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


from Numeric import Float64, zeros



############################
# Spectral density values. #
############################


# Original {tm} and {tm, S2}.
#############################

def calc_tm_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the original model-free formula with
    the single parameter {tm} or the parameters {tm, S2}.

    The model-free formula for the parameter {tm} is:

                      _n_
                 2    \           /      1       \ 
        J(w)  =  - S2  >  ci . ti | ------------ |
                 5    /__         \ 1 + (w.ti)^2 /
                      i=m

    Calculations which are replicated in the gradient equations are:

        w_ti_sqrd = (w.ti)^2
        fact_ti = 1 / (1 + (w.ti)^2)
    """

    data.w_ti_sqrd = data.frq_sqrd_list * data.ti ** 2
    data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)



# Original {S2, te}.
####################

def calc_S2_te_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the original model-free formula with
    the parameters {S2, te}.

    The model-free formula is:

                    _n_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation)

        te_ti = te + ti
        te_ti_te = (te + ti).te


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation)

        one_s2 = 1 - S2

        te_ti_sqrd = (te + ti)^2
        w_te_ti_sqrd = (w.te.ti)^2
        inv_te_denom = 1 / ((te + ti)^2 + (w.te.ti)^2)
    """

    data.one_s2 = 1.0 - params[data.s2_index]

    data.te_ti = params[data.te_index] + data.ti
    data.te_ti_te = data.te_ti * params[data.te_index]
    data.te_ti_sqrd = data.te_ti ** 2
    data.w_te_ti_sqrd = data.w_ti_sqrd * params[data.te_index] ** 2
    data.inv_te_denom = 1.0 / (data.te_ti_sqrd + data.w_te_ti_sqrd)



# Original {tm, S2, te}.
########################

def calc_tm_S2_te_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the original model-free formula with
    the parameters {tm, S2, te}.

    The model-free formula is:

                    _n_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2

        te_ti = te + ti
        te_ti_te = (te + ti).te


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)

        one_s2 = 1 - S2

        te_ti_sqrd = (te + ti)^2
        w_te_ti_sqrd = (w.te.ti)^2
        inv_te_denom = 1 / ((te + ti)^2 + (w.te.ti)^2)
    """

    data.w_ti_sqrd = data.frq_sqrd_list * data.ti ** 2
    data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)

    data.one_s2 = 1.0 - params[data.s2_index]

    data.te_ti = params[data.te_index] + data.ti
    data.te_ti_te = data.te_ti * params[data.te_index]
    data.te_ti_sqrd = data.te_ti ** 2
    data.w_te_ti_sqrd = data.w_ti_sqrd * params[data.te_index] ** 2
    data.inv_te_denom = 1.0 / (data.te_ti_sqrd + data.w_te_ti_sqrd)



# Extended {S2f, S2, ts}.
#########################

def calc_S2f_S2_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, S2, ts}.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation)

        ts_ti = ts + ti
        ts_ti_ts = (ts + ti).ts


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation)

        s2f_s2 = S2f - S2

        ts_ti_sqrd = (ts + ti)^2
        w_ts_ti_sqrd = (w.ts.ti)^2
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2)
    """

    data.s2f_s2 = params[data.s2f_index] - params[data.s2_index]

    data.ts_ti = params[data.ts_index] + data.ti
    data.ts_ti_ts = data.ts_ti * params[data.ts_index]
    data.ts_ti_sqrd = data.ts_ti ** 2
    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_index] ** 2
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)



# Extended {tm, S2f, S2, ts}.
#############################

def calc_tm_S2f_S2_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {tm, S2f, S2, ts}.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2

        ts_ti = ts + ti
        ts_ti_ts = (ts + ti).ts


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)

        s2f_s2 = S2f - S2

        ts_ti_sqrd = (ts + ti)^2
        w_ts_ti_sqrd = (w.ts.ti)^2
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2)
    """

    data.w_ti_sqrd = data.frq_sqrd_list * data.ti ** 2
    data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)

    data.s2f_s2 = params[data.s2f_index] - params[data.s2_index]

    data.ts_ti = params[data.ts_index] + data.ti
    data.ts_ti_ts = data.ts_ti * params[data.ts_index]
    data.ts_ti_sqrd = data.ts_ti ** 2
    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_index] ** 2
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, S2s, ts}.

    The model-free formula is:

                       _n_
                 2     \           /      S2s           (1 - S2s)(ts + ti)ts    \ 
        J(w)  =  - S2f  >  ci . ti | ------------  +  ------------------------- |
                 5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation)

        ts_ti = ts + ti
        ts_ti_ts = (ts + ti).ts


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation)

        one_s2s = 1 - S2s

        ts_ti_sqrd = (ts + ti)^2
        w_ts_ti_sqrd = (w.ts.ti)^2
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2)
    """

    data.one_s2s = 1.0 - params[data.s2s_index]

    data.ts_ti = params[data.ts_index] + data.ti
    data.ts_ti_ts = data.ts_ti * params[data.ts_index]
    data.ts_ti_sqrd = data.ts_ti ** 2
    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_index] ** 2
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)



# Extended {S2f, tf, S2, ts}.
#############################

def calc_S2f_tf_S2_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, tf, S2, ts}.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation)

        tf_ti = tf + ti
        ts_ti = ts + ti
        tf_ti_tf = (tf + ti).tf
        ts_ti_ts = (ts + ti).ts


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation)

        one_s2f = 1 - S2f
        s2f_s2 = S2f - S2

        tf_ti_sqrd = (tf + ti)^2
        ts_ti_sqrd = (ts + ti)^2
        w_tf_ti_sqrd = (w.tf.ti)^2
        w_ts_ti_sqrd = (w.ts.ti)^2
        inv_tf_denom = 1 / ((tf + ti)^2 + (w.tf.ti)^2)
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2)
    """

    data.one_s2f = 1.0 - params[data.s2f_index]
    data.s2f_s2 = params[data.s2f_index] - params[data.s2_index]

    data.tf_ti = params[data.tf_index] + data.ti
    data.ts_ti = params[data.ts_index] + data.ti
    data.tf_ti_tf = data.tf_ti * params[data.tf_index]
    data.ts_ti_ts = data.ts_ti * params[data.ts_index]
    data.tf_ti_sqrd = data.tf_ti ** 2
    data.ts_ti_sqrd = data.ts_ti ** 2
    data.w_tf_ti_sqrd = data.w_ti_sqrd * params[data.tf_index] ** 2
    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_index] ** 2
    data.inv_tf_denom = 1.0 / (data.tf_ti_sqrd + data.w_tf_ti_sqrd)
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)



# Extended {tm, S2f, tf, S2, ts}.
#################################

def calc_tm_S2f_tf_S2_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {tm, S2f, tf, S2, ts}.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2

        tf_ti = tf + ti
        ts_ti = ts + ti
        tf_ti_tf = (tf + ti).tf
        ts_ti_ts = (ts + ti).ts


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)

        one_s2f = 1 - S2f
        s2f_s2 = S2f - S2

        tf_ti_sqrd = (tf + ti)^2
        ts_ti_sqrd = (ts + ti)^2
        w_tf_ti_sqrd = (w.tf.ti)^2
        w_ts_ti_sqrd = (w.ts.ti)^2
        inv_tf_denom = 1 / ((tf + ti)^2 + (w.tf.ti)^2)
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2)
    """

    data.w_ti_sqrd = data.frq_sqrd_list * data.ti ** 2
    data.fact_ti = 1.0 / (1.0 + data.w_ti_sqrd)

    data.one_s2f = 1.0 - params[data.s2f_index]
    data.s2f_s2 = params[data.s2f_index] - params[data.s2_index]

    data.tf_ti = params[data.tf_index] + data.ti
    data.ts_ti = params[data.ts_index] + data.ti
    data.tf_ti_tf = data.tf_ti * params[data.tf_index]
    data.ts_ti_ts = data.ts_ti * params[data.ts_index]
    data.tf_ti_sqrd = data.tf_ti ** 2
    data.ts_ti_sqrd = data.ts_ti ** 2
    data.w_tf_ti_sqrd = data.w_ti_sqrd * params[data.tf_index] ** 2
    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_index] ** 2
    data.inv_tf_denom = 1.0 / (data.tf_ti_sqrd + data.w_tf_ti_sqrd)
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, tf, S2s, ts}.

    The model-free formula is:

                    _n_
                 2  \           /   S2f . S2s        (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m

    Replicated calculations are:

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation)

        tf_ti = tf + ti
        ts_ti = ts + ti
        tf_ti_tf = (tf + ti).tf
        ts_ti_ts = (ts + ti).ts


    Calculations which are replicated in the gradient equations are:

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation)

        one_s2s = 1 - S2s
        one_s2f = 1 - S2f
        s2f_s2 = S2f(1 - S2s) = S2f - S2

        tf_ti_sqrd = (tf + ti)^2
        ts_ti_sqrd = (ts + ti)^2
        w_tf_ti_sqrd = (w.tf.ti)^2
        w_ts_ti_sqrd = (w.ts.ti)^2
        inv_tf_denom = 1 / ((tf + ti)^2 + (w.tf.ti)^2)
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2)
    """

    data.one_s2s = 1.0 - params[data.s2s_index]
    data.one_s2f = 1.0 - params[data.s2f_index]
    data.s2f_s2 = params[data.s2f_index] * data.one_s2s

    data.tf_ti = params[data.tf_index] + data.ti
    data.ts_ti = params[data.ts_index] + data.ti
    data.tf_ti_tf = data.tf_ti * params[data.tf_index]
    data.ts_ti_ts = data.ts_ti * params[data.ts_index]
    data.tf_ti_sqrd = data.tf_ti ** 2
    data.ts_ti_sqrd = data.ts_ti ** 2
    data.w_tf_ti_sqrd = data.w_ti_sqrd * params[data.tf_index] ** 2
    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_index] ** 2
    data.inv_tf_denom = 1.0 / (data.tf_ti_sqrd + data.w_tf_ti_sqrd)
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)




###############################
# Spectral density gradients. #
###############################


# Original {tm} and {tm, S2}.
#############################

def calc_tm_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the original model-free formula
    with the single parameter {tm} or the parameters {tm, S2}.

    Replicated calculations are:

                           1 - (w.ti)^2
        fact_djw_dti  =  ----------------
                         (1 + (w.ti)^2)^2
    """

    data.fact_djw_dti = (1.0 - data.w_ti_sqrd) * data.fact_ti**2



# Original {S2, te}.
####################

def calc_S2_te_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the original model-free formula
    with the parameters {S2, te}.

    Replicated calculations are:

                                (te + ti)^2 - (w.te.ti)^2
        fact_djw_dte  =  ti^2 -----------------------------
                              ((te + ti)^2 + (w.te.ti)^2)^2
    """

    data.fact_djw_dte = data.ti ** 2 * (data.te_ti_sqrd - data.w_te_ti_sqrd) * data.inv_te_denom ** 2



# Original {tm, S2, te}.
########################

def calc_tm_S2_te_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the original model-free formula
    with the parameters tm, S2, and te.

    Replicated calculations are:

                       (te + tm)^2 - (w.te.tm)^2
        fact_djw  =  -----------------------------
                     ((te + tm)^2 + (w.te.tm)^2)^2

                            1 - (w.tm)^2
        fact1_djw_dtm  =  ----------------
                          (1 + (w.tm)^2)^2

                                 (te + tm)^2 - (w.te.tm)^2
        fact2_djw_dtm  =  te^2 -----------------------------
                               ((te + tm)^2 + (w.te.tm)^2)^2

                         2        (te + tm)^2 - (w.te.tm)^2
        fact_djw_dte  =  - tm^2 -----------------------------
                         5      ((te + tm)^2 + (w.te.tm)^2)^2
    """

    # tm.
    data.fact1_djw_dtm = (1.0 - data.w_ti_sqrd) * data.fact_ti**2

    # te.
    data.fact_djw = (data.te_tm_sqrd - data.w_te_tm_sqrd) * data.inv_te_denom ** 2
    data.fact2_djw_dtm = params[data.te_index]**2 * data.fact_djw
    data.fact_djw_dte = data.two_fifths_tm_sqrd * data.fact_djw



# Extended {S2f, S2, ts}.
#########################

def calc_S2f_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters S2f, S2, and ts.

    Replicated calculations are:


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom ** 2



# Extended {tm, S2f, S2, ts}.
#############################

def calc_tm_S2f_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters S2f, S2, and ts.

    Replicated calculations are:

                       (ts + tm)^2 - (w.ts.tm)^2
        fact_djw  =  -----------------------------
                     ((ts + tm)^2 + (w.ts.tm)^2)^2


                            1 - (w.tm)^2
        fact1_djw_dtm  =  ----------------
                          (1 + (w.tm)^2)^2


                                 (ts + tm)^2 - (w.ts.tm)^2
        fact2_djw_dtm  =  ts^2 -----------------------------
                               ((ts + tm)^2 + (w.ts.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    # tm.
    data.fact1_djw_dtm = (1.0 - data.w_ti_sqrd) * data.fact_ti**2

    # ts.
    data.fact_djw = (data.ts_tm_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom ** 2
    data.fact2_djw_dtm = params[data.ts_index]**2 * data.fact_djw
    data.fact_djw_dts = data.two_fifths_tm_sqrd * data.fact_djw



# Extended {S2f, tf, S2, ts}.
#############################

def calc_S2f_tf_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters S2f, tf, S2, and ts.

    Replicated calculations are:

                         2        (tf + tm)^2 - (w.tf.tm)^2
        fact_djw_dtf  =  - tm^2 -----------------------------
                         5      ((tf + tm)^2 + (w.tf.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    data.fact_djw_dtf = data.two_fifths_tm_sqrd * (data.tf_tm_sqrd - data.w_tf_ti_sqrd) * data.inv_tf_denom ** 2
    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom ** 2



# Extended {tm, S2f, tf, S2, ts}.
#################################

def calc_tm_S2f_tf_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters tm, S2f, tf, S2, and ts.

    Replicated calculations are:

                        (tf + tm)^2 - (w.tf.tm)^2
        fact2_djw  =  -----------------------------
                      ((tf + tm)^2 + (w.tf.tm)^2)^2


                        (ts + tm)^2 - (w.ts.tm)^2
        fact3_djw  =  -----------------------------
                      ((ts + tm)^2 + (w.ts.tm)^2)^2


                            1 - (w.tm)^2
        fact1_djw_dtm  =  ----------------
                          (1 + (w.tm)^2)^2


                                 (tf + tm)^2 - (w.tf.tm)^2
        fact2_djw_dtm  =  tf^2 -----------------------------
                               ((tf + tm)^2 + (w.tf.tm)^2)^2


                                 (ts + tm)^2 - (w.ts.tm)^2
        fact3_djw_dtm  =  ts^2 -----------------------------
                               ((ts + tm)^2 + (w.ts.tm)^2)^2


                         2        (tf + tm)^2 - (w.tf.tm)^2
        fact_djw_dtf  =  - tm^2 -----------------------------
                         5      ((tf + tm)^2 + (w.tf.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    # tm.
    data.fact1_djw_dtm = (1.0 - data.w_ti_sqrd) * data.fact_ti**2

    # tf.
    data.fact2_djw = (data.tf_tm_sqrd - data.w_tf_ti_sqrd) * data.inv_tf_denom ** 2
    data.fact2_djw_dtm = params[data.tf_index]**2 * data.fact2_djw
    data.fact_djw_dtf = data.two_fifths_tm_sqrd * data.fact2_djw

    # ts.
    data.fact3_djw = (data.ts_tm_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom ** 2
    data.fact3_djw_dtm = params[data.ts_index]**2 * data.fact3_djw
    data.fact_djw_dts = data.two_fifths_tm_sqrd * data.fact3_djw



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters S2f, S2s, and ts.

    Replicated calculations are:

                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2


                          2    /      1                 (ts + tm).ts        \ 
        fact_djw_ds2s  =  - tm | ------------  -  ------------------------- |
                          5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom ** 2
    data.fact_djw_ds2s = data.two_fifths_tm * (data.fact_ti - data.ts_tm_ts * data.inv_ts_denom)



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters S2f, tf, S2s, and ts.

    Replicated calculations are:

                         2        (tf + tm)^2 - (w.tf.tm)^2
        fact_djw_dtf  =  - tm^2 -----------------------------
                         5      ((tf + tm)^2 + (w.tf.tm)^2)^2


                         2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts  =  - tm^2 -----------------------------
                         5      ((ts + tm)^2 + (w.ts.tm)^2)^2


                          2    /      1                 (ts + tm).ts        \ 
        fact_djw_ds2s  =  - tm | ------------  -  ------------------------- |
                          5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    data.fact_djw_dtf = data.two_fifths_tm_sqrd * (data.tf_tm_sqrd - data.w_tf_ti_sqrd) * data.inv_tf_denom ** 2
    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom ** 2
    data.fact_djw_ds2s = data.two_fifths_tm * (data.fact_ti - data.ts_tm_ts * data.inv_ts_denom)

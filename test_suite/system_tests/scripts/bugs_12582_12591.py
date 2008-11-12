"""This system test catches 2 bugs submitted by Chris Brosey.

The bugs include:
    - Bug #12582 (https://gna.org/bugs/index.php?12582).
    - Bug #12591 (https://gna.org/bugs/index.php?12591).
"""

# Python module imports.
import sys


# Path of the files.
path = sys.path[-1] + '/test_suite/shared_data/model_free/S2_0.970_te_2048_Rex_0.149'

# Loop over the models.
for name in ['tm0', 'tm1']:
    # Setup.
    pipe.create(pipe_name=name, pipe_type='mf')
    sequence.read(file='noe.500.out', dir=path, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, sep=None)
    relax_data.read(ri_label='R1', frq_label='500', frq=500208000.0, file='r1.500.out', dir=path, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None)
    relax_data.read(ri_label='R2', frq_label='500', frq=500208000.0, file='r2.500.out', dir=path, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None)
    relax_data.read(ri_label='NOE', frq_label='500', frq=500208000.0, file='noe.500.out', dir=path, mol_name_col=None, res_num_col=0, res_name_col=1, spin_num_col=None, spin_name_col=None, data_col=2, error_col=3, sep=None)
    value.set(val=1.0200000000000001e-10, param='bond_length', spin_id=None)
    value.set(val=-0.00017199999999999998, param='csa', spin_id=None)
    value.set(val='15N', param='heteronucleus', spin_id=None)
    value.set(val='1H', param='proton', spin_id=None)
    model_free.select_model(model=name, spin_id=None)

    # Optimisation.
    grid_search(lower=None, upper=None, inc=11, constraints=True, verbosity=1)
    minimise('newton', func_tol=1e-25, max_iterations=10000000, constraints=True, scaling=True, verbosity=1)

    # Results writing.
    results.write(file='devnull', force=True, compress_type=1)

# Model selection.
sequence.display()
eliminate(function=None, args=None)
model_selection(method='AIC', modsel_pipe='aic', pipes=['tm0', 'tm1'])

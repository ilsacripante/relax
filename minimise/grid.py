import sys
from Numeric import Float64, ones, copy, zeros
from re import match

def grid(func, grid_ops, args=(), print_flag=0):
	"""Grid search function.


	Function options
	~~~~~~~~~~~~~~~~

	func		- The function to minimise.
	grid_ops	- Matrix of options for the grid search.
	args		- The tuple of arguments to supply to the function func.

	The first dimension of grid_ops corresponds to the parameters of the function func, and the second dimension corresponds to:
		0 - The number of increments.
		1 - Lower limit.
		2 - Upper limit.


	Returned objects
	~~~~~~~~~~~~~~~~

	The parameter vector corresponding to the minimum function value.
	The minimum function value.

	"""

	# Initialise data structures.
	num_params = len(grid_ops)
	total_steps = 1.0
	step_num = ones((num_params))
	step_size = zeros((num_params), Float64)
	params = zeros((num_params), Float64)
	min_params = zeros((num_params), Float64)
	for k in range(num_params):
		step_size[k] = (grid_ops[k][2] - grid_ops[k][1]) / (grid_ops[k][0] - 1)
		params[k] = grid_ops[k][1]
		min_params[k] = grid_ops[k][1]
		total_steps = total_steps * grid_ops[k][0]

	# Back calculate the initial function value.
	f = apply(func, (params,)+args)
	f_min = f

	# Debugging code.
	if print_flag >= 1:
		print "\n%-23s%-20i\n" % ("Total number of steps:", total_steps)
		if print_flag == 2:
			print "%-20s%-20s\n" % ("Step size:", `step_size`)
		print "%-6s%-8i%-12s%-20s" % ("Step:", 1, "Min params:", `params`)
		if print_flag == 2:
			print "%-20s%-20i" % ("Step number:", 1)
			print "%-20s%-20s" % ("Increment:", `step_num`)
			print "%-20s%-20s" % ("Init params:", `params`)
			print "%-20s%-20g\n" % ("Init f:", f)

	# Grid search.
	for step in range(2, total_steps + 1):
		# Loop over the parameters.
		for k in range(num_params):
			if step_num[k] < grid_ops[k][0]:
				step_num[k] = step_num[k] + 1
				params[k] = params[k] + step_size[k]
				# Exit so that the other step numbers are not incremented.
				break
			else:
				step_num[k] = 1
				params[k] = grid_ops[k][1]

		# Back calculate the current function value.
		f = apply(func, (params,)+args)

		# Test if the current function value is less than the least function value.
		if f < f_min:
			f_min = f
			min_params = copy.deepcopy(params)

			# Debugging code.
			if print_flag >= 1:
				print "%-6s%-8i%-12s%-65s%-16s%-20s" % ("Step:", step, "Min params:", `min_params`, "Function value:", `f_min`)

		# Debugging code.
		if print_flag == 2:
			print "%-20s%-20i" % ("Step number:", step)
			print "%-20s%-20s" % ("Increment:", `step_num`)
			print "%-20s%-20s" % ("Params:", `params`)
			print "%-20s%-20g" % ("Function value:", f)
			print "%-20s%-20s" % ("Min params:", `min_params`)
			print "%-20s%-20g\n" % ("Min f:", f_min)

	return min_params, f_min

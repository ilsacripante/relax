# A method based on cross-validation model selection.
#
# This implements one-item-out cross-validation.
#
# The program is divided into the following stages:
#    Stage 1:  Creation of the files for the model-free calculations for models 1 to 5.  For each model,
#        a directory for each relaxation data set is created without including the data.  Monte Carlo
#        simulations are not used on these initial runs, because the errors are not needed (should
#        speed up analysis considerably).
#    Stage 2:  Model selection and the creation of the final run.  Monte Carlo simulations are used to
#        find errors.  This stage has the option of optimizing the diffusion tensor along with the
#        model-free parameters.
#    Stage 3:  Extraction of the data.

import sys
from re import match

from common_ops import Common_operations


class CV(Common_operations):
    def __init__(self, relax):
        """Model-free analysis based on cross-validation model selection methods."""

        self.relax = relax


    def extract_mf_data(self):
        """Extract the model-free results."""

        for model in self.relax.data.runs:
            print "Extracting model-free data of model " + model
            for i in range(self.relax.data.num_ri):
                cv_dir = model + "/" + model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]
                cv_model = model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]
                print "\t" + cv_dir + "/mfout."
                mfout = self.relax.file_ops.read_file(cv_dir + '/mfout')
                mfout_lines = mfout.readlines()
                mfout.close()
                num_res = len(self.relax.data.relax_data[0])
                self.relax.data.data[cv_model] = self.relax.star.extract(mfout_lines, num_res, self.relax.usr_param.chi2_lim, self.relax.usr_param.ftest_lim, ftest='n', sims='n')


    def fill_results(self, data, model='0'):
        """Initialise the next row of the results data structure."""

        results = {}
        results['res_num']   = data['res_num']
        results['model']   = model
        results['s2']      = ''
        results['s2_err']  = ''
        results['s2f']     = ''
        results['s2f_err'] = ''
        results['s2s']     = ''
        results['s2s_err'] = ''
        results['te']      = ''
        results['te_err']  = ''
        results['rex']     = ''
        results['rex_err'] = ''
        results['chi2']     = ''
        return results


    def model_selection(self):
        """Model selection."""

        data = self.relax.data.data
        self.relax.data.calc_frq()
        self.relax.data.calc_constants()
        tm = float(self.relax.usr_param.tm['val']) * 1e-9

        if self.relax.debug:
            self.relax.log.write("\n\n<<< " + self.relax.usr_param.method + " model selection >>>\n\n")

        for res in range(len(self.relax.data.relax_data[0])):
            sys.stdout.write("%9s" % "Residue: ")
            sys.stdout.write("%-9s" % (self.relax.data.relax_data[0][res][1] + " " + self.relax.data.relax_data[0][res][0]))
            self.relax.data.cv.cv_crit.append({})
            self.relax.data.results.append({})

            if self.relax.debug:
                self.relax.log.write('%-22s\n' % ( "Checking res " + data["m1-"+self.relax.data.frq_label[self.relax.data.remap_table[0]]+"_"+self.relax.data.data_types[0]][res]['res_num'] ))

            for model in self.relax.data.runs:
                sum_cv_crit = 0

                if self.relax.debug:
                    self.relax.log.write(model + "\n")

                for i in range(self.relax.data.num_ri):
                    cv_model = model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]

                    real = [ float(self.relax.data.relax_data[i][res][2]) ]
                    err = [ float(self.relax.data.relax_data[i][res][3]) ]
                    types = [ [self.relax.data.data_types[i], float(self.relax.data.frq[self.relax.data.remap_table[i]])] ]

                    if match('m1', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ data[cv_model][res]['s2'] ])
                    elif match('m2', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ data[cv_model][res]['s2'], data[cv_model][res]['te'] ])
                    elif match('m3', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ data[cv_model][res]['s2'], data[cv_model][res]['rex'] ])
                    elif match('m4', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ data[cv_model][res]['s2'], data[cv_model][res]['te'], data[cv_model][res]['rex'] ])
                    elif match('m5', model):
                        back_calc = self.relax.calc_relax_data.calc(tm, model, types, [ data[cv_model][res]['s2f'], data[cv_model][res]['s2s'], data[cv_model][res]['te'] ])

                    chi2 = self.relax.calc_chi2.relax_data(real, err, back_calc)
                    cv_crit = chi2 / (2.0 * 1.0)
                    sum_cv_crit = sum_cv_crit + cv_crit

                    if self.relax.debug:
                        self.relax.log.write("%7s%-10.4f%2s" % (" Chi2: ", chi2, " |"))
                        self.relax.log.write("%10s%-14.4f%2s\n\n" % (" CV crit: ", cv_crit, " |"))

                self.relax.data.cv.cv_crit[res][model] = sum_cv_crit / float(len(self.relax.data.relax_data))

                if self.relax.debug:
                    self.relax.log.write("%13s%-10.4f\n\n" % ("Ave CV crit: ", sum_cv_crit/float(len(self.relax.data.relax_data))))

            # Select model.
            min = 'm1'
            for model in self.relax.data.runs:
                if self.relax.data.cv.cv_crit[res][model] < self.relax.data.cv.cv_crit[res][min]:
                    min = model
            if self.relax.data.cv.cv_crit[res][min] == float('inf'):
                self.relax.data.results[res] = self.fill_results(data[min+"-"+self.relax.data.frq_label[self.relax.data.remap_table[0]]+"_"+self.relax.data.data_types[0]][res], model='0')
            else:
                self.relax.data.results[res] = self.fill_results(data[min+"-"+self.relax.data.frq_label[self.relax.data.remap_table[0]]+"_"+self.relax.data.data_types[0]][res], model=min[1])

            if self.relax.debug:
                self.relax.log.write(self.relax.usr_param.method + " (m1): " + `self.relax.data.cv.cv_crit[res]['m1']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m2): " + `self.relax.data.cv.cv_crit[res]['m2']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m3): " + `self.relax.data.cv.cv_crit[res]['m3']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m4): " + `self.relax.data.cv.cv_crit[res]['m4']` + "\n")
                self.relax.log.write(self.relax.usr_param.method + " (m5): " + `self.relax.data.cv.cv_crit[res]['m5']` + "\n")
                self.relax.log.write("The selected model is: " + min + "\n\n")

            sys.stdout.write("%10s\n" % ("Model " + self.relax.data.results[res]['model']))


    def print_data(self):
        """Print all the data into the 'data_all' file."""

        file = open('data_all', 'w')
        file_crit = open('crit', 'w')

        sys.stdout.write("[")
        for res in range(len(self.relax.data.results)):
            sys.stdout.write("-")
            file.write("\n\n<<< Residue " + self.relax.data.results[res]['res_num'])
            file.write(", Model " + self.relax.data.results[res]['model'] + " >>>\n")
            file.write('%-20s' % '')
            file.write('%-19s' % 'Model 1')
            file.write('%-19s' % 'Model 2')
            file.write('%-19s' % 'Model 3')
            file.write('%-19s' % 'Model 4')
            file.write('%-19s' % 'Model 5')

            file_crit.write('%-6s' % self.relax.data.results[res]['res_num'])
            file_crit.write('%-6s' % self.relax.data.results[res]['model'])

            for i in range(self.relax.data.num_ri):
                file.write("\n-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i])

                # S2.
                file.write('\n%-20s' % 'S2')
                for model in self.relax.data.runs:
                    cv_model = model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]
                    file.write('%9.3f' % self.relax.data.data[cv_model][res]['s2'])
                    file.write('%1s' % '�')
                    file.write('%-9.3f' % self.relax.data.data[cv_model][res]['s2_err'])

                # S2f.
                file.write('\n%-20s' % 'S2f')
                for model in self.relax.data.runs:
                    cv_model = model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]
                    file.write('%9.3f' % self.relax.data.data[cv_model][res]['s2f'])
                    file.write('%1s' % '�')
                    file.write('%-9.3f' % self.relax.data.data[cv_model][res]['s2f_err'])

                # S2s.
                file.write('\n%-20s' % 'S2s')
                for model in self.relax.data.runs:
                    cv_model = model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]
                    file.write('%9.3f' % self.relax.data.data[cv_model][res]['s2s'])
                    file.write('%1s' % '�')
                    file.write('%-9.3f' % self.relax.data.data[cv_model][res]['s2s_err'])

                # te.
                file.write('\n%-20s' % 'te')
                for model in self.relax.data.runs:
                    cv_model = model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]
                    file.write('%9.2f' % self.relax.data.data[cv_model][res]['te'])
                    file.write('%1s' % '�')
                    file.write('%-9.2f' % self.relax.data.data[cv_model][res]['te_err'])

                # Rex.
                file.write('\n%-20s' % 'Rex')
                for model in self.relax.data.runs:
                    cv_model = model + "-" + self.relax.data.frq_label[self.relax.data.remap_table[i]][1] + "_" + self.relax.data.data_types[i]
                    file.write('%9.3f' % self.relax.data.data[cv_model][res]['rex'])
                    file.write('%1s' % '�')
                    file.write('%-9.3f' % self.relax.data.data[cv_model][res]['rex_err'])

            # Cross validation criteria.
            file.write('\n%-20s' % 'CV')
            for model in self.relax.data.runs:
                file.write('%-19.3f' % self.relax.data.cv.cv_crit[res][model])

                file_crit.write('%-25s' % `self.relax.data.cv.cv_crit[res][model]`)
            file_crit.write('\n')

        file.write('\n')
        sys.stdout.write("]\n")
        file.close()


    def print_results(self):
        """Print the results into the results file."""

        file = open('results', 'w')
        file.write('%-6s%-6s\n' % ( 'ResNo', 'Model' ))
        sys.stdout.write("[")
        for res in range(len(self.relax.data.results)):
            sys.stdout.write("-")
            file.write('%-6s' % self.relax.data.results[res]['res_num'])
            file.write('%-6s\n' % self.relax.data.results[res]['model'])
        sys.stdout.write("]\n")
        file.close()

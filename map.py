from Numeric import Float64, array, zeros
from os import mkdir
from re import match


class Map:
    def __init__(self, relax):
        """"""

        self.relax = relax


    def map_space(self, model=None, inc=20, file="map", dir="dx"):
        """"""

        # Equation type specific function setup.
        ########################################

        # Model-free analysis.
        if match('mf', self.relax.data.equations[model]):
            map_bounds = self.relax.model_free.map_bounds
            self.main_loop = self.relax.model_free.main_loop

        # Unknown equation type.
        else:
            print "The equation " + `self.relax.data.equations[model]` + " has not been coded into the grid search macro."
            return

        ######
        # End.


        # Function arguments.
        self.model = model
        self.inc = inc
        self.file = file
        self.dir = dir

        # The OpenDX directory.
        if self.dir:
            try:
                mkdir(self.dir)
            except OSError:
                pass

        # Get the map bounds.
        self.bounds = map_bounds(model=self.model)

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(model):
            for i in range(len(self.bounds[0])):
                self.bounds[:, i] = self.bounds[:, i] / self.relax.data.scaling[self.model][0]

        # Number of parameters.
        self.n = len(self.relax.data.param_types[self.model])

        # Setup the step sizes.
        self.step_size = zeros(self.n, Float64)
        for i in range(self.n):
            self.step_size[i] = (self.bounds[i][1] - self.bounds[i][0]) / (self.inc - 1.0)

        # Percentage initialisation.
        self.percent = 0.0
        self.percent_inc = 100.0 / self.inc**(self.n - 1.0)

        # Map the 3D space.
        if self.n == 3:
            self.create_3D_general()
            self.create_3D_program()
            self.create_3D_map()

        # Map the 4D space.
        elif self.n == 4:
            print "4D space mapping is not implemented yet."
            return
            #self.map_4D()

        # Other dimension spaces.
        else:
            return


    def create_3D_general(self):
        """Function for creating the OpenDX .general file for a 3D map."""

        # Open the file.
        if self.dir:
            general_file = open(self.dir + "/" + self.file + ".general", "w")
        else:
            general_file = open(self.file + ".general", "w")

        # Generate the text.
        general_file.write("file = " + self.file + "\n")
        general_file.write("grid = " + `self.inc` + " x " + `self.inc` + " x " + `self.inc` + "\n")
        general_file.write("format = ascii\n")
        general_file.write("interleaving = field\n")
        general_file.write("majority = row\n")
        general_file.write("field = data\n")
        general_file.write("structure = scalar\n")
        general_file.write("type = float\n")
        general_file.write("dependency = positions\n")
        general_file.write("positions = regular, regular, regular, 0, 1, 0, 1, 0, 1\n\n")
        general_file.write("end\n")

        # Close the file.
        general_file.close()


    def create_3D_map(self):
        """Function for creating a 3D map."""

        # Map file.
        if self.dir:
            map_file = open(self.dir + "/" + self.file, "w")
        else:
            map_file = open(self.file, "w")

        # Initialise.
        values = zeros(3, Float64)
        print "%-10s%8.3f%-1s" % ("Progress:", self.percent, "%")

        # Create the map.
        values[0] = self.bounds[0][0]
        for i in range(self.inc):
            values[1] = self.bounds[1][0]
            for j in range(self.inc):
                values[2] = self.bounds[2][0]
                for k in range(self.inc):
                    self.main_loop(model=self.model, min_algor='fixed', min_options=values, print_flag=0)
                    map_file.write("%30f\n" % self.relax.data.min_results[self.model][0][0])
                    values[2] = values[2] + self.step_size[2]
                self.percent = self.percent + self.percent_inc
                print "%-10s%8.3f%-8s%-8g" % ("Progress:", self.percent, "%, value: ", self.relax.data.min_results[self.model][0][0])
                values[1] = values[1] + self.step_size[1]
            values[0] = values[0] + self.step_size[0]

        # Close the file.
        map_file.close()


    def create_3D_program(self):
        """Function for creating the OpenDX program for a 3D map."""

        # Open the file.
        if self.dir:
            program_file = open(self.dir + "/" + self.file + ".net", "w")
        else:
            program_file = open(self.file + ".net", "w")

        # Generate the text.
        text = """//
// time: Mon Sep 16 14:34:57 2002
//
// version: 3.1.2 (format), 4.1.3 (DX)
//
//
// MODULE main
// workspace: width = 620, height = 651
// layout: snap = 0, width = 50, height = 50, align = NN
//
macro main(
) -> (
) {
    // 
    // node Import[1]: x = 167, y = 6, inputs = 6, label = Import
    // input[1]: defaulting = 0, visible = 1, type = 32, value = \""""

        program_file.write(text)
        program_file.write(self.file)

        text = """.general"
    // input[3]: defaulting = 1, visible = 1, type = 32, value = "general"
    //
main_Import_1_out_1 = 
    Import(
    main_Import_1_in_1,
    main_Import_1_in_2,
    main_Import_1_in_3,
    main_Import_1_in_4,
    main_Import_1_in_5,
    main_Import_1_in_6
    ) [instance: 1, cache: 1];
    // 
    // node Isosurface[1]: x = 10, y = 82, inputs = 6, label = Outer Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 1000.0
    //
main_Isosurface_1_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_1_in_2,
    main_Isosurface_1_in_3,
    main_Isosurface_1_in_4,
    main_Isosurface_1_in_5,
    main_Isosurface_1_in_6
    ) [instance: 1, cache: 1];
    // 
    // node Color[1]: x = 37, y = 156, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0 0 0.2]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.4
    //
main_Color_1_out_1 = 
    Color(
    main_Isosurface_1_out_1,
    main_Color_1_in_2,
    main_Color_1_in_3,
    main_Color_1_in_4,
    main_Color_1_in_5
    ) [instance: 1, cache: 1];
    // 
    // node Isosurface[2]: x = 125, y = 81, inputs = 6, label = Middle Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 100.0
    //
main_Isosurface_2_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_2_in_2,
    main_Isosurface_2_in_3,
    main_Isosurface_2_in_4,
    main_Isosurface_2_in_5,
    main_Isosurface_2_in_6
    ) [instance: 2, cache: 1];
    // 
    // node Color[2]: x = 152, y = 156, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "blue"
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.45
    //
main_Color_2_out_1 = 
    Color(
    main_Isosurface_2_out_1,
    main_Color_2_in_2,
    main_Color_2_in_3,
    main_Color_2_in_4,
    main_Color_2_in_5
    ) [instance: 2, cache: 1];
    // 
    // node Collect[1]: x = 101, y = 233, inputs = 2, label = Collect
    //
main_Collect_1_out_1 = 
    Collect(
    main_Color_1_out_1,
    main_Color_2_out_1
    ) [instance: 1, cache: 1];
    // 
    // node Isosurface[3]: x = 242, y = 80, inputs = 6, label = Inner Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 50.0
    //
main_Isosurface_3_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_3_in_2,
    main_Isosurface_3_in_3,
    main_Isosurface_3_in_4,
    main_Isosurface_3_in_5,
    main_Isosurface_3_in_6
    ) [instance: 3, cache: 1];
    // 
    // node Color[3]: x = 269, y = 157, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [0.5 0.5 1]
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 0.3
    //
main_Color_3_out_1 = 
    Color(
    main_Isosurface_3_out_1,
    main_Color_3_in_2,
    main_Color_3_in_3,
    main_Color_3_in_4,
    main_Color_3_in_5
    ) [instance: 3, cache: 1];
    // 
    // node Isosurface[4]: x = 357, y = 79, inputs = 6, label = Inner Isosurface
    // input[2]: defaulting = 0, visible = 1, type = 5, value = 10.0
    //
main_Isosurface_4_out_1 = 
    Isosurface(
    main_Import_1_out_1,
    main_Isosurface_4_in_2,
    main_Isosurface_4_in_3,
    main_Isosurface_4_in_4,
    main_Isosurface_4_in_5,
    main_Isosurface_4_in_6
    ) [instance: 4, cache: 1];
    // 
    // node Color[5]: x = 384, y = 157, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "white"
    // input[3]: defaulting = 0, visible = 1, type = 5, value = 1.0
    //
main_Color_5_out_1 = 
    Color(
    main_Isosurface_4_out_1,
    main_Color_5_in_2,
    main_Color_5_in_3,
    main_Color_5_in_4,
    main_Color_5_in_5
    ) [instance: 5, cache: 1];
    // 
    // node Collect[4]: x = 335, y = 232, inputs = 2, label = Collect
    //
main_Collect_4_out_1 = 
    Collect(
    main_Color_3_out_1,
    main_Color_5_out_1
    ) [instance: 4, cache: 1];
    // 
    // node Collect[3]: x = 195, y = 301, inputs = 2, label = Collect
    //
main_Collect_3_out_1 = 
    Collect(
    main_Collect_1_out_1,
    main_Collect_4_out_1
    ) [instance: 3, cache: 1];
    // 
    // node Collect[5]: x = 398, y = 309, inputs = 2, label = Collect
    //
main_Collect_5_out_1 = 
    Collect(
    main_Collect_3_out_1,
    main_Collect_5_in_2
    ) [instance: 5, cache: 1];
    // 
    // node Scale[2]: x = 21, y = 378, inputs = 2, label = Scale
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 1 1]
    //
main_Scale_2_out_1 = 
    Scale(
    main_Collect_5_out_1,
    main_Scale_2_in_2
    ) [instance: 2, cache: 1];
    // 
    // node AutoCamera[1]: x = 82, y = 447, inputs = 9, label = AutoCamera
    // input[2]: defaulting = 0, visible = 1, type = 8, value = [1 -1 0]
    // input[5]: defaulting = 0, visible = 0, type = 5, value = .75
    // input[6]: defaulting = 0, visible = 0, type = 8, value = [-1 1 0]
    // input[7]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[8]: defaulting = 0, visible = 0, type = 5, value = 30.0
    // input[9]: defaulting = 0, visible = 0, type = 32, value = "black"
    //
main_AutoCamera_1_out_1 = 
    AutoCamera(
    main_Scale_2_out_1,
    main_AutoCamera_1_in_2,
    main_AutoCamera_1_in_3,
    main_AutoCamera_1_in_4,
    main_AutoCamera_1_in_5,
    main_AutoCamera_1_in_6,
    main_AutoCamera_1_in_7,
    main_AutoCamera_1_in_8,
    main_AutoCamera_1_in_9
    ) [instance: 1, cache: 1];
    // 
    // node AutoAxes[1]: x = 33, y = 517, inputs = 19, label = AutoAxes
    // input[3]: defaulting = 0, visible = 1, type = 16777248, value = {"alpha" "beta" "gamma"}
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 30
    // input[5]: defaulting = 0, visible = 1, type = 16777224, value = {[0 0 0] [20 20 20]}
    // input[6]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[7]: defaulting = 1, visible = 0, type = 3, value = 1
    // input[9]: defaulting = 0, visible = 1, type = 3, value = 1
    // input[11]: defaulting = 1, visible = 0, type = 16777248, value = {"all"}
    // input[12]: defaulting = 0, visible = 0, type = 5, value = 0.8
    // input[13]: defaulting = 0, visible = 0, type = 32, value = "area"
    // input[14]: defaulting = 1, visible = 1, type = 16777221, value = { 0.0 }
    // input[15]: defaulting = 1, visible = 1, type = 16777221, value = { 0.0 }
    // input[16]: defaulting = 1, visible = 1, type = 16777221, value = { 0.0 }
    // input[17]: defaulting = 1, visible = 1, type = 16777248, value = {" "}
    // input[18]: defaulting = 1, visible = 1, type = 16777248, value = {" "}
    // input[19]: defaulting = 1, visible = 1, type = 16777248, value = {" "}
    //
main_AutoAxes_1_out_1 = 
    AutoAxes(
    main_Scale_2_out_1,
    main_AutoCamera_1_out_1,
    main_AutoAxes_1_in_3,
    main_AutoAxes_1_in_4,
    main_AutoAxes_1_in_5,
    main_AutoAxes_1_in_6,
    main_AutoAxes_1_in_7,
    main_AutoAxes_1_in_8,
    main_AutoAxes_1_in_9,
    main_AutoAxes_1_in_10,
    main_AutoAxes_1_in_11,
    main_AutoAxes_1_in_12,
    main_AutoAxes_1_in_13,
    main_AutoAxes_1_in_14,
    main_AutoAxes_1_in_15,
    main_AutoAxes_1_in_16,
    main_AutoAxes_1_in_17,
    main_AutoAxes_1_in_18,
    main_AutoAxes_1_in_19
    ) [instance: 1, cache: 1];
    // 
    // node Import[2]: x = 476, y = 5, inputs = 6, label = Import
    // input[1]: defaulting = 0, visible = 1, type = 32, value = "fit.general"
    //
main_Import_2_out_1 = 
    Import(
    main_Import_2_in_1,
    main_Import_2_in_2,
    main_Import_2_in_3,
    main_Import_2_in_4,
    main_Import_2_in_5,
    main_Import_2_in_6
    ) [instance: 2, cache: 1];
    // 
    // node Glyph[1]: x = 500, y = 80, inputs = 7, label = Glyph
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "sphere"
    // input[4]: defaulting = 0, visible = 1, type = 5, value = 1.0
    // input[5]: defaulting = 0, visible = 1, type = 5, value = 0.0
    //
main_Glyph_1_out_1 = 
    Glyph(
    main_Import_2_out_1,
    main_Glyph_1_in_2,
    main_Glyph_1_in_3,
    main_Glyph_1_in_4,
    main_Glyph_1_in_5,
    main_Glyph_1_in_6,
    main_Glyph_1_in_7
    ) [instance: 1, cache: 1];
    // 
    // node Color[6]: x = 548, y = 158, inputs = 5, label = Color
    // input[2]: defaulting = 0, visible = 1, type = 32, value = "red"
    //
main_Color_6_out_1 = 
    Color(
    main_Glyph_1_out_1,
    main_Color_6_in_2,
    main_Color_6_in_3,
    main_Color_6_in_4,
    main_Color_6_in_5
    ) [instance: 6, cache: 1];
    // 
    // node Image[2]: x = 141, y = 589, inputs = 49, label = Image
    // input[1]: defaulting = 0, visible = 0, type = 67108863, value = "Image_2"
    // input[4]: defaulting = 0, visible = 0, type = 1, value = 1
    // input[5]: defaulting = 0, visible = 0, type = 8, value = [12.243 10.1395 9.34909]
    // input[6]: defaulting = 0, visible = 0, type = 8, value = [22.6042 6.9002 119.794]
    // input[7]: defaulting = 1, visible = 0, type = 5, value = 39.0494
    // input[8]: defaulting = 0, visible = 0, type = 1, value = 1258
    // input[9]: defaulting = 0, visible = 0, type = 5, value = 0.721
    // input[10]: defaulting = 0, visible = 0, type = 8, value = [-0.995449 0.0164223 0.093868]
    // input[11]: defaulting = 0, visible = 0, type = 5, value = 19.9564
    // input[12]: defaulting = 0, visible = 0, type = 1, value = 1
    // input[14]: defaulting = 0, visible = 0, type = 1, value = 1
    // input[15]: defaulting = 1, visible = 0, type = 32, value = "none"
    // input[16]: defaulting = 1, visible = 0, type = 32, value = "none"
    // input[17]: defaulting = 1, visible = 0, type = 1, value = 1
    // input[18]: defaulting = 1, visible = 0, type = 1, value = 1
    // input[19]: defaulting = 0, visible = 0, type = 1, value = 0
    // input[25]: defaulting = 0, visible = 0, type = 32, value = "best"
    // input[26]: defaulting = 0, visible = 0, type = 32, value = "tiff"
    // input[29]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[30]: defaulting = 0, visible = 0, type = 16777248, value = {\""""

        program_file.write(text)
        program_file.write(self.relax.data.param_types[self.model][0] + " (" + `self.bounds[0][0]` + " to " + `self.bounds[0][1]` + ")\", \"")
        program_file.write(self.relax.data.param_types[self.model][1] + " (" + `self.bounds[1][0]` + " to " + `self.bounds[1][1]` + ")\", \"")
        program_file.write(self.relax.data.param_types[self.model][2] + " (" + `self.bounds[2][0]` + " to " + `self.bounds[2][1]` + ")\"}")

        text = """
    // input[32]: defaulting = 0, visible = 0, type = 16777224, value = {[0 0 0] [100 100 20]}
    // input[33]: defaulting = 0, visible = 0, type = 3, value = 1
    // input[34]: defaulting = 0, visible = 0, type = 3, value = 0
    // input[36]: defaulting = 0, visible = 0, type = 3, value = 1
    // input[41]: defaulting = 0, visible = 0, type = 32, value = "rotate"
    // depth: value = 24
    // window: position = (0.0000,0.0000), size = 0.9938x0.9287
    // internal caching: 1
    //
main_Image_2_out_1,
main_Image_2_out_2,
main_Image_2_out_3 = 
    Image(
    main_Image_2_in_1,
    main_AutoAxes_1_out_1,
    main_Image_2_in_3,
    main_Image_2_in_4,
    main_Image_2_in_5,
    main_Image_2_in_6,
    main_Image_2_in_7,
    main_Image_2_in_8,
    main_Image_2_in_9,
    main_Image_2_in_10,
    main_Image_2_in_11,
    main_Image_2_in_12,
    main_Image_2_in_13,
    main_Image_2_in_14,
    main_Image_2_in_15,
    main_Image_2_in_16,
    main_Image_2_in_17,
    main_Image_2_in_18,
    main_Image_2_in_19,
    main_Image_2_in_20,
    main_Image_2_in_21,
    main_Image_2_in_22,
    main_Image_2_in_23,
    main_Image_2_in_24,
    main_Image_2_in_25,
    main_Image_2_in_26,
    main_Image_2_in_27,
    main_Image_2_in_28,
    main_Image_2_in_29,
    main_Image_2_in_30,
    main_Image_2_in_31,
    main_Image_2_in_32,
    main_Image_2_in_33,
    main_Image_2_in_34,
    main_Image_2_in_35,
    main_Image_2_in_36,
    main_Image_2_in_37,
    main_Image_2_in_38,
    main_Image_2_in_39,
    main_Image_2_in_40,
    main_Image_2_in_41,
    main_Image_2_in_42,
    main_Image_2_in_43,
    main_Image_2_in_44,
    main_Image_2_in_45,
    main_Image_2_in_46,
    main_Image_2_in_47,
    main_Image_2_in_48,
    main_Image_2_in_49
    ) [instance: 2, cache: 1];
// network: end of macro body
CacheScene(main_Image_2_in_1, main_Image_2_out_1, main_Image_2_out_2);
}
main_Import_1_in_1 = \""""

        program_file.write(text)
        program_file.write(self.file)

        text = """.general";
main_Import_1_in_2 = NULL;
main_Import_1_in_3 = NULL;
main_Import_1_in_4 = NULL;
main_Import_1_in_5 = NULL;
main_Import_1_in_6 = NULL;
main_Import_1_out_1 = NULL;
main_Isosurface_1_in_2 = 1000.0;
main_Isosurface_1_in_3 = NULL;
main_Isosurface_1_in_4 = NULL;
main_Isosurface_1_in_5 = NULL;
main_Isosurface_1_in_6 = NULL;
main_Isosurface_1_out_1 = NULL;
main_Color_1_in_2 = [0 0 0.2];
main_Color_1_in_3 = 0.4;
main_Color_1_in_4 = NULL;
main_Color_1_in_5 = NULL;
main_Color_1_out_1 = NULL;
main_Isosurface_2_in_2 = 100.0;
main_Isosurface_2_in_3 = NULL;
main_Isosurface_2_in_4 = NULL;
main_Isosurface_2_in_5 = NULL;
main_Isosurface_2_in_6 = NULL;
main_Isosurface_2_out_1 = NULL;
main_Color_2_in_2 = "blue";
main_Color_2_in_3 = 0.45;
main_Color_2_in_4 = NULL;
main_Color_2_in_5 = NULL;
main_Color_2_out_1 = NULL;
main_Collect_1_out_1 = NULL;
main_Isosurface_3_in_2 = 50.0;
main_Isosurface_3_in_3 = NULL;
main_Isosurface_3_in_4 = NULL;
main_Isosurface_3_in_5 = NULL;
main_Isosurface_3_in_6 = NULL;
main_Isosurface_3_out_1 = NULL;
main_Color_3_in_2 = [0.5 0.5 1];
main_Color_3_in_3 = 0.3;
main_Color_3_in_4 = NULL;
main_Color_3_in_5 = NULL;
main_Color_3_out_1 = NULL;
main_Isosurface_4_in_2 = 10.0;
main_Isosurface_4_in_3 = NULL;
main_Isosurface_4_in_4 = NULL;
main_Isosurface_4_in_5 = NULL;
main_Isosurface_4_in_6 = NULL;
main_Isosurface_4_out_1 = NULL;
main_Color_5_in_2 = "white";
main_Color_5_in_3 = 1.0;
main_Color_5_in_4 = NULL;
main_Color_5_in_5 = NULL;
main_Color_5_out_1 = NULL;
main_Collect_4_out_1 = NULL;
main_Collect_3_out_1 = NULL;
main_Collect_5_in_2 = NULL;
main_Collect_5_out_1 = NULL;
main_Scale_2_in_2 = [1 1 1];
main_Scale_2_out_1 = NULL;
main_AutoCamera_1_in_2 = [1 -1 0];
main_AutoCamera_1_in_3 = NULL;
main_AutoCamera_1_in_4 = NULL;
main_AutoCamera_1_in_5 = .75;
main_AutoCamera_1_in_6 = [-1 1 0];
main_AutoCamera_1_in_7 = 0;
main_AutoCamera_1_in_8 = 30.0;
main_AutoCamera_1_in_9 = "black";
main_AutoCamera_1_out_1 = NULL;
main_AutoAxes_1_in_3 = {"alpha" "beta" "gamma"};
main_AutoAxes_1_in_4 = 30;
main_AutoAxes_1_in_5 = {[0 0 0] [20 20 20]};
main_AutoAxes_1_in_6 = 1;
main_AutoAxes_1_in_7 = NULL;
main_AutoAxes_1_in_8 = NULL;
main_AutoAxes_1_in_9 = 1;
main_AutoAxes_1_in_10 = NULL;
main_AutoAxes_1_in_11 = NULL;
main_AutoAxes_1_in_12 = 0.8;
main_AutoAxes_1_in_13 = "area";
main_AutoAxes_1_in_14 = NULL;
main_AutoAxes_1_in_15 = NULL;
main_AutoAxes_1_in_16 = NULL;
main_AutoAxes_1_in_17 = NULL;
main_AutoAxes_1_in_18 = NULL;
main_AutoAxes_1_in_19 = NULL;
main_AutoAxes_1_out_1 = NULL;
main_Import_2_in_1 = "fit.general";
main_Import_2_in_2 = NULL;
main_Import_2_in_3 = NULL;
main_Import_2_in_4 = NULL;
main_Import_2_in_5 = NULL;
main_Import_2_in_6 = NULL;
main_Import_2_out_1 = NULL;
main_Glyph_1_in_2 = "sphere";
main_Glyph_1_in_3 = NULL;
main_Glyph_1_in_4 = 1.0;
main_Glyph_1_in_5 = 0.0;
main_Glyph_1_in_6 = NULL;
main_Glyph_1_in_7 = NULL;
main_Glyph_1_out_1 = NULL;
main_Color_6_in_2 = "red";
main_Color_6_in_3 = NULL;
main_Color_6_in_4 = NULL;
main_Color_6_in_5 = NULL;
macro Image(
        id,
        object,
        where,
        useVector,
        to,
        from,
        width,
        resolution,
        aspect,
        up,
        viewAngle,
        perspective,
        options,
        buttonState = 1,
        buttonUpApprox = "none",
        buttonDownApprox = "none",
        buttonUpDensity = 1,
        buttonDownDensity = 1,
        renderMode = 0,
        defaultCamera,
        reset,
        backgroundColor,
        throttle,
        RECenable = 0,
        RECfile,
        RECformat,
        RECresolution,
        RECaspect,
        AAenable = 0,
        AAlabels,
        AAticks,
        AAcorners,
        AAframe,
        AAadjust,
        AAcursor,
        AAgrid,
        AAcolors,
        AAannotation,
        AAlabelscale,
        AAfont,
        interactionMode,
        title,
        AAxTickLocs,
        AAyTickLocs,
        AAzTickLocs,
        AAxTickLabels,
        AAyTickLabels,
        AAzTickLabels,
        webOptions) -> (
        object,
        camera,
        where)
{
    ImageMessage(
        id,
        backgroundColor,
        throttle,
        RECenable,
        RECfile,
        RECformat,
        RECresolution,
        RECaspect,
        AAenable,
        AAlabels,
        AAticks,
        AAcorners,
        AAframe,
        AAadjust,
        AAcursor,
        AAgrid,
        AAcolors,
        AAannotation,
        AAlabelscale,
        AAfont,
        AAxTickLocs,
        AAyTickLocs,
        AAzTickLocs,
        AAxTickLabels,
        AAyTickLabels,
        AAzTickLabels,
        interactionMode,
        title,
        renderMode,
        buttonUpApprox,
        buttonDownApprox,
        buttonUpDensity,
        buttonDownDensity) [instance: 1, cache: 1];
    autoCamera =
        AutoCamera(
            object,
            "front",
            object,
            resolution,
            aspect,
            [0,1,0],
            perspective,
            viewAngle,
            backgroundColor) [instance: 1, cache: 1];
    realCamera =
        Camera(
            to,
            from,
            width,
            resolution,
            aspect,
            up,
            perspective,
            viewAngle,
            backgroundColor) [instance: 1, cache: 1];
    coloredDefaultCamera = 
	 UpdateCamera(defaultCamera,
            background=backgroundColor) [instance: 1, cache: 1];
    nullDefaultCamera =
        Inquire(defaultCamera,
            "is null + 1") [instance: 1, cache: 1];
    resetCamera =
        Switch(
            nullDefaultCamera,
            coloredDefaultCamera,
            autoCamera) [instance: 1, cache: 1];
    resetNull = 
        Inquire(
            reset,
            "is null + 1") [instance: 2, cache: 1];
    reset =
        Switch(
            resetNull,
            reset,
            0) [instance: 2, cache: 1];
    whichCamera =
        Compute(
            "($0 != 0 || $1 == 0) ? 1 : 2",
            reset,
            useVector) [instance: 1, cache: 1];
    camera = Switch(
            whichCamera,
            resetCamera,
            realCamera) [instance: 3, cache: 1];
    AAobject =
        AutoAxes(
            object,
            camera,
            AAlabels,
            AAticks,
            AAcorners,
            AAframe,
            AAadjust,
            AAcursor,
            AAgrid,
            AAcolors,
            AAannotation,
            AAlabelscale,
            AAfont,
            AAxTickLocs,
            AAyTickLocs,
            AAzTickLocs,
            AAxTickLabels,
            AAyTickLabels,
            AAzTickLabels) [instance: 1, cache: 1];
    switchAAenable = Compute("$0+1",
	     AAenable) [instance: 2, cache: 1];
    object = Switch(
	     switchAAenable,
	     object,
	     AAobject) [instance:4, cache: 1];
    SWapproximation_options =
        Switch(
            buttonState,
            buttonUpApprox,
            buttonDownApprox) [instance: 5, cache: 1];
    SWdensity_options =
        Switch(
            buttonState,
            buttonUpDensity,
            buttonDownDensity) [instance: 6, cache: 1];
    HWapproximation_options =
        Format(
            "%s,%s",
            buttonDownApprox,
            buttonUpApprox) [instance: 1, cache: 1];
    HWdensity_options =
        Format(
            "%d,%d",
            buttonDownDensity,
            buttonUpDensity) [instance: 2, cache: 1];
    switchRenderMode = Compute(
	     "$0+1",
	     renderMode) [instance: 3, cache: 1];
    approximation_options = Switch(
	     switchRenderMode,
            SWapproximation_options,
	     HWapproximation_options) [instance: 7, cache: 1];
    density_options = Switch(
	     switchRenderMode,
            SWdensity_options,
            HWdensity_options) [instance: 8, cache: 1];
    renderModeString = Switch(
            switchRenderMode,
            "software",
            "hardware")[instance: 9, cache: 1];
    object_tag = Inquire(
            object,
            "object tag")[instance: 3, cache: 1];
    annoted_object =
        Options(
            object,
            "send boxes",
            0,
            "cache",
            1,
            "object tag",
            object_tag,
            "ddcamera",
            whichCamera,
            "rendering approximation",
            approximation_options,
            "render every",
            density_options,
            "button state",
            buttonState,
            "rendering mode",
            renderModeString) [instance: 1, cache: 1];
    RECresNull =
        Inquire(
            RECresolution,
            "is null + 1") [instance: 4, cache: 1];
    ImageResolution =
        Inquire(
            camera,
            "camera resolution") [instance: 5, cache: 1];
    RECresolution =
        Switch(
            RECresNull,
            RECresolution,
            ImageResolution) [instance: 10, cache: 1];
    RECaspectNull =
        Inquire(
            RECaspect,
            "is null + 1") [instance: 6, cache: 1];
    ImageAspect =
        Inquire(
            camera,
            "camera aspect") [instance: 7, cache: 1];
    RECaspect =
        Switch(
            RECaspectNull,
            RECaspect,
            ImageAspect) [instance: 11, cache: 1];
    switchRECenable = Compute(
          "$0 == 0 ? 1 : (($2 == $3) && ($4 == $5)) ? ($1 == 1 ? 2 : 3) : 4",
            RECenable,
            switchRenderMode,
            RECresolution,
            ImageResolution,
            RECaspect,
	     ImageAspect) [instance: 4, cache: 1];
    NoRECobject, RECNoRerenderObject, RECNoRerHW, RECRerenderObject = Route(switchRECenable, annoted_object);
    Display(
        NoRECobject,
        camera,
        where,
        throttle) [instance: 1, cache: 1];
    image =
        Render(
            RECNoRerenderObject,
            camera) [instance: 1, cache: 1];
    Display(
        image,
        NULL,
        where,
        throttle) [instance: 2, cache: 1];
    WriteImage(
        image,
        RECfile,
        RECformat) [instance: 1, cache: 1];
    rec_where = Display(
        RECNoRerHW,
        camera,
        where,
        throttle) [instance: 1, cache: 0];
    rec_image = ReadImageWindow(
        rec_where) [instance: 1, cache: 1];
    WriteImage(
        rec_image,
        RECfile,
        RECformat) [instance: 1, cache: 1];
    RECupdateCamera =
	UpdateCamera(
	    camera,
	    resolution=RECresolution,
	    aspect=RECaspect) [instance: 2, cache: 1];
    Display(
        RECRerenderObject,
        camera,
        where,
        throttle) [instance: 1, cache: 1];
    RECRerenderObject =
	ScaleScreen(
	    RECRerenderObject,
	    NULL,
	    RECresolution,
	    camera) [instance: 1, cache: 1];
    image =
        Render(
            RECRerenderObject,
            RECupdateCamera) [instance: 2, cache: 1];
    WriteImage(
        image,
        RECfile,
        RECformat) [instance: 2, cache: 1];
}
main_Image_2_in_1 = "Image_2";
main_Image_2_in_3 = "X24,,";
main_Image_2_in_4 = 1;
main_Image_2_in_5 = [12.243 10.1395 9.34909];
main_Image_2_in_6 = [22.6042 6.9002 119.794];
main_Image_2_in_7 = NULL;
main_Image_2_in_8 = 1258;
main_Image_2_in_9 = 0.721;
main_Image_2_in_10 = [-0.995449 0.0164223 0.093868];
main_Image_2_in_11 = 19.9564;
main_Image_2_in_12 = 1;
main_Image_2_in_13 = NULL;
main_Image_2_in_14 = 1;
main_Image_2_in_15 = NULL;
main_Image_2_in_16 = NULL;
main_Image_2_in_17 = NULL;
main_Image_2_in_18 = NULL;
main_Image_2_in_19 = 0;
main_Image_2_in_20 = NULL;
main_Image_2_in_21 = NULL;
main_Image_2_in_22 = NULL;
main_Image_2_in_23 = NULL;
main_Image_2_in_25 = "best";
main_Image_2_in_26 = "tiff";
main_Image_2_in_27 = NULL;
main_Image_2_in_28 = NULL;
main_Image_2_in_29 = 0;
main_Image_2_in_30 = {"S2 (0 to 1)", "te (0ns to 10000ns)", "Rex (0 to 30)"};
main_Image_2_in_31 = NULL;
main_Image_2_in_32 = {[0 0 0] [100 100 20]};
main_Image_2_in_33 = 1;
main_Image_2_in_34 = 0;
main_Image_2_in_35 = NULL;
main_Image_2_in_36 = 1;
main_Image_2_in_37 = NULL;
main_Image_2_in_38 = NULL;
main_Image_2_in_39 = NULL;
main_Image_2_in_40 = NULL;
main_Image_2_in_41 = "rotate";
main_Image_2_in_42 = NULL;
main_Image_2_in_43 = NULL;
main_Image_2_in_44 = NULL;
main_Image_2_in_45 = NULL;
main_Image_2_in_46 = NULL;
main_Image_2_in_47 = NULL;
main_Image_2_in_48 = NULL;
main_Image_2_in_49 = NULL;
Executive("product version 4 1 3");
$sync
main();"""

        program_file.write(text)
        
        # Close the file.
        program_file.close()


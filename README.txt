P1 and DOM Heat-Exchanger Code
==============================

This folder contains the P1 and Discrete Ordinates Model calculations used for the heat-exchanger part of the thesis. The two radiation models use the same finite-volume framework and are applied to the different tube arrangements and parameter studies.

Requirements
------------

The C++ code needs:

- CMake 3.16 or newer
- a C++17 compiler
- a Unix-like terminal environment

The plotting scripts use Python 3 with:

    numpy
    pandas
    matplotlib

These packages can be installed with:

    pip install numpy pandas matplotlib

Code layout
-----------

The main parts of the project are:

    main.cpp
        Runs the heat-exchanger studies.

    P1.hpp
        P1 radiation model.

    DOM.hpp
        Discrete Ordinates Model.

    FVCore/
        Field classes, boundary conditions, ordinate handling and heat-exchanger diagnostics.

    Mesh/
        Mesh reading and face addressing.

    Discretisation/
        Finite-volume diffusion, convection and source terms.

    SparseOperations/
        Sparse matrix and vector classes.

    Solver/
        Iterative solver routines.

    ValidationTests/
        The five heat-exchanger studies and their plotting scripts.

    Files/MeshFiles/
        Meshes for the arrangements and spacing cases.

    Files/FieldFiles/
        Initial temperature and irradiation fields for the cases.

    Output/
        Simulation results and generated plots.

Building and running
--------------------

From the project root run:

    chmod +x run.sh
    ./run.sh

This removes the old build folder, builds the code in Release mode, and runs:

    build/p1_app

CMake copies Files/ into build/Files/. The executable is then run from inside build/, while PathConfig.hpp writes the results to ../Output/.

The supplied main.cpp runs all five studies:

1. arrangement test
2. spatial-difference test
3. optical-thickness test
4. scattering test
5. tube-temperature-difference test

If only one study is required, comment out the other .test() calls in main.cpp and rebuild.

Output
------

Each study writes to its own folder below Output/, for example:

    Output/DOMP1HeatExchangerArrangementTest/
    Output/DOMP1HeatExchangerSpatialDifferenceTest/
    Output/DOMP1HeatExchangerOpticalThicknessTest/
    Output/DOMP1HeatExchangerScatteringTest/
    Output/DOMP1HeatExchangerTemperatureDifferenceTest/

The exact contents depend on the study, but include CSV diagnostics, centreline or inter-row profiles, summary data and VTK fields.

Plotting
--------

Run the C++ simulations before the Python scripts. The commands below are intended to be run from the project root.

Arrangement study:

    python3 ValidationTests/DOMP1HeatExchangerArrangementTest/plot_heat_exchanger_arrangement_profiles.py Output

Spatial-difference study:

    python3 ValidationTests/DOMP1HeatExchangerSpatialDifferenceTest/plot_DOMP1HeatExchangerSpatialDifferenceTest.py .

Optical-thickness/spatial comparison:

    python3 ValidationTests/DOMP1HeatExchangerOpticalThicknessTest/plot_DOMP1HeatExchangerOpticalSpatialComparison.py .

Scattering study:

    python3 ValidationTests/DOMP1HeatExchangerScatteringTest/plot_DOMP1HeatExchangerScatteringTest.py .

Temperature-difference study:

    python3 ValidationTests/DOMP1HeatExchangerTemperatureDifferenceTest/plot_DOMP1HeatExchangerTemperatureDifferenceTest.py .

The scripts locate their data below Output/ and save the generated figures within the corresponding test output folders.

Changing cases
--------------

The physical test ranges and arrangements are defined in the header files inside ValidationTests/. main.cpp only controls which study groups are run. Meshes and initial fields are stored under Files/ and should remain in their present directory structure.

# include "PathConfig.hpp"

# include <iostream>
# include <vector>
# include <array>
# include <map>
# include <filesystem>
# include <string>
# include <fstream>
# include <cstdlib>
# include <stdexcept>
# include <cmath>

# include "MeshFileReader3D.hpp"
# include "FaceAddressedMesh3D.hpp"
# include "SparseAddress.hpp"
# include "SparseMatrix.hpp"
# include "SparseLinearVector.hpp"
# include "SparseLinearSystem.hpp"
# include "GaussSeidelSmoother.hpp"
# include "GaussSeidelSolver.hpp"
# include "Convection.hpp"
# include "Diffusion.hpp"
# include "Ddt.hpp"
# include "Source.hpp"
# include "FVMatrix.hpp"
# include "FaceFluxField.hpp"
# include "ScalarProperty.hpp"
# include "BoundaryCondition.hpp"
# include "FixedValueBC.hpp"
# include "GradientBC.hpp"
# include "Patch.hpp"
# include "FieldFileReader.hpp"
# include "Field.hpp"
# include "P1.hpp"

# include "DOMatrix.hpp"
# include "OrdinateField.hpp"
# include "OrdinatesConstructor.hpp"
# include "PeriodicBC.hpp"
# include "DiscreteOrdinateBC.hpp"
# include "DiscreteOrdinateWallHeatFlux.hpp"
# include "DOM.hpp"

# include "HeatExchangerDOMDiagnostics.hpp"
# include "HeatExchangeP1Diagnostics.hpp"

# include "AnalyticalEvaluator.hpp"

# include "DOMP1HeatExchangerArrangementTest.hpp"
# include "DOMP1HeatExchangerSpatialDifferenceTest.hpp"
# include "DOMP1HeatExchangerOpticalThicknessTest.hpp"
# include "DOMP1HeatExchangerTemperatureDifferenceTest.hpp"
# include "DOMP1HeatExchangerScatteringTest.hpp"

namespace fs = std::filesystem;
using namespace std ;


int main(){

    DOMP1HeatExchangerArrangementTest DOMP1HEAT ;
    DOMP1HEAT.test() ;

    DOMP1HeatExchangerSpatialDifferenceTest DOMP1HESDT ;
    DOMP1HESDT.test() ;

    DOMP1HeatExchangerOpticalThicknessTest DOMP1HEOTT ;
    DOMP1HEOTT.test() ;

    DOMP1HeatExchangerScatteringTest DOMP1HEST ;
    DOMP1HEST.test() ;

    DOMP1HeatExchangerTemperatureDifferenceTest DOMP1HETDT ;
    DOMP1HETDT.test() ;

}








# pragma once

# include "PathConfig.hpp"
# include "P1.hpp"
# include "DOM.hpp"

# include <iostream>
# include <vector>
# include <map>
# include <filesystem>
# include <string>
# include <fstream>
# include <stdexcept>
# include <cmath>
# include <chrono>
# include <limits>
# include <array>
# include <sstream>
# include <algorithm>

using namespace std;

struct DOMP1HeatExchangerTemperatureDifferenceTestResult{
    string parameterName ;
    double parameterValue = 0.0 ;
    double runtime = 0.0 ;
    double absorptionCoefficient = 0.0 ;
    double scatteringCoefficient = 0.0 ;
    double hotPipeTemperature = 0.0 ;
    double coldPipeTemperature = 0.0 ;
    double outerWallTemperature = 0.0 ;
    double initialMediumTemperature = 0.0 ;
    int totalIterationCount = 0 ;
    double minimumDimensionlessTemperature = 0.0 ;
    double maximumDimensionlessTemperature = 0.0 ;
    double minimumDimensionlessIrradiation = 0.0 ;
    double maximumDimensionlessIrradiation = 0.0 ;
    double minimumDimensionlessHeatFluxMagnitude = 0.0 ;
    double maximumDimensionlessHeatFluxMagnitude = 0.0 ;
    array<double,3> minimumTemperatureLocation = {0,0,0} ;
    array<double,3> maximumTemperatureLocation = {0,0,0} ;
    array<double,3> minimumIrradiationLocation = {0,0,0} ;
    array<double,3> maximumIrradiationLocation = {0,0,0} ;
    array<double,3> minimumHeatFluxMagnitudeLocation = {0,0,0} ;
    array<double,3> maximumHeatFluxMagnitudeLocation = {0,0,0} ;
    double totalHotPipeHeatRelease = 0.0 ;
    double totalColdPipeHeatAbsorption = 0.0 ;
    double totalOuterWallHeatLoss = 0.0 ;
    double heatRecoveryRatio = 0.0 ;
    double wallLossRatio = 0.0 ;
    double meanColdPipeHeatLoad = 0.0 ;
    double standardDeviationColdPipeHeatLoad = 0.0 ;
    double coefficientOfVariationColdPipeHeatLoad = 0.0 ;
    double minimumColdPipeHeatLoad = 0.0 ;
    double maximumColdPipeHeatLoad = 0.0 ;
    double minimumTemperature = 0.0 ;
    double maximumTemperature = 0.0 ;
    double minimumHeatFluxMagnitude = 0.0 ;
    double maximumHeatFluxMagnitude = 0.0 ;
    double averageTemperature = 0.0 ;
    double standardDeviationTemperature = 0.0 ;
    double minimumIrradiation = 0.0 ;
    double maximumIrradiation = 0.0 ;
    double averageIrradiation = 0.0 ;
    double totalRadiativeSourceTerm = 0.0 ;
    double energyBalanceResidual = 0.0 ;
    double energyBalanceError = 0.0 ;
    map<string,double> hotPipeHeatRelease ;
    map<string,double> coldPipeHeatAbsorption ;
    map<string,double> outerWallHeatLoss ;
    map<string,double> averageWallIrradiation ;
    map<string,double> averageWallHeatFlux ;
};


class DOMP1HeatExchangerTemperatureDifferenceTest{

    vector<DOMP1HeatExchangerTemperatureDifferenceTestResult> p1Results_ ;
    vector<DOMP1HeatExchangerTemperatureDifferenceTestResult> domResults_ ;

    public:

    void test(){
        P1HeatExchangerTemperatureDifferenceTest() ;
        DOMHeatExchangerTemperatureDifferenceTest() ;
        compareP1AndDOM() ;
    }

    void P1HeatExchangerTemperatureDifferenceTest(){
        PathConfig paths ;
        try{ paths.validate() ; paths.ensureOutputDir() ;}
        catch(const exception& e){ cerr << "Path error: " << e.what() << endl ; throw runtime_error(e.what()) ;}

        string parentFolder = "DOMP1HeatExchangerTemperatureDifferenceTest" ;
        string caseName = "P1" ;
        vector<string> arrangements = {"HotPipesSurroundedByColdPipes","AlternatingArrangement"} ;
        vector<double> parameterValues = {900.0,1000.0,1100.0,1200.0,1300.0} ;
        vector<string> outerWallPatchNames = {"east","west","north","south","top","bottom"} ;
        double a = 1.0, sigmaS = 0.0, k = 0.0, anisotropyFactor = 0.0, coldPipeTemperature = 100.0, outerWallTemperature = 0.0, initialMediumTemperature = 0.0 ;
        string dimension = "HeatExchangerMesh" ;

        for(string arrangement: arrangements){
            vector<string> hotPipePatchNames, coldPipePatchNames ;
            if(arrangement=="HotPipesSurroundedByColdPipes"){
                hotPipePatchNames = {"circle22","circle23","circle24","circle25","circle32","circle33","circle34","circle35","circle42","circle43","circle44","circle45","circle52","circle53","circle54","circle55"} ;
                coldPipePatchNames = {"circle11","circle12","circle13","circle14","circle15","circle16","circle21","circle26","circle31","circle36","circle41","circle46","circle51","circle56","circle61","circle62","circle63","circle64","circle65","circle66"} ;
            }
            else{
                hotPipePatchNames = {"circle11","circle13","circle15","circle22","circle24","circle26","circle31","circle33","circle35","circle42","circle44","circle46","circle51","circle53","circle55","circle62"} ;
                coldPipePatchNames = {"circle12","circle14","circle16","circle21","circle23","circle25","circle32","circle34","circle36","circle41","circle43","circle45","circle52","circle54","circle56","circle61","circle63","circle64","circle65","circle66"} ;
            }
            vector<double> emissivity(hotPipePatchNames.size()+coldPipePatchNames.size()+outerWallPatchNames.size(),1.0) ;
            string arrangementCaseName = caseName + "/" + arrangement ;
            paths.createOutputDirectory(parentFolder,arrangementCaseName) ;
            ofstream summary_info(paths.getOutputDirectory(parentFolder,arrangementCaseName) / "P1_summary.csv") ;
            writeSummaryHeader(summary_info) ;

            for(double parameterValue: parameterValues){
                string parameterSubCaseName = "temperatureDifference" + to_string(parameterValue) ;
                double hotPipeTemperature = coldPipeTemperature+parameterValue ;
                vector<string> meshFiles = paths.getMeshFilenames(parentFolder,dimension) ;
                vector<string> fieldFiles = {paths.getTFieldFile(parentFolder,arrangement,parameterSubCaseName),paths.getGFieldFile(parentFolder,arrangement,parameterSubCaseName)} ;
                string p1CaseName = parentFolder + "/" + caseName + "/" + arrangement ;
                P1 p1(meshFiles,fieldFiles,a,sigmaS,k,emissivity,dimension,p1CaseName,parameterSubCaseName,anisotropyFactor,hotPipePatchNames,coldPipePatchNames,outerWallPatchNames) ;

                auto start = chrono::high_resolution_clock::now() ;
                p1.runP1HeatExchanger() ;
                p1.heatExchangerData()->calculateExtendedDiagnostics() ;
                auto end = chrono::high_resolution_clock::now() ;
                chrono::duration<double> elapsed = end-start ;

                int totalIterationCount = readIterationCount(paths.getOutputDirectory(p1CaseName,parameterSubCaseName)) ;
                DOMP1HeatExchangerTemperatureDifferenceTestResult result = collectResult("temperature_difference",parameterValue,elapsed.count(),a,sigmaS,hotPipeTemperature,coldPipeTemperature,outerWallTemperature,initialMediumTemperature,totalIterationCount,p1.heatExchangerData()) ;
                p1Results_.push_back(result) ;
                writeSummaryResult(summary_info,result) ;
                writePipeResults(paths.getOutputDirectory(parentFolder,arrangementCaseName),"P1",result) ;
                writeExtendedDiagnostics(paths.getOutputDirectory(parentFolder,arrangementCaseName),parameterSubCaseName,p1.heatExchangerData(),0.20,a,sigmaS,hotPipeTemperature,coldPipeTemperature,outerWallTemperature,initialMediumTemperature) ;
            }
        }
    }

    void DOMHeatExchangerTemperatureDifferenceTest(){
        PathConfig paths ;
        try{ paths.validate() ; paths.ensureOutputDir() ;}
        catch(const exception& e){ cerr << "Path error: " << e.what() << endl ; throw runtime_error(e.what()) ;}

        string parentFolder = "DOMP1HeatExchangerTemperatureDifferenceTest" ;
        string caseName = "DOM" ;
        vector<string> arrangements = {"HotPipesSurroundedByColdPipes","AlternatingArrangement"} ;
        vector<double> parameterValues = {900.0,1000.0,1100.0,1200.0,1300.0} ;
        vector<string> outerWallPatchNames = {"east","west","north","south","top","bottom"} ;
        double a = 1.0, sigmaS = 0.0, k = 0.0, anisotropyFactor = 0.0, coldPipeTemperature = 100.0, outerWallTemperature = 0.0, initialMediumTemperature = 0.0 ;
        int ordinate = 8 ;
        string dimension = "HeatExchangerMesh" ;

        for(string arrangement: arrangements){
            vector<string> hotPipePatchNames, coldPipePatchNames ;
            if(arrangement=="HotPipesSurroundedByColdPipes"){
                hotPipePatchNames = {"circle22","circle23","circle24","circle25","circle32","circle33","circle34","circle35","circle42","circle43","circle44","circle45","circle52","circle53","circle54","circle55"} ;
                coldPipePatchNames = {"circle11","circle12","circle13","circle14","circle15","circle16","circle21","circle26","circle31","circle36","circle41","circle46","circle51","circle56","circle61","circle62","circle63","circle64","circle65","circle66"} ;
            }
            else{
                hotPipePatchNames = {"circle11","circle13","circle15","circle22","circle24","circle26","circle31","circle33","circle35","circle42","circle44","circle46","circle51","circle53","circle55","circle62"} ;
                coldPipePatchNames = {"circle12","circle14","circle16","circle21","circle23","circle25","circle32","circle34","circle36","circle41","circle43","circle45","circle52","circle54","circle56","circle61","circle63","circle64","circle65","circle66"} ;
            }
            vector<double> emissivity(hotPipePatchNames.size()+coldPipePatchNames.size()+outerWallPatchNames.size(),1.0) ;
            string arrangementCaseName = caseName + "/" + arrangement ;
            paths.createOutputDirectory(parentFolder,arrangementCaseName) ;
            ofstream summary_info(paths.getOutputDirectory(parentFolder,arrangementCaseName) / "DOM_summary.csv") ;
            writeSummaryHeader(summary_info) ;

            for(double parameterValue: parameterValues){
                string parameterSubCaseName = "temperatureDifference" + to_string(parameterValue) ;
                double hotPipeTemperature = coldPipeTemperature+parameterValue ;
                vector<string> meshFiles = paths.getMeshFilenames(parentFolder,dimension) ;
                vector<string> fieldFiles = {paths.getTFieldFile(parentFolder,arrangement,parameterSubCaseName)} ;
                string domCaseName = parentFolder + "/" + caseName + "/" + arrangement ;
                DOM dom(meshFiles,fieldFiles,a,k,sigmaS,emissivity,dimension,domCaseName,parameterSubCaseName,ordinate,anisotropyFactor,hotPipePatchNames,coldPipePatchNames,outerWallPatchNames) ;

                auto start = chrono::high_resolution_clock::now() ;
                dom.runDOMHeatExchanger() ;
                dom.heatExchangerData()->calculateExtendedDiagnostics() ;
                auto end = chrono::high_resolution_clock::now() ;
                chrono::duration<double> elapsed = end-start ;

                int totalIterationCount = readIterationCount(paths.getOutputDirectory(domCaseName,parameterSubCaseName)) ;
                DOMP1HeatExchangerTemperatureDifferenceTestResult result = collectResult("temperature_difference",parameterValue,elapsed.count(),a,sigmaS,hotPipeTemperature,coldPipeTemperature,outerWallTemperature,initialMediumTemperature,totalIterationCount,dom.heatExchangerData()) ;
                domResults_.push_back(result) ;
                writeSummaryResult(summary_info,result) ;
                writePipeResults(paths.getOutputDirectory(parentFolder,arrangementCaseName),"DOM",result) ;
                writeExtendedDiagnostics(paths.getOutputDirectory(parentFolder,arrangementCaseName),parameterSubCaseName,dom.heatExchangerData(),0.20,a,sigmaS,hotPipeTemperature,coldPipeTemperature,outerWallTemperature,initialMediumTemperature) ;
            }
        }
    }

    void compareP1AndDOM(){
        if(p1Results_.size()!=domResults_.size()){ throw runtime_error("temperature_difference comparison requires matching P1 and DOM result counts") ;}
        PathConfig paths ;
        string parentFolder = "DOMP1HeatExchangerTemperatureDifferenceTest" ;
        string caseName = "Comparison" ;
        vector<string> arrangements = {"HotPipesSurroundedByColdPipes","AlternatingArrangement"} ;
        size_t resultsPerArrangement = p1Results_.size()/arrangements.size() ;

        for(size_t arrangementIndex=0; arrangementIndex<arrangements.size(); ++arrangementIndex){
            string arrangementCaseName = caseName + "/" + arrangements[arrangementIndex] ;
            paths.createOutputDirectory(parentFolder,arrangementCaseName) ;
            ofstream comparison_info(paths.getOutputDirectory(parentFolder,arrangementCaseName) / "P1_DOM_comparison.csv") ;
            writeComparisonHeader(comparison_info) ;
            size_t startIndex = arrangementIndex*resultsPerArrangement ;
            for(size_t i=0; i<resultsPerArrangement; ++i){ writeComparisonResult(comparison_info,p1Results_[startIndex+i],domResults_[startIndex+i]) ;}
        }
    }

    private:

    template<class DiagnosticsType>
    DOMP1HeatExchangerTemperatureDifferenceTestResult collectResult(string parameterName, double parameterValue, double runtime, double a, double sigmaS, double hotPipeTemperature, double coldPipeTemperature, double outerWallTemperature, double initialMediumTemperature, int totalIterationCount, DiagnosticsType& diagnostics){
        DOMP1HeatExchangerTemperatureDifferenceTestResult result ;
        result.parameterName = parameterName ;
        result.parameterValue = parameterValue ;
        result.runtime = runtime ;
        result.absorptionCoefficient = a ; result.scatteringCoefficient = sigmaS ; result.hotPipeTemperature = hotPipeTemperature ; result.coldPipeTemperature = coldPipeTemperature ; result.outerWallTemperature = outerWallTemperature ; result.initialMediumTemperature = initialMediumTemperature ; result.totalIterationCount = totalIterationCount ;
        double irradiationScale = 4.0*5.670374419e-8*pow(hotPipeTemperature,4), heatFluxScale = 5.670374419e-8*pow(hotPipeTemperature,4), temperatureScale = hotPipeTemperature-coldPipeTemperature ;
        result.minimumDimensionlessTemperature = (diagnostics->minimumTemperature()-coldPipeTemperature)/temperatureScale ; result.maximumDimensionlessTemperature = (diagnostics->maximumTemperature()-coldPipeTemperature)/temperatureScale ;
        result.minimumDimensionlessIrradiation = diagnostics->minimumIrradiation()/irradiationScale ; result.maximumDimensionlessIrradiation = diagnostics->maximumIrradiation()/irradiationScale ;
        result.minimumDimensionlessHeatFluxMagnitude = diagnostics->minimumHeatFluxMagnitude()/heatFluxScale ; result.maximumDimensionlessHeatFluxMagnitude = diagnostics->maximumHeatFluxMagnitude()/heatFluxScale ;
        result.minimumTemperatureLocation = diagnostics->minimumTemperatureLocation() ; result.maximumTemperatureLocation = diagnostics->maximumTemperatureLocation() ; result.minimumIrradiationLocation = diagnostics->minimumIrradiationLocation() ; result.maximumIrradiationLocation = diagnostics->maximumIrradiationLocation() ; result.minimumHeatFluxMagnitudeLocation = diagnostics->minimumHeatFluxMagnitudeLocation() ; result.maximumHeatFluxMagnitudeLocation = diagnostics->maximumHeatFluxMagnitudeLocation() ;
        result.totalHotPipeHeatRelease = diagnostics->totalHotPipeHeatRelease() ;
        result.totalColdPipeHeatAbsorption = diagnostics->totalColdPipeHeatAbsorption() ;
        result.totalOuterWallHeatLoss = diagnostics->totalOuterWallHeatLoss() ;
        result.heatRecoveryRatio = diagnostics->heatRecoveryRatio() ;
        result.wallLossRatio = diagnostics->wallLossRatio() ;
        result.meanColdPipeHeatLoad = diagnostics->meanColdPipeHeatLoad() ;
        result.standardDeviationColdPipeHeatLoad = diagnostics->standardDeviationColdPipeHeatLoad() ;
        result.coefficientOfVariationColdPipeHeatLoad = diagnostics->coefficientOfVariationColdPipeHeatLoad() ;
        result.minimumColdPipeHeatLoad = diagnostics->minimumColdPipeHeatLoad() ;
        result.maximumColdPipeHeatLoad = diagnostics->maximumColdPipeHeatLoad() ;
        result.minimumTemperature = diagnostics->minimumTemperature() ;
        result.maximumTemperature = diagnostics->maximumTemperature() ;
        result.averageTemperature = diagnostics->averageTemperature() ;
        result.standardDeviationTemperature = diagnostics->standardDeviationTemperature() ;
        result.minimumIrradiation = diagnostics->minimumIrradiation() ;
        result.maximumIrradiation = diagnostics->maximumIrradiation() ;
        result.averageIrradiation = diagnostics->averageIrradiation() ;
        result.totalRadiativeSourceTerm = diagnostics->totalRadiativeSourceTerm() ;
        result.energyBalanceResidual = diagnostics->energyBalanceResidual() ;
        result.energyBalanceError = diagnostics->energyBalanceError() ;
        result.hotPipeHeatRelease = diagnostics->hotPipeHeatRelease() ;
        result.coldPipeHeatAbsorption = diagnostics->coldPipeHeatAbsorption() ;
        result.outerWallHeatLoss = diagnostics->outerWallHeatLoss() ;
        result.averageWallIrradiation = diagnostics->averageWallIrradiation() ;
        result.averageWallHeatFlux = diagnostics->averageWallHeatFlux() ;
        result.minimumHeatFluxMagnitude = diagnostics->minimumHeatFluxMagnitude() ;
        result.maximumHeatFluxMagnitude = diagnostics->maximumHeatFluxMagnitude() ;
        return result ;
    }

    void writeSummaryHeader(ofstream& out){
        out << "parameter_name,parameter_value,absorption_coefficient,scattering_coefficient,hot_pipe_temperature,cold_pipe_temperature,outer_wall_temperature,initial_medium_temperature,minimum_irradiation,minimum_dimensionless_irradiation,minimum_irradiation_x,minimum_irradiation_y,minimum_irradiation_z,maximum_irradiation,maximum_dimensionless_irradiation,maximum_irradiation_x,maximum_irradiation_y,maximum_irradiation_z,minimum_temperature,minimum_dimensionless_temperature,minimum_temperature_x,minimum_temperature_y,minimum_temperature_z,maximum_temperature,maximum_dimensionless_temperature,maximum_temperature_x,maximum_temperature_y,maximum_temperature_z,minimum_heat_flux_magnitude,minimum_dimensionless_heat_flux_magnitude,minimum_heat_flux_x,minimum_heat_flux_y,minimum_heat_flux_z,maximum_heat_flux_magnitude,maximum_dimensionless_heat_flux_magnitude,maximum_heat_flux_x,maximum_heat_flux_y,maximum_heat_flux_z,total_hot_pipe_heat_release,total_cold_pipe_heat_absorption,total_outer_wall_heat_loss,heat_recovery_ratio,wall_loss_ratio,mean_cold_pipe_heat_load,standard_deviation_cold_pipe_heat_load,coefficient_of_variation_cold_pipe_heat_load,minimum_cold_pipe_heat_load,maximum_cold_pipe_heat_load,average_temperature,average_irradiation,total_radiative_source_term,energy_balance_residual,energy_balance_error,runtime,total_iteration_count" << endl ;
    }

    void writeSummaryResult(ofstream& out, const DOMP1HeatExchangerTemperatureDifferenceTestResult& result){

    out << result.parameterName << ","
        << result.parameterValue << ","
        << result.absorptionCoefficient << ","
        << result.scatteringCoefficient << ","
        << result.hotPipeTemperature << ","
        << result.coldPipeTemperature << ","
        << result.outerWallTemperature << ","
        << result.initialMediumTemperature << ","
        << result.minimumIrradiation << ","
        << result.minimumDimensionlessIrradiation << ","
        << result.minimumIrradiationLocation[0] << ","
        << result.minimumIrradiationLocation[1] << ","
        << result.minimumIrradiationLocation[2] << ","
        << result.maximumIrradiation << ","
        << result.maximumDimensionlessIrradiation << ","
        << result.maximumIrradiationLocation[0] << ","
        << result.maximumIrradiationLocation[1] << ","
        << result.maximumIrradiationLocation[2] << ","
        << result.minimumTemperature << ","
        << result.minimumDimensionlessTemperature << ","
        << result.minimumTemperatureLocation[0] << ","
        << result.minimumTemperatureLocation[1] << ","
        << result.minimumTemperatureLocation[2] << ","
        << result.maximumTemperature << ","
        << result.maximumDimensionlessTemperature << ","
        << result.maximumTemperatureLocation[0] << ","
        << result.maximumTemperatureLocation[1] << ","
        << result.maximumTemperatureLocation[2] << ","
        << result.minimumHeatFluxMagnitude << ","
        << result.minimumDimensionlessHeatFluxMagnitude << ","
        << result.minimumHeatFluxMagnitudeLocation[0] << ","
        << result.minimumHeatFluxMagnitudeLocation[1] << ","
        << result.minimumHeatFluxMagnitudeLocation[2] << ","
        << result.maximumHeatFluxMagnitude << ","
        << result.maximumDimensionlessHeatFluxMagnitude << ","
        << result.maximumHeatFluxMagnitudeLocation[0] << ","
        << result.maximumHeatFluxMagnitudeLocation[1] << ","
        << result.maximumHeatFluxMagnitudeLocation[2] << ","
        << result.totalHotPipeHeatRelease << ","
        << result.totalColdPipeHeatAbsorption << ","
        << result.totalOuterWallHeatLoss << ","
        << result.heatRecoveryRatio << ","
        << result.wallLossRatio << ","
        << result.meanColdPipeHeatLoad << ","
        << result.standardDeviationColdPipeHeatLoad << ","
        << result.coefficientOfVariationColdPipeHeatLoad << ","
        << result.minimumColdPipeHeatLoad << ","
        << result.maximumColdPipeHeatLoad << ","
        << result.averageTemperature << ","
        << result.averageIrradiation << ","
        << result.totalRadiativeSourceTerm << ","
        << result.energyBalanceResidual << ","
        << result.energyBalanceError << ","
        << result.runtime << ","
        << result.totalIterationCount
        << endl ;
    }

    void writePipeResults(const filesystem::path& outputDirectory, const string& modelName, const DOMP1HeatExchangerTemperatureDifferenceTestResult& result){
        ofstream pipe_info(outputDirectory / (modelName + "_pipe_diagnostics.csv"), ios::app) ;
        if(pipe_info.tellp()==0){ pipe_info << "parameter_name,parameter_value,absorption_coefficient,scattering_coefficient,hot_pipe_temperature,cold_pipe_temperature,outer_wall_temperature,initial_medium_temperature,pipe_name,pipe_type,heat_transfer,average_irradiation,average_wall_heat_flux" << endl ;}
        for(const auto& [pipeName,heatTransfer]: result.hotPipeHeatRelease){ pipe_info << result.parameterName << "," << result.parameterValue << "," << result.absorptionCoefficient << "," << result.scatteringCoefficient << "," << result.hotPipeTemperature << "," << result.coldPipeTemperature << "," << result.outerWallTemperature << "," << result.initialMediumTemperature << "," << pipeName << ",hot," << heatTransfer << "," << result.averageWallIrradiation.at(pipeName) << "," << result.averageWallHeatFlux.at(pipeName) << endl ;}
        for(const auto& [pipeName,heatTransfer]: result.coldPipeHeatAbsorption){ pipe_info << result.parameterName << "," << result.parameterValue << "," << result.absorptionCoefficient << "," << result.scatteringCoefficient << "," << result.hotPipeTemperature << "," << result.coldPipeTemperature << "," << result.outerWallTemperature << "," << result.initialMediumTemperature << "," << pipeName << ",cold," << heatTransfer << "," << result.averageWallIrradiation.at(pipeName) << "," << result.averageWallHeatFlux.at(pipeName) << endl ;}
        for(const auto& [wallName,heatTransfer]: result.outerWallHeatLoss){ pipe_info << result.parameterName << "," << result.parameterValue << "," << result.absorptionCoefficient << "," << result.scatteringCoefficient << "," << result.hotPipeTemperature << "," << result.coldPipeTemperature << "," << result.outerWallTemperature << "," << result.initialMediumTemperature << "," << wallName << ",outer_wall," << heatTransfer << "," << result.averageWallIrradiation.at(wallName) << "," << result.averageWallHeatFlux.at(wallName) << endl ;}
    }


    int readIterationCount(const filesystem::path& directory){
        int maximumIterationCount = 0 ;
        if(!filesystem::exists(directory)){ return maximumIterationCount ;}
        for(const auto& entry: filesystem::recursive_directory_iterator(directory)){
            if(!entry.is_regular_file()){ continue ;}
            string filename = entry.path().filename().string() ;
            if(filename.rfind("finalRedidual",0)!=0 && filename.rfind("finalResidual",0)!=0){ continue ;}
            ifstream in(entry.path()) ; string line ; int dataRows = -1 ;
            while(getline(in,line)){ ++dataRows ;}
            maximumIterationCount = max(maximumIterationCount,max(dataRows,0)) ;
        }
        return maximumIterationCount ;
    }

    template<class DiagnosticsType>
    void writeExtendedDiagnostics(const filesystem::path& outputDirectory, const string& caseName, DiagnosticsType& diagnostics, double pitch, double a, double sigmaS, double hotPipeTemperature, double coldPipeTemperature, double outerWallTemperature, double initialMediumTemperature){
        const double Lx = 1.5, Ly = 1.5, Lz = 0.01, tubeDiameter = 0.10, temperatureScale = hotPipeTemperature-coldPipeTemperature, irradiationScale = 4.0*5.670374419e-8*pow(hotPipeTemperature,4), heatFluxScale = 5.670374419e-8*pow(hotPipeTemperature,4) ;
        filesystem::path caseDirectory = outputDirectory / "ExtendedDiagnostics" / caseName ; filesystem::create_directories(caseDirectory) ;

        ofstream midpointFile(caseDirectory / "midpoint_diagnostics.csv") ;
        midpointFile << "case_name,absorption_coefficient,scattering_coefficient,hot_pipe_temperature,cold_pipe_temperature,outer_wall_temperature,initial_medium_temperature,midpoint_id,target_x,target_y,sampled_x,sampled_y,temperature,irradiation,heat_flux_magnitude,heat_flux_x,heat_flux_y,radiative_source_term" << endl ;
        double start = 0.5*(Lx-5.0*pitch) ;
        for(int j=0; j<6; ++j){ for(int i=0; i<5; ++i){ double x = start+(i+0.5)*pitch, y = start+j*pitch ; array<double,10> s = diagnostics->pointSample(x,y,0.5*Lz) ; midpointFile << caseName << "," << a << "," << sigmaS << "," << hotPipeTemperature << "," << coldPipeTemperature << "," << outerWallTemperature << "," << initialMediumTemperature << ",H_" << i+1 << "_" << j+1 << "," << x << "," << y << "," << s[0] << "," << s[1] << "," << s[3] << "," << s[4] << "," << s[5] << "," << s[6] << "," << s[7] << "," << s[9] << endl ;}}
        for(int j=0; j<5; ++j){ for(int i=0; i<6; ++i){ double x = start+i*pitch, y = start+(j+0.5)*pitch ; array<double,10> s = diagnostics->pointSample(x,y,0.5*Lz) ; midpointFile << caseName << "," << a << "," << sigmaS << "," << hotPipeTemperature << "," << coldPipeTemperature << "," << outerWallTemperature << "," << initialMediumTemperature << ",V_" << i+1 << "_" << j+1 << "," << x << "," << y << "," << s[0] << "," << s[1] << "," << s[3] << "," << s[4] << "," << s[5] << "," << s[6] << "," << s[7] << "," << s[9] << endl ;}}

        for(const string& patchName: vector<string>{"north","south","east","west"}){
            ofstream wallFile(caseDirectory / (patchName+"_wall_profile.csv")) ;
            wallFile << "case_name,absorption_coefficient,scattering_coefficient,hot_pipe_temperature,cold_pipe_temperature,outer_wall_temperature,initial_medium_temperature,position_over_L,x,y,dimensionless_temperature,dimensionless_irradiation,dimensionless_heat_flux_magnitude,normal_wall_heat_flux,dimensionless_normal_wall_heat_flux,heat_flux_x,heat_flux_y,radiative_source_term" << endl ;
            for(const array<double,11>& s: diagnostics->wallProfile(patchName,heatFluxScale)){ double position = (patchName=="north" || patchName=="south") ? s[0]/Lx : s[1]/Ly ; wallFile << caseName << "," << a << "," << sigmaS << "," << hotPipeTemperature << "," << coldPipeTemperature << "," << outerWallTemperature << "," << initialMediumTemperature << "," << position << "," << s[0] << "," << s[1] << "," << (s[3]-coldPipeTemperature)/temperatureScale << "," << s[4]/irradiationScale << "," << s[5]/heatFluxScale << "," << s[6] << "," << s[10] << "," << s[7] << "," << s[8] << "," << s[9] << endl ;}
        }

        vector<pair<string,double>> gaps = {{"lower",start+0.5*pitch},{"central",start+2.5*pitch},{"upper",start+4.5*pitch}} ;
        for(const auto& [gapName,y]: gaps){
            ofstream profileFile(caseDirectory / (gapName+"_inter_row_profile.csv")) ;
            profileFile << "case_name,absorption_coefficient,scattering_coefficient,hot_pipe_temperature,cold_pipe_temperature,outer_wall_temperature,initial_medium_temperature,x_over_L,x,y,dimensionless_temperature,dimensionless_irradiation,dimensionless_heat_flux_magnitude,dimensionless_heat_flux_x,radiative_source_term" << endl ;
            for(const array<double,10>& s: diagnostics->lineProfile(y,0.5*Lz)){ profileFile << caseName << "," << a << "," << sigmaS << "," << hotPipeTemperature << "," << coldPipeTemperature << "," << outerWallTemperature << "," << initialMediumTemperature << "," << s[0]/Lx << "," << s[0] << "," << s[1] << "," << (s[3]-coldPipeTemperature)/temperatureScale << "," << s[4]/irradiationScale << "," << s[5]/heatFluxScale << "," << s[6]/heatFluxScale << "," << s[9] << endl ;}
        }

        ofstream contourFile(caseDirectory / "cell_contour_data.csv") ;
        contourFile << "case_name,absorption_coefficient,scattering_coefficient,hot_pipe_temperature,cold_pipe_temperature,outer_wall_temperature,initial_medium_temperature,x,y,z,dimensionless_temperature,dimensionless_irradiation,heat_flux_x,heat_flux_y,heat_flux_z,dimensionless_heat_flux_magnitude,radiative_source_term" << endl ;
        for(const array<double,10>& s: diagnostics->cellContourData()){ contourFile << caseName << "," << a << "," << sigmaS << "," << hotPipeTemperature << "," << coldPipeTemperature << "," << outerWallTemperature << "," << initialMediumTemperature << "," << s[0] << "," << s[1] << "," << s[2] << "," << (s[3]-coldPipeTemperature)/temperatureScale << "," << s[4]/irradiationScale << "," << s[6] << "," << s[7] << "," << s[8] << "," << s[5]/heatFluxScale << "," << s[9] << endl ;}
    }

    double relativeDifference(double p1Value, double domValue){
        if(abs(domValue)<numeric_limits<double>::epsilon()){ return abs(p1Value-domValue) ;}
        return abs(p1Value-domValue)/abs(domValue) ;
    }

    void writeComparisonHeader(ofstream& out){
        out << "parameter_name,parameter_value,p1_total_hot_pipe_heat_release,dom_total_hot_pipe_heat_release,relative_difference_total_hot_pipe_heat_release,p1_total_cold_pipe_heat_absorption,dom_total_cold_pipe_heat_absorption,relative_difference_total_cold_pipe_heat_absorption,p1_total_outer_wall_heat_loss,dom_total_outer_wall_heat_loss,relative_difference_total_outer_wall_heat_loss,p1_heat_recovery_ratio,dom_heat_recovery_ratio,relative_difference_heat_recovery_ratio,p1_wall_loss_ratio,dom_wall_loss_ratio,relative_difference_wall_loss_ratio,p1_cold_pipe_heat_load_cv,dom_cold_pipe_heat_load_cv,relative_difference_cold_pipe_heat_load_cv,p1_average_temperature,dom_average_temperature,relative_difference_average_temperature,p1_average_irradiation,dom_average_irradiation,relative_difference_average_irradiation,p1_energy_balance_error,dom_energy_balance_error,p1_runtime,dom_runtime" << endl ;
    }

    void writeComparisonResult(ofstream& out, const DOMP1HeatExchangerTemperatureDifferenceTestResult& p1Result, const DOMP1HeatExchangerTemperatureDifferenceTestResult& domResult){
        out << p1Result.parameterName << "," << p1Result.parameterValue << "," << p1Result.totalHotPipeHeatRelease << "," << domResult.totalHotPipeHeatRelease << "," << relativeDifference(p1Result.totalHotPipeHeatRelease,domResult.totalHotPipeHeatRelease) << "," << p1Result.totalColdPipeHeatAbsorption << "," << domResult.totalColdPipeHeatAbsorption << "," << relativeDifference(p1Result.totalColdPipeHeatAbsorption,domResult.totalColdPipeHeatAbsorption) << "," << p1Result.totalOuterWallHeatLoss << "," << domResult.totalOuterWallHeatLoss << "," << relativeDifference(p1Result.totalOuterWallHeatLoss,domResult.totalOuterWallHeatLoss) << "," << p1Result.heatRecoveryRatio << "," << domResult.heatRecoveryRatio << "," << relativeDifference(p1Result.heatRecoveryRatio,domResult.heatRecoveryRatio) << "," << p1Result.wallLossRatio << "," << domResult.wallLossRatio << "," << relativeDifference(p1Result.wallLossRatio,domResult.wallLossRatio) << "," << p1Result.coefficientOfVariationColdPipeHeatLoad << "," << domResult.coefficientOfVariationColdPipeHeatLoad << "," << relativeDifference(p1Result.coefficientOfVariationColdPipeHeatLoad,domResult.coefficientOfVariationColdPipeHeatLoad) << "," << p1Result.averageTemperature << "," << domResult.averageTemperature << "," << relativeDifference(p1Result.averageTemperature,domResult.averageTemperature) << "," << p1Result.averageIrradiation << "," << domResult.averageIrradiation << "," << relativeDifference(p1Result.averageIrradiation,domResult.averageIrradiation) << "," << p1Result.energyBalanceError << "," << domResult.energyBalanceError << "," << p1Result.runtime << "," << domResult.runtime << endl ;
    }


};

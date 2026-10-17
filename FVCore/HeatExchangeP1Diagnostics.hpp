# pragma once

# include <iostream>
# include <vector>
# include <array>
# include <cmath>
# include <map>
# include <string>
# include <algorithm>
# include <limits>
# include <memory>
# include <stdexcept>

# include "FaceAddressedMesh3D.hpp"
# include "Patch.hpp"
# include "Field.hpp"
# include "FVMatrix.hpp"
# include "ScalarProperty.hpp"

using namespace std ;

struct P1HeatExchangerInternalHeatStat{
    int cellIndex_ = -1 ;
    double x_ = 0, y_ = 0, z_ = 0, magnitude_ = 0 ;
} ;

struct P1HeatExchangerWallHeatStat{
    int faceIndex_ = -1 ;
    double heatFlux_ = 0, heatTransfer_ = 0, irradiation_ = 0 ;
} ;

class HeatExchangeP1Diagnostics{

    private:

        const FaceAddressedMesh3D& mesh_ ;
        FVMatrix& fvMatrixG_ ;
        FVMatrix& fvMatrixT_ ;
        Field& fieldG_ ;
        Field& fieldT_ ;
        const ScalarProperty& gamma_ ;

        const vector<string> hotPipePatchNames_ ;
        const vector<string> coldPipePatchNames_ ;
        const vector<string> outerWallPatchNames_ ;

        vector<P1HeatExchangerInternalHeatStat> internalHeatFlux_ ;
        map<string,vector<P1HeatExchangerWallHeatStat>> wallHeatData_ ;
        vector<double> internalIrradiation_ ;
        vector<double> radiativeSourceTerm_ ;

        map<string,double> averageWallHeatFlux_ ;
        map<string,double> totalWallHeatTransfer_ ;
        map<string,double> averageWallIrradiation_ ;
        map<string,double> totalIncidentRadiation_ ;
        map<string,double> averageWallTemperature_ ;
        map<string,double> wallArea_ ;

        map<string,double> hotPipeHeatRelease_ ;
        map<string,double> coldPipeHeatAbsorption_ ;
        map<string,double> outerWallHeatLoss_ ;

        double totalHotPipeHeatRelease_ = 0 ;
        double totalColdPipeHeatAbsorption_ = 0 ;
        double totalOuterWallHeatLoss_ = 0 ;
        double heatRecoveryRatio_ = 0 ;
        double wallLossRatio_ = 0 ;

        double meanColdPipeHeatLoad_ = 0 ;
        double standardDeviationColdPipeHeatLoad_ = 0 ;
        double coefficientOfVariationColdPipeHeatLoad_ = 0 ;
        double minimumColdPipeHeatLoad_ = 0 ;
        double maximumColdPipeHeatLoad_ = 0 ;

        double minimumTemperature_ = 0 ;
        double maximumTemperature_ = 0 ;
        double averageTemperature_ = 0 ;
        double standardDeviationTemperature_ = 0 ;

        double minimumIrradiation_ = 0 ;
        double maximumIrradiation_ = 0 ;
        double averageIrradiation_ = 0 ;

        double totalRadiativeSourceTerm_ = 0 ;
        double energyBalanceResidual_ = 0 ;
        double energyBalanceError_ = 0 ;

        double sigma_ = 5.670374419e-8 ;

        double minimumHeatFluxMagnitude_ = 0, maximumHeatFluxMagnitude_ = 0 ;
        array<double,3> minimumTemperatureLocation_ = {0,0,0}, maximumTemperatureLocation_ = {0,0,0}, minimumIrradiationLocation_ = {0,0,0}, maximumIrradiationLocation_ = {0,0,0}, minimumHeatFluxMagnitudeLocation_ = {0,0,0}, maximumHeatFluxMagnitudeLocation_ = {0,0,0} ;


    public:

        HeatExchangeP1Diagnostics(const FaceAddressedMesh3D& mesh, FVMatrix& fvMatrixG, FVMatrix& fvMatrixT, Field& fieldG, Field& fieldT, const ScalarProperty& gamma, const vector<string>& hotPipePatchNames, const vector<string>& coldPipePatchNames, const vector<string>& outerWallPatchNames):mesh_(mesh),
                                                                                                                                                                                                                                                               fvMatrixG_(fvMatrixG),
                                                                                                                                                                                                                                                               fvMatrixT_(fvMatrixT),
                                                                                                                                                                                                                                                               fieldG_(fieldG),
                                                                                                                                                                                                                                                               fieldT_(fieldT),
                                                                                                                                                                                                                                                               gamma_(gamma),
                                                                                                                                                                                                                                                               hotPipePatchNames_(hotPipePatchNames),
                                                                                                                                                                                                                                                               coldPipePatchNames_(coldPipePatchNames),
                                                                                                                                                                                                                                                               outerWallPatchNames_(outerWallPatchNames)
        {}

        vector<P1HeatExchangerInternalHeatStat>& internalHeatFlux(){ return internalHeatFlux_ ;}
        const vector<P1HeatExchangerInternalHeatStat>& internalHeatFlux() const{ return internalHeatFlux_ ;}

        map<string,vector<P1HeatExchangerWallHeatStat>>& wallHeatData(){ return wallHeatData_ ;}
        const map<string,vector<P1HeatExchangerWallHeatStat>>& wallHeatData() const{ return wallHeatData_ ;}

        vector<double>& internalIrradiation(){ return internalIrradiation_ ;}
        const vector<double>& internalIrradiation() const{ return internalIrradiation_ ;}

        vector<double>& radiativeSourceTerm(){ return radiativeSourceTerm_ ;}
        const vector<double>& radiativeSourceTerm() const{ return radiativeSourceTerm_ ;}

        map<string,double>& averageWallHeatFlux(){ return averageWallHeatFlux_ ;}
        const map<string,double>& averageWallHeatFlux() const{ return averageWallHeatFlux_ ;}

        map<string,double>& totalWallHeatTransfer(){ return totalWallHeatTransfer_ ;}
        const map<string,double>& totalWallHeatTransfer() const{ return totalWallHeatTransfer_ ;}

        map<string,double>& averageWallIrradiation(){ return averageWallIrradiation_ ;}
        const map<string,double>& averageWallIrradiation() const{ return averageWallIrradiation_ ;}

        map<string,double>& totalIncidentRadiation(){ return totalIncidentRadiation_ ;}
        const map<string,double>& totalIncidentRadiation() const{ return totalIncidentRadiation_ ;}

        map<string,double>& averageWallTemperature(){ return averageWallTemperature_ ;}
        const map<string,double>& averageWallTemperature() const{ return averageWallTemperature_ ;}

        map<string,double>& wallArea(){ return wallArea_ ;}
        const map<string,double>& wallArea() const{ return wallArea_ ;}

        map<string,double>& hotPipeHeatRelease(){ return hotPipeHeatRelease_ ;}
        const map<string,double>& hotPipeHeatRelease() const{ return hotPipeHeatRelease_ ;}

        map<string,double>& coldPipeHeatAbsorption(){ return coldPipeHeatAbsorption_ ;}
        const map<string,double>& coldPipeHeatAbsorption() const{ return coldPipeHeatAbsorption_ ;}

        map<string,double>& outerWallHeatLoss(){ return outerWallHeatLoss_ ;}
        const map<string,double>& outerWallHeatLoss() const{ return outerWallHeatLoss_ ;}

        double totalHotPipeHeatRelease() const{ return totalHotPipeHeatRelease_ ;}
        double totalColdPipeHeatAbsorption() const{ return totalColdPipeHeatAbsorption_ ;}
        double totalOuterWallHeatLoss() const{ return totalOuterWallHeatLoss_ ;}
        double heatRecoveryRatio() const{ return heatRecoveryRatio_ ;}
        double wallLossRatio() const{ return wallLossRatio_ ;}

        double meanColdPipeHeatLoad() const{ return meanColdPipeHeatLoad_ ;}
        double standardDeviationColdPipeHeatLoad() const{ return standardDeviationColdPipeHeatLoad_ ;}
        double coefficientOfVariationColdPipeHeatLoad() const{ return coefficientOfVariationColdPipeHeatLoad_ ;}
        double minimumColdPipeHeatLoad() const{ return minimumColdPipeHeatLoad_ ;}
        double maximumColdPipeHeatLoad() const{ return maximumColdPipeHeatLoad_ ;}

        double minimumTemperature() const{ return minimumTemperature_ ;}
        double maximumTemperature() const{ return maximumTemperature_ ;}
        double averageTemperature() const{ return averageTemperature_ ;}
        double standardDeviationTemperature() const{ return standardDeviationTemperature_ ;}

        double minimumIrradiation() const{ return minimumIrradiation_ ;}
        double maximumIrradiation() const{ return maximumIrradiation_ ;}
        double averageIrradiation() const{ return averageIrradiation_ ;}

        double totalRadiativeSourceTerm() const{ return totalRadiativeSourceTerm_ ;}
        double energyBalanceResidual() const{ return energyBalanceResidual_ ;}
        double energyBalanceError() const{ return energyBalanceError_ ;}

        void calculateInternalHeatFlux(){

            internalHeatFlux_.assign(mesh_.numCells(), P1HeatExchangerInternalHeatStat{}) ;

            for(int cellIndex=0; cellIndex<mesh_.numCells(); ++cellIndex){
                double gradX = 0, gradY = 0, gradZ = 0 ;
                double cellVolume = mesh_.cellVolume(cellIndex) ;

                for(int faceIndex: mesh_.cellFaces(cellIndex)){
                    array<int,2> ownerNeighbour = mesh_.faceOwnerNeighbour(faceIndex) ;
                    array<double,3> faceAreaVector = mesh_.faceAreaVector(faceIndex) ;
                    if(ownerNeighbour[0] != cellIndex){ faceAreaVector = {-faceAreaVector[0],-faceAreaVector[1],-faceAreaVector[2]} ;}

                    double Gf = 0 ;
                    if(ownerNeighbour[1] != -1){ Gf = 0.5*(fvMatrixG_.sys().X()(ownerNeighbour[0]) + fvMatrixG_.sys().X()(ownerNeighbour[1])) ;}
                    else{ Gf = boundaryValue(fieldG_,fvMatrixG_,faceIndex) ;}

                    gradX += Gf*faceAreaVector[0]/cellVolume ;
                    gradY += Gf*faceAreaVector[1]/cellVolume ;
                    gradZ += Gf*faceAreaVector[2]/cellVolume ;
                }

                internalHeatFlux_[cellIndex].cellIndex_ = cellIndex ;
                internalHeatFlux_[cellIndex].x_ = -gamma_(cellIndex)*gradX ;
                internalHeatFlux_[cellIndex].y_ = -gamma_(cellIndex)*gradY ;
                internalHeatFlux_[cellIndex].z_ = -gamma_(cellIndex)*gradZ ;
                internalHeatFlux_[cellIndex].magnitude_ = sqrt(internalHeatFlux_[cellIndex].x_*internalHeatFlux_[cellIndex].x_ + internalHeatFlux_[cellIndex].y_*internalHeatFlux_[cellIndex].y_ + internalHeatFlux_[cellIndex].z_*internalHeatFlux_[cellIndex].z_) ;
            }
        }

        void calculateWallDiagnostics(){

        wallHeatData_.clear() ; averageWallHeatFlux_.clear() ; totalWallHeatTransfer_.clear() ; averageWallIrradiation_.clear() ; totalIncidentRadiation_.clear() ; averageWallTemperature_.clear() ; wallArea_.clear() ;

        for(Patch p: mesh_.boundaryPatches()){

            double totalHeatTransfer = 0, totalIrradiation = 0, totalTemperature = 0, totalArea = 0 ;
            wallHeatData_[p.name()] = {} ;

            BoundaryCondition& GBoundaryCondition = *fieldG_.boundary()[p.index()] ;
            BoundaryCondition& TBoundaryCondition = *fieldT_.boundary()[p.index()] ;

            for(int faceIndex: p.faces()){

                int ownerCell = mesh_.faceOwnerNeighbour(faceIndex)[0] ;
                double area = mesh_.faceArea(faceIndex) ;
                double distance = distanceFaceToCell(faceIndex) ;

                double Gf = boundaryFaceValue(fieldG_,fvMatrixG_,p.index(),faceIndex) ;
                double Tw = boundaryFaceValue(fieldT_,fvMatrixT_,p.index(),faceIndex) ;

                double q = 0.0 ;

                if(GBoundaryCondition.typeName()=="fixedgradient"){
                    double gradient = GBoundaryCondition.boundaryValues().at(faceIndex) ;
                    q = gamma_(ownerCell)*gradient ;
                }
                else{
                    q = gamma_(ownerCell)*(Gf-fvMatrixG_.sys().X()(ownerCell))/distance ;
                }

                double Q = q*area ;
                double wallIrradiation = Gf/4.0-q/2.0 ;

                wallHeatData_[p.name()].push_back({faceIndex,q,Q,wallIrradiation}) ;

                totalHeatTransfer += Q ;
                totalIrradiation += wallIrradiation*area ;
                totalTemperature += Tw*area ;
                totalArea += area ;
            }

            if(totalArea<=0){
                throw runtime_error("Cannot calculate P1 heat exchanger diagnostics for zero-area patch: "+p.name()) ;
            }

            wallArea_[p.name()] = totalArea ;
            averageWallHeatFlux_[p.name()] = totalHeatTransfer/totalArea ;
            totalWallHeatTransfer_[p.name()] = totalHeatTransfer ;
            averageWallIrradiation_[p.name()] = totalIrradiation/totalArea ;
            totalIncidentRadiation_[p.name()] = totalIrradiation ;
            averageWallTemperature_[p.name()] = totalTemperature/totalArea ;
        }
    }
    
        void calculateInternalIrradiationStatistics(){

            internalIrradiation_.assign(mesh_.numCells(), 0.0) ;
            minimumIrradiation_ = numeric_limits<double>::max() ; maximumIrradiation_ = -numeric_limits<double>::max() ; averageIrradiation_ = 0 ;
            double totalVolume = 0 ;

            for(int i=0; i<mesh_.numCells(); ++i){
                internalIrradiation_[i] = fvMatrixG_.sys().X()(i) ;
                double volume = mesh_.cellVolume(i) ;
                minimumIrradiation_ = min(minimumIrradiation_,internalIrradiation_[i]) ; maximumIrradiation_ = max(maximumIrradiation_,internalIrradiation_[i]) ;
                averageIrradiation_ += internalIrradiation_[i]*volume ; totalVolume += volume ;
            }
            if(totalVolume > 0){ averageIrradiation_ /= totalVolume ;}
        }

        void calculateTemperatureStatistics(){

            minimumTemperature_ = numeric_limits<double>::max() ; maximumTemperature_ = -numeric_limits<double>::max() ; averageTemperature_ = 0 ; standardDeviationTemperature_ = 0 ;
            double totalVolume = 0 ;

            for(int i=0; i<mesh_.numCells(); ++i){
                double T = fvMatrixT_.sys().X()(i), volume = mesh_.cellVolume(i) ;
                minimumTemperature_ = min(minimumTemperature_,T) ; maximumTemperature_ = max(maximumTemperature_,T) ; averageTemperature_ += T*volume ; totalVolume += volume ;
            }
            if(totalVolume > 0){ averageTemperature_ /= totalVolume ;}
            for(int i=0; i<mesh_.numCells(); ++i){ double dT = fvMatrixT_.sys().X()(i)-averageTemperature_ ; standardDeviationTemperature_ += dT*dT*mesh_.cellVolume(i) ;}
            if(totalVolume > 0){ standardDeviationTemperature_ = sqrt(standardDeviationTemperature_/totalVolume) ;}
        }

        void calculateRadiativeSourceTerm(ScalarProperty& a){

            radiativeSourceTerm_.assign(mesh_.numCells(), 0.0) ; totalRadiativeSourceTerm_ = 0 ;
            for(int i=0; i<mesh_.numCells(); ++i){
                radiativeSourceTerm_[i] = a(i)*(4*sigma_*pow(fvMatrixT_.sys().X()(i),4)-fvMatrixG_.sys().X()(i)) ;
                totalRadiativeSourceTerm_ += radiativeSourceTerm_[i]*mesh_.cellVolume(i) ;
            }
        }

        void calculateHeatExchangerPerformance(){

            hotPipeHeatRelease_.clear() ; coldPipeHeatAbsorption_.clear() ; outerWallHeatLoss_.clear() ;
            totalHotPipeHeatRelease_ = 0 ; totalColdPipeHeatAbsorption_ = 0 ; totalOuterWallHeatLoss_ = 0 ;

            for(const string& patchName: hotPipePatchNames_){ validatePatchName(patchName) ; hotPipeHeatRelease_[patchName] = totalWallHeatTransfer_.at(patchName) ; totalHotPipeHeatRelease_ += hotPipeHeatRelease_[patchName] ;}
            for(const string& patchName: coldPipePatchNames_){ validatePatchName(patchName) ; coldPipeHeatAbsorption_[patchName] = -totalWallHeatTransfer_.at(patchName) ; totalColdPipeHeatAbsorption_ += coldPipeHeatAbsorption_[patchName] ;}
            for(const string& patchName: outerWallPatchNames_){ validatePatchName(patchName) ; outerWallHeatLoss_[patchName] = -totalWallHeatTransfer_.at(patchName) ; totalOuterWallHeatLoss_ += outerWallHeatLoss_[patchName] ;}

            if(abs(totalHotPipeHeatRelease_) > 1e-14){ heatRecoveryRatio_ = totalColdPipeHeatAbsorption_/totalHotPipeHeatRelease_ ; wallLossRatio_ = totalOuterWallHeatLoss_/totalHotPipeHeatRelease_ ;}
            else{ heatRecoveryRatio_ = 0 ; wallLossRatio_ = 0 ;}
        }

        void calculateColdPipeHeatLoadUniformity(){

            meanColdPipeHeatLoad_ = 0 ; standardDeviationColdPipeHeatLoad_ = 0 ; coefficientOfVariationColdPipeHeatLoad_ = 0 ; minimumColdPipeHeatLoad_ = 0 ; maximumColdPipeHeatLoad_ = 0 ;
            if(coldPipeHeatAbsorption_.empty()){ return ;}

            minimumColdPipeHeatLoad_ = numeric_limits<double>::max() ; maximumColdPipeHeatLoad_ = -numeric_limits<double>::max() ;
            for(const auto& [patchName,Q]: coldPipeHeatAbsorption_){ meanColdPipeHeatLoad_ += Q ; minimumColdPipeHeatLoad_ = min(minimumColdPipeHeatLoad_,Q) ; maximumColdPipeHeatLoad_ = max(maximumColdPipeHeatLoad_,Q) ;}
            meanColdPipeHeatLoad_ /= coldPipeHeatAbsorption_.size() ;
            for(const auto& [patchName,Q]: coldPipeHeatAbsorption_){ standardDeviationColdPipeHeatLoad_ += (Q-meanColdPipeHeatLoad_)*(Q-meanColdPipeHeatLoad_) ;}
            standardDeviationColdPipeHeatLoad_ = sqrt(standardDeviationColdPipeHeatLoad_/coldPipeHeatAbsorption_.size()) ;
            if(abs(meanColdPipeHeatLoad_) > 1e-14){ coefficientOfVariationColdPipeHeatLoad_ = standardDeviationColdPipeHeatLoad_/abs(meanColdPipeHeatLoad_) ;}
        }

        void calculateEnergyBalance(){

            double totalBoundaryHeatTransfer = 0, normalisingHeatTransfer = 0 ;
            for(const auto& [patchName,Q]: totalWallHeatTransfer_){ totalBoundaryHeatTransfer += Q ; normalisingHeatTransfer += abs(Q) ;}
            energyBalanceResidual_ = totalBoundaryHeatTransfer + totalRadiativeSourceTerm_ ;
            if(normalisingHeatTransfer > 1e-14){ energyBalanceError_ = abs(energyBalanceResidual_)/normalisingHeatTransfer ;}
            else{ energyBalanceError_ = 0 ;}
        }

        void calculateDiagnostics(ScalarProperty& a){
            calculateInternalHeatFlux() ; calculateWallDiagnostics() ; calculateInternalIrradiationStatistics() ; calculateTemperatureStatistics() ; calculateRadiativeSourceTerm(a) ; calculateHeatExchangerPerformance() ; calculateColdPipeHeatLoadUniformity() ; calculateEnergyBalance() ;
        }

        double boundaryValue(Field& field, FVMatrix& fvMatrix, int faceIndex){

            for(Patch p: mesh_.boundaryPatches()){

                if(find(p.faces().begin(),p.faces().end(),faceIndex)!=p.faces().end()){
                    return boundaryFaceValue(field,fvMatrix,p.index(),faceIndex) ;
                }
            }

            throw runtime_error("Boundary face was not found while calculating P1 heat exchanger diagnostics.") ;
        }


        double minimumHeatFluxMagnitude() const{ return minimumHeatFluxMagnitude_ ;}
        double maximumHeatFluxMagnitude() const{ return maximumHeatFluxMagnitude_ ;}
        const array<double,3>& minimumTemperatureLocation() const{ return minimumTemperatureLocation_ ;}
        const array<double,3>& maximumTemperatureLocation() const{ return maximumTemperatureLocation_ ;}
        const array<double,3>& minimumIrradiationLocation() const{ return minimumIrradiationLocation_ ;}
        const array<double,3>& maximumIrradiationLocation() const{ return maximumIrradiationLocation_ ;}
        const array<double,3>& minimumHeatFluxMagnitudeLocation() const{ return minimumHeatFluxMagnitudeLocation_ ;}
        const array<double,3>& maximumHeatFluxMagnitudeLocation() const{ return maximumHeatFluxMagnitudeLocation_ ;}

        void calculateExtendedDiagnostics(){
            if(internalHeatFlux_.size()!=static_cast<size_t>(mesh_.numCells()) || internalIrradiation_.size()!=static_cast<size_t>(mesh_.numCells()) || radiativeSourceTerm_.size()!=static_cast<size_t>(mesh_.numCells())){ throw runtime_error("P1 extended diagnostics require calculateDiagnostics() to be called first") ;}
            minimumTemperature_ = numeric_limits<double>::max() ; maximumTemperature_ = -numeric_limits<double>::max() ; minimumIrradiation_ = numeric_limits<double>::max() ; maximumIrradiation_ = -numeric_limits<double>::max() ; minimumHeatFluxMagnitude_ = numeric_limits<double>::max() ; maximumHeatFluxMagnitude_ = -numeric_limits<double>::max() ;
            for(int i=0; i<mesh_.numCells(); ++i){
                const array<double,3> c = mesh_.cellCentre(i) ; double T = fvMatrixT_.sys().X()(i), G = internalIrradiation_[i], q = internalHeatFlux_[i].magnitude_ ;
                if(T<minimumTemperature_){ minimumTemperature_ = T ; minimumTemperatureLocation_ = c ;} if(T>maximumTemperature_){ maximumTemperature_ = T ; maximumTemperatureLocation_ = c ;}
                if(G<minimumIrradiation_){ minimumIrradiation_ = G ; minimumIrradiationLocation_ = c ;} if(G>maximumIrradiation_){ maximumIrradiation_ = G ; maximumIrradiationLocation_ = c ;}
                if(q<minimumHeatFluxMagnitude_){ minimumHeatFluxMagnitude_ = q ; minimumHeatFluxMagnitudeLocation_ = c ;} if(q>maximumHeatFluxMagnitude_){ maximumHeatFluxMagnitude_ = q ; maximumHeatFluxMagnitudeLocation_ = c ;}
            }
        }

        int nearestCell(double x, double y, double z) const{
            int nearest = -1 ; double minimumDistanceSquared = numeric_limits<double>::max() ;
            for(int i=0; i<mesh_.numCells(); ++i){ const array<double,3> c = mesh_.cellCentre(i) ; double d2 = (c[0]-x)*(c[0]-x)+(c[1]-y)*(c[1]-y)+(c[2]-z)*(c[2]-z) ; if(d2<minimumDistanceSquared){ minimumDistanceSquared = d2 ; nearest = i ;}}
            if(nearest<0){ throw runtime_error("Unable to locate a heat exchanger cell for point sampling") ;} return nearest ;
        }

        array<double,10> pointSample(double x, double y, double z) const{
            int i = nearestCell(x,y,z) ; const array<double,3> c = mesh_.cellCentre(i) ;
            return {c[0],c[1],c[2],fvMatrixT_.sys().X()(i),internalIrradiation_[i],internalHeatFlux_[i].magnitude_,internalHeatFlux_[i].x_,internalHeatFlux_[i].y_,internalHeatFlux_[i].z_,radiativeSourceTerm_[i]} ;
        }

        vector<array<double,10>> lineProfile(double y, double z) const{
            double minimumDistance = numeric_limits<double>::max() ;
            for(int i=0; i<mesh_.numCells(); ++i){ const array<double,3> c = mesh_.cellCentre(i) ; minimumDistance = min(minimumDistance,abs(c[1]-y)+abs(c[2]-z)) ;}
            vector<array<double,10>> profile ;
            for(int i=0; i<mesh_.numCells(); ++i){ const array<double,3> c = mesh_.cellCentre(i) ; if(abs((abs(c[1]-y)+abs(c[2]-z))-minimumDistance)<1e-10){ profile.push_back({c[0],c[1],c[2],fvMatrixT_.sys().X()(i),internalIrradiation_[i],internalHeatFlux_[i].magnitude_,internalHeatFlux_[i].x_,internalHeatFlux_[i].y_,internalHeatFlux_[i].z_,radiativeSourceTerm_[i]}) ;}}
            sort(profile.begin(),profile.end(),[](const array<double,10>& a,const array<double,10>& b){ return a[0]<b[0] ;}) ; return profile ;
        }

        vector<array<double,10>> wallProfile(const string& patchName) const{
            vector<array<double,10>> profile ; auto patchIt = wallHeatData_.find(patchName) ; if(patchIt==wallHeatData_.end()){ throw runtime_error("P1 wall profile patch was not found: "+patchName) ;}
            for(const P1HeatExchangerWallHeatStat& stat: patchIt->second){ int owner = mesh_.faceOwnerNeighbour(stat.faceIndex_)[0] ; const array<double,3> c = mesh_.faceCentre(stat.faceIndex_) ; profile.push_back({c[0],c[1],c[2],fvMatrixT_.sys().X()(owner),stat.irradiation_,internalHeatFlux_[owner].magnitude_,stat.heatFlux_,internalHeatFlux_[owner].x_,internalHeatFlux_[owner].y_,radiativeSourceTerm_[owner]}) ;}
            sort(profile.begin(),profile.end(),[&](const array<double,10>& a,const array<double,10>& b){ return (patchName=="north" || patchName=="south") ? a[0]<b[0] : a[1]<b[1] ;}) ; return profile ;
        }

        vector<array<double,11>> wallProfile(const string& patchName, double heatFluxScale) const{
            vector<array<double,11>> profile ;
            for(const array<double,10>& s: wallProfile(patchName)){ profile.push_back({s[0],s[1],s[2],s[3],s[4],s[5],s[6],s[7],s[8],s[9],s[6]/heatFluxScale}) ;}
            return profile ;
        }

        vector<array<double,10>> cellContourData() const{
            vector<array<double,10>> data ; data.reserve(mesh_.numCells()) ;
            for(int i=0; i<mesh_.numCells(); ++i){ const array<double,3> c = mesh_.cellCentre(i) ; data.push_back({c[0],c[1],c[2],fvMatrixT_.sys().X()(i),internalIrradiation_[i],internalHeatFlux_[i].magnitude_,internalHeatFlux_[i].x_,internalHeatFlux_[i].y_,internalHeatFlux_[i].z_,radiativeSourceTerm_[i]}) ;}
            return data ;
        }

        void validatePatchName(const string& patchName) const{
            if(totalWallHeatTransfer_.find(patchName) == totalWallHeatTransfer_.end()){ throw runtime_error("Heat exchanger boundary patch was not found: " + patchName) ;}
        }

        double boundaryFaceValue(Field& field, FVMatrix& fvMatrix, int patchIndex, int faceIndex){

            BoundaryCondition& boundaryCondition = *field.boundary()[patchIndex] ;
            int ownerCell = mesh_.faceOwnerNeighbour(faceIndex)[0] ;

            if(boundaryCondition.typeName()=="fixedgradient"){

                double gradient = boundaryCondition.boundaryValues().at(faceIndex) ;
                double distance = distanceFaceToCell(faceIndex) ;

                return fvMatrix.sys().X()(ownerCell)+gradient*distance ;
            }

            return boundaryCondition.boundaryValues().at(faceIndex) ;
        }

        double distanceFaceToCell(const int& faceIndex){
            array<double,3> faceAreaVec = mesh_.faceAreaVector(faceIndex) ;
            double sfMag = sqrt(faceAreaVec[0]*faceAreaVec[0] + faceAreaVec[1]*faceAreaVec[1] + faceAreaVec[2]*faceAreaVec[2]) ;
            faceAreaVec = {faceAreaVec[0]/sfMag,faceAreaVec[1]/sfMag,faceAreaVec[2]/sfMag} ;
            array<double,3> p1 = mesh_.faceCentre(faceIndex), p2 = mesh_.cellCentre(mesh_.faceOwnerNeighbour(faceIndex)[0]) ;
            return abs((p1[0]-p2[0])*faceAreaVec[0] + (p1[1]-p2[1])*faceAreaVec[1] + (p1[2]-p2[2])*faceAreaVec[2]) ;
        }
} ;

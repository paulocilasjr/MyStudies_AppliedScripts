# Load MetaboAnalystR
library(MetaboAnalystR)

#Load OptiLCMS
library(OptiLCMS)

#Example raw spectral data processing (MS1)
# in this example, we are going to use an experimental Malaria metabolomics dataset (UPLC-Q/E-ESI+, HILIC)
#Between two immune status (Native vs. Semi-immune).
#There are 12 samples (2 groups, 6 samples for each) and 3 QCs included in this dataset. 
#We are going to use the auto-optimiezed pipeline to process MS1 data.

download.file("https://www.xialab.ca/api/download/metaboloanalyst/malaria_r_example.zip",
              destfile = "malaria_raw.zip",
              method = "curl")
unzip("malaria_raw.zip", exdir = "upload")

# 2.1 - Region of interest (ROI) extraction

#rt.idx = retained percentage of chromatogram in retention time dimension. suggested 
#to use more than 50% (0.5) to include larger ROI and improve accuracy of following parameters' optimization

#rmConts = remove contamination before ROI extraction. 

# this step is only used for auto-optimized workflow. 

library(MetaboAnalystR)
library(OptiLCMS)

#Here, we extract ROIs from 3 QC samples.
dataFiles <- list.files("upload/QC/", full.names = TRUE)
mSet <- PerformROIExtraction(datapath = DataFiles, rt.idx = 0.9, rmConts = TRUE);

# 2.2 Auto-optmization of parameters
# execute PerformParamsOptimization function to optmize the critical parameters of peak picking and alignment
# It utilizes the extracted ROI data and the internal instument-specific parameters 
# Parallel computing can be enabled. More RAM will be consumed if the parallel core is set high
# Parameters optmization with a design of experiment (DoE) strategy. 
# Recommendations for parallel core setting = 64GB RAM ~ 6 cores; 32GB RAM ~ 4 cores; 
# 16GB RAM ~ 2 cores. Minimum 16GB RAM is required for raw spectral processing

best_params <- PerformParamsOptmization(mSet, param = SetPeakParam(platform = "UPLC-Q/E", ncore = 4);

# 2.3 - Importing example Data
mSet <- ImportRawMSData(path = c("upload"), plotSettings = SetPlotParam(Plot = T))

# 2.4 Raw spectral data processing
# Detect peaks (also known as peak picking) from the centroid data. centWave algorithm implemented in XCMS has been shown 
# to perform well in processing LC-HRMS spectra. 
# After peak detecton, peak alignment is performed to address retention time variations across spectra. 
# These aligned peaks from a peak intesity table with varying proportions of missing values.
# These missing values indicate that either peak detection failed or the corrsponding feature is absent from the respective sample.
# Therefore, the final step is 'gap filling' by repoerfroming direct peak extraction on corresponding regions in the raw spectra. 

#"mSet" include complete raw MS spectra to be processed.
#"params" is using the "best_params" generated above
#Plotting functions can be enabled with parameters
#"plotSettings = SetPlotParam(Plot = T)", os disabled b changing "T" into "F";
mSet <- PerformPeakProfiling(mSet, Params = best_params, plotSettings = SetPlotParam(Plot=TRUE))

# 2.5 Feature annotation
# Multiple peaks can be derived from the same compounds. These are real, biologically relevant peaks and might result from the
# formation of addcuts, incorporation of isotopes, or fragmentation during sample preparation or LC-MS analysis.
# Therefore, the fisrt sept in peak annotation aims to identify real peaks, and to clarify the relationship among them.
# Many empirical and statistical rules have been developed to address this problem, including CAMERA and CliqueMS.
# Peak annotation in MetaboAnalyst is currently based on CAMERA
# mz_abs_add = used tp set the allowed variance for the search (for adduct annotation), default = 0.001

annParamns <- SetAnnotationParam(polarity = 'positive', mz_abs_add = 0.015); 

mSet <- PerformPeakAnnotation(mSet, annParams)



#!/usr/bin/python

from __future__ import print_function                               

import os
import re                                                            
import sys
import ROOT
import errno                                                         
import codecs
import shutil   
import argparse
import subprocess
import array as arr
import numpy as np
import Ext_functions_from_eos

### Define Initial varaiables ###
dest       = 'Beam'
rereco     = False 
deadRocMap = True

### Locations of directories for various outputs

workPath   = os.getcwd()

evedispath = '/afs/cern.ch/user/a/abakshi/DQM_ML/'
tkrunspath = '/afs/cern.ch/user/a/abakshi/DQM_ML/TkCommissioner_runs/'
filepath   = '/afs/cern.ch/user/a/abakshi/DQM_ML/CMSSW_10_4_0_pre2/src/DQM/SiStripMonitorClient/scripts/'

### To obtain this information, in your shell type echo $CMSSW_BASE

CMSSW_BASE = '/afs/cern.ch/user/a/abakshi/DQM_ML/CMSSW_10_4_0_pre2'

### These are the locations of the directories within the CMSSW 

testpath   = '/src/DQM/SiStripMonitorClient/test/'
datapath   = '/src/DQM/SiStripMonitorClient/data/'
scriptpath = '/src/DQM/SiStripMonitorClient/scripts/'           
                                                                
### Here we define inputs to the script, Run type, Run number and the File name for eos files ######

parser     = argparse.ArgumentParser(description = 'ML options for TkMaps')

parser.add_argument('--ML', default = False, type = bool, help = 'To generate log files with all entries for ML applications')
parser.add_argument('--Run_type'  , type = str, help = 'Run type :  Cosmics | ZeroBias | StreamExpress | StreamExpressCosmics')
parser.add_argument('--Run_number', type = int, help = 'Valid run number' )
parser.add_argument('--File_name' , type = str, help = 'Complete filename of the DQM file, can also be used with xrootd')
parser.add_argument('--Output_loc', type = str, help = 'Location to output tracker maps')

args       = parser.parse_args()

ML         = args.ML
Run_type   = args.Run_type
#File_Name  = args.File_name
Run_number = args.Run_number
Output_loc = args.Output_loc

nnnOut     = Run_number/1000

runDirval    = Ext_functions_from_eos.setRunDirectory(Run_number)
DataLocalDir = runDirval[0]                                                          

########## Download the DQM file from eos if needed ##########

#if (File_Name == ' ') :
File_Name = Ext_functions_from_eos.downloadfromeos(Run_number, str(Run_type))

################ Check if run is complete  ###################

print("Getting the run status from DQMFile")

Check_command = 'check_runcomplete ' + filepath + File_Name
Check_output  = subprocess.call(Check_command, shell=True)                             
                                                                                            
if Check_output == 0:
   print('Using DQM file: ' + File_Name)

else:       
   print('***************** Warning: DQM file is not ready ************************')

   input_var = raw_input("DQM file is incomplete, do you want to continue? (y/n): ")     

   if (input_var == 'y') or (input_var == 'Y'):
            print('Using DQM file: '+ File_Name)
   else:
            sys.exit(0)


############### Start making TkMaps ################

### Overwrite previous folders if they exist 
### If not create a new directory

checkfolder = os.path.exists(str(Run_number))

if checkfolder == True:
   shutil.rmtree(str(Run_number))                                                 
   os.makedirs(  str(Run_number) + '/' + Run_type)                          

else:
   os.makedirs(str(Run_number) + '/' + Run_type)                                      

######## Similarily for eos areas ###################
 
#if os.path.exists(Output_loc + '/' + str(nnnOut) + '/' + str(Run_number)) :
   #shutil.rmtree(Output_loc + '/' + str(nnnOut) + '/' + str(Run_number))
   #os.makedirs(Output_loc + '/' + str(nnnOut) + '/' + str(Run_number) + '/' + Run_type)

#else:
   #os.makedirs(Output_loc + '/' + str(nnnOut) + '/' + str(Run_number) + '/' + Run_type)
       

############## Getting Global Tag  ############################

#After switching production to 10_X_X release, the clean up section needs to be reviewed and modified ??

globalTag = Ext_functions_from_eos.getGT(filepath+File_Name, str(Run_number), 'globalTag_Step1')        

print(" Creating the TrackerMap.... ")

detIdInfoFileName = 'TkDetIdInfo_Run' + str(Run_number) + '_' + Run_type + '.root'

os.chdir(str(Run_number) + '/' + Run_type)

### This cmsRun command generates the TkMaps 
### The 2 config files are for the ML and not ML case
### The ML one creates a dump of all the modules to generate dataframes for ML applications

if (ML == True) :  
     subprocess.call('cmsRun ' + CMSSW_BASE + testpath + 'SiStripDQM_OfflineTkMap_Template_cfg_DB_ML.py globalTag=' + globalTag + ' runNumber=' + str(Run_number) + ' dqmFile=' + filepath + File_Name + ' detIdInfoFile=' + detIdInfoFileName, shell=True)

else : 
    subprocess.call('cmsRun ' + CMSSW_BASE + testpath + 'SiStripDQM_OfflineTkMap_Template_cfg_DB.py globalTag='     + globalTag + ' runNumber=' + str(Run_number) + ' dqmFile=' + filepath + File_Name + ' detIdInfoFile=' + detIdInfoFileName, shell=True)

subprocess.call('rm -f *svg', shell=True)


############## Rename bad module list file ######################

shutil.move('QTBadModules.log','QualityTest_run' + str(Run_number) + '.txt')


############# Copying the template html file to index.html #####

if Run_type == "Cosmics" or Run_type == "StreamExpressCosmics":
    subprocess.call('cat ' + CMSSW_BASE + datapath + 'index_template_TKMap_cosmics.html | sed -e "s@RunNumber@' + str(Run_number) + '@g" > index.html', shell=True)
    
elif Run_type == "StreamExpress":
    subprocess.call('cat ' + CMSSW_BASE + datapath + 'index_template_Express_TKMap.html | sed -e "s@RunNumber@' + str(Run_number) + '@g" > index.html', shell=True)
    
else:
    subprocess.call('cat ' + CMSSW_BASE + datapath + 'index_template_TKMap.html | sed -e "s@RunNumber@' + str(Run_number) + '@g" > index.html', shell=True)


shutil.copyfile(CMSSW_BASE + '/src/DQM/SiStripMonitorClient/data/fedmap.html','fedmap.html')
shutil.copyfile(CMSSW_BASE + '/src/DQM/SiStripMonitorClient/data/psumap.html','psumap.html')

print(" Check TrackerMap on " + str(Run_number) + '/' + Run_type + " folder")  

output = []
output.append(os.popen("/bin/ls ").readline().strip())                                        


############# Producing the list of bad modules #################

print(" Creating the list of bad modules ")
    
subprocess.call('listbadmodule ' + filepath + '/'+ File_Name + ' PCLBadComponents.log', shell=True)
subprocess.call('bs_bad_ls_harvester . '+ str(Run_number), shell=True)                     
 

############# Producing the Module difference for ExpressStream ###

if (Run_type == "Cosmics") or (Run_type == "StreamExpressCosmics"): dest="Cosmics"

#Create merged list of BadComponent from (PCL, RunInfo and FED Errors)  

subprocess.call('cmsRun ' + CMSSW_BASE + testpath + 'mergeBadChannel_Template_cfg.py globalTag=' + globalTag + ' runNumber=' + str(Run_number) + ' dqmFile=' + filepath + '/' + File_Name, shell=True)

shutil.move('MergedBadComponents.log','MergedBadComponents_run' + str(Run_number) + '.txt')    

subprocess.call("mkdir -p " + tkrunspath + DataLocalDir + "/" + dest + " 2> /dev/null", shell=True)

shutil.copyfile(detIdInfoFileName, tkrunspath + DataLocalDir + '/' + dest + '/' + detIdInfoFileName)

os.remove(detIdInfoFileName)
os.remove('MergedBadComponentsTkMap_Canvas.root')
os.remove('MergedBadComponentsTkMap.root')

############ Counting dead pixels ##############################

print("counting dead pixel ROCs" )                                        
    
if (Run_number < 290124) :                                 
    subprocess.call(CMSSW_BASE + scriptpath + 'DeadROCCounter.py ' + filepath + '/' + File_Name, shell=True)
else: 
    subprocess.call(CMSSW_BASE + scriptpath + 'DeadROCCounter_Phase1.py '+ filepath + '/' + File_Name, shell=True)

if rereco:
    subprocess.call('mkdir -p ' + evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_number) + '/ReReco 2> /dev/null', shell=True)
else:
    subprocess.call('mkdir -p ' + evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_number) + '/' + Run_type + ' 2> /dev/null', shell=True)
    
#shutil.move('PixZeroOccROCs_run' + str(Run_number) + '.txt', workPath + '/PixZeroOccROCs_run' + str(Run_number) + '.txt')
  
############# Counting Dead ROCs and Inefficient DC in the run #
    
if deadRocMap == True:
    subprocess.call(CMSSW_BASE + scriptpath + 'DeadROC_duringRun.py '+ filepath + File_Name + ' ' + filepath + File_Name, shell=True)
    subprocess.call(CMSSW_BASE + scriptpath + 'change_name.py', shell=True)
    subprocess.call(CMSSW_BASE + scriptpath + 'PixelMapPlotter.py MaskedROC_sum.txt -c', shell=True)
    os.remove('MaskedROC_sum.txt')
    subprocess.call(CMSSW_BASE + scriptpath + 'InefficientDoubleROC.py ' + filepath + File_Name, shell=True)
 
else:
    print('No Online DQM file available, Dead ROC maps will not be produced')
    print('No Online DQM file available, inefficient DC list  will also not be produced')
 
############# Merge Dead ROCs and Occupoancy Plot ##############

subprocess.call(CMSSW_BASE + scriptpath + 'MergeOccDeadROC.py ' + filepath + File_Name, shell=True)

############# Merge PCL and DQM Plot (only StreamExpress) ######

if Run_type=="StreamExpress" or Run_type=="StreamHIExpress":
   subprocess.call(CMSSW_BASE + scriptpath + 'MergePCLDeadROC.py '+ filepath + File_Name + ' ' + filepath + File_Name_PCL, shell=True)
   subprocess.call(CMSSW_BASE + scriptpath + 'MergePCLFedErr.py ' + filepath + File_Name + ' ' + filepath + File_Name_PCL, shell=True)
   subprocess.call(CMSSW_BASE + scriptpath + 'PCLOthers.py '      + filepath + File_Name + ' ' + filepath + File_Name_PCL, shell=True)

############# Copy ouput files #################################

strip_files = os.listdir('.')
 
for file_name in strip_files:
    full_stripfile_name = os.path.join('.', file_name)
    if (os.path.isfile(full_stripfile_name)):
        if rereco:
            shutil.copy(full_stripfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_number) + '/ReReco')
        else:
            shutil.copy(full_stripfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_number) + '/' + Run_type)
       	    #shutil.copy(full_stripfile_name, Output_loc  + '/' + str(nnnOut) + '/' + str(Run_number) + '/' + Run_type)

############# Start making pixel maps ##########################

os.chdir(workPath)
#os.remove('index.html')
shutil.rmtree(str(Run_number))

############# Produce pixel phase1 TH2Poly maps ###############

subprocess.call(CMSSW_BASE + scriptpath + 'TH2PolyOfflineMaps.py ' + filepath + '/' + File_Name + ' 3000 2000', shell=True)
#shutil.move(workPath + '/PixZeroOccROCs_run' + str(Run_number) + '.txt', 'OUT/PixZeroOccROCs_run' + str(Run_number) + '.txt')
  
############# Copy ouput files #################################

pixel_files = os.listdir('./OUT')
for file_name in pixel_files:
    full_pixelfile_name = os.path.join('./OUT/', file_name)
    if (os.path.isfile(full_pixelfile_name)):
        if rereco:
           shutil.copy(full_pixelfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_number) + '/ReReco')
        else:
           shutil.copy(full_pixelfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_number) + '/' + Run_type)
           #shutil.copy(full_stripfile_name, Output_loc + '/' + str(nnnOut) + '/' + str(Run_number) + '/' + Run_type)

shutil.rmtree('OUT')
   
############# Produce pixel phase1 tree for Offline TkCommissioner ####

pixelTreeFileName = 'PixelPhase1Tree_Run'+str(Run_number)+'_'+Run_type+'.root'
    
subprocess.call( CMSSW_BASE + scriptpath + 'PhaseITreeProducer.py ' + filepath + '/' + File_Name + ' ' + pixelTreeFileName, shell=True)

shutil.copyfile(pixelTreeFileName, tkrunspath + DataLocalDir + '/' + dest + '/' + pixelTreeFileName)
    
os.remove(pixelTreeFileName)
os.remove(filepath + File_Name)
os.chdir(workPath)



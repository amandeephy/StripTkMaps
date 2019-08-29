#!/usr/bin/python
import os
import re                                                            
import sys
import ROOT
import errno                                                         
import codecs
import shutil                                                 
import subprocess
import Ext_functions
from __future__ import print_function                                


# This seems like a better place to start
dest       = 'Beam'
rereco     = False 
filepath   = '/tmp/'

Run_type   = sys.argv[1]
Run_Number = [int(x) for x in sys.argv[2:]]

testpath   = '/src/DQM/SiStripMonitorClient/test/'
datapath   = '/src/DQM/SiStripMonitorClient/data/'
scriptpath = '/src/DQM/SiStripMonitorClient/scripts/'

evedispath = '/data/users/event_display/'
tkrunspath = '/data/users/event_display/TkCommissioner_runs/'

CMSSW_BASE = str(os.popen('echo ${CMSSW_BASE}').read().strip())
                                                                           

########### Check if user enter the right run type #################

if Run_type == 'Cosmics' or Run_type == 'StreamExpress' or Run_type == 'StreamExpressCosmics' or Run_type == 'ZeroBias' or Run_type == 'StreamHIExpress' or Run_type == 'HIMinimumBias1' or re.match('ZeroBias([0-9]+?)',Run_type) or re.match('HIMinimumBias([0-9]+?)',Run_type):  #Okay this is definitely funny
    print(Run_type)

elif Run_type == 'ReReco':
    rereco    = True
    Run_type  ='ZeroBias'

else:
    print("please enter a valid run type: Cosmics | ZeroBias | StreamExpress | StreamExpressCosmics ")
    sys.exit(0)


for i in range(len(Run_Number)):                                                           

    ################# Download DQM file ############################

    print(" Downloading File ")

    nnnOut    = Run_Number[i]/1000
    File_Name = downloadOfflineDQMhisto(Run_Number[i], Run_type, rereco)

    if Run_type == "StreamExpress" or Run_type == "StreamHIExpress":
        File_Name_PCL = Ext_functions.downloadOfflinePCLhisto(Run_Number[i], Run_type)                   
    
    deadRocMap, File_Name_online = Ext_functions.downloadOnlineDQMhisto(Run_Number[i], Run_type)           

    runDirval    = Ext_functions.setRunDirectory(Run_Number[i])
    DataLocalDir = runDirval[0]                                                            

    ################ Check if run is complete  ##############

    print("Getting the run status from DQMFile")
    Check_command = 'check_runcomplete '+filepath+File_Name
    Check_output  = subprocess.call(Check_command, shell=True)                             
                                                                                            
    if Check_output == 0:
        print('Using DQM file: '+File_Name)

    else:
        
        print('***************** Warning: DQM file is not ready ************************')
        input_var = raw_input("DQM file is incomplete, do you want to continue? (y/n): ")
        
        if (input_var == 'y') or (input_var == 'Y'):
            print('Using DQM file: '+File_Name)
        else:
            sys.exit(0)

    if Run_type=="StreamExpress" or Run_type=="StreamHIExpress":
        if File_Name_PCL=='Temp':                                                          
            
            print('***************** Warning: PCL file is not ready ************************')
            input_var = raw_input("PCL file is not ready, you will need to re-run the script later for PCL plots, do you want to continue? (y/n): ")
            
            if (input_var == 'y') or (input_var == 'Y'):                                   
                print('-------->   Remember to re-run the script later !!!!! ')
            else:
                sys.exit(0)
    
    ############### Start making TkMaps ################

    checkfolder = os.path.exists(str(Run_Number[i]))
    if checkfolder == True:
        shutil.rmtree(str(Run_Number[i]))                                                 
        os.makedirs(str(Run_Number[i])+'/'+Run_type)                          
    else:
        os.makedirs(str(Run_Number[i])+'/'+Run_type)                                      
        
    ############## Getting Global Tag  ############################

    globalTag = getGT(filepath+File_Name, str(Run_Number[i]), 'globalTag_Step1')          #After switching production to 10_X_X release, the clean up section needs to be reviewed and modified ??
    
    print(" Creating the TrackerMap.... ")

    workPath          = os.getcwd()
    detIdInfoFileName = 'TkDetIdInfo_Run'+str(Run_Number[i])+'_'+Run_type+'.root'
                                                    
    os.chdir(str(Run_Number[i])+'/'+Run_type)                                            
    
    subprocess.call('cmsRun ' + CMSSW_BASE + testpath + 'SiStripDQM_OfflineTkMap_Template_cfg_DB.py globalTag=' + globalTag + ' runNumber=' + str(Run_Number[i]) + ' dqmFile=' + filepath + '/' + File_Name + ' detIdInfoFile=' + detIdInfoFileName, shell=True)
    subprocess.call('rm -f *svg', shell=True)

    ############## Rename bad module list file ######################

    shutil.move('QTBadModules.log','QualityTest_run' + str(Run_Number[i]) + '.txt')

    ############# Copying the template html file to index.html #####

    if Run_type == "Cosmics" or Run_type == "StreamExpressCosmics":
        subprocess.call('cat ' + CMSSW_BASE + datapath + 'index_template_TKMap_cosmics.html | sed -e "s@RunNumber@' + str(Run_Number[i]) + '@g" > index.html', shell=True)
    elif Run_type == "StreamExpress":
        subprocess.call('cat ' + CMSSW_BASE + datapath + 'index_template_Express_TKMap.html | sed -e "s@RunNumber@' + str(Run_Number[i]) + '@g" > index.html', shell=True)
    else:
        subprocess.call('cat ' + CMSSW_BASE + datapath + 'index_template_TKMap.html | sed -e "s@RunNumber@' + str(Run_Number[i]) + '@g" > index.html', shell=True)

    shutil.copyfile(CMSSW_BASE + datapath + 'fedmap.html','fedmap.html')
    shutil.copyfile(CMSSW_BASE + datapath + 'psumap.html','psumap.html')

    print(" Check TrackerMap on " + str(Run_Number[i]) + '/' + Run_type + " folder")
    
    output =[]
    output.append(os.popen("/bin/ls ").readline().strip())                                       
    print(output)

    ############# Producing the list of bad modules #################

    print(" Creating the list of bad modules ")
    
    subprocess.call('listbadmodule ' + filepath + '/'+ File_Name + ' PCLBadComponents.log', shell=True) 
    subprocess.call('bs_bad_ls_harvester . '+ str(Run_Number[i]), shell=True)                     
    
    ############# Producing the Module difference for ExpressStream ###

    if (Run_type == "Cosmics") or (Run_type == "StreamExpressCosmics"):
        dest="Cosmics"


    ############# Create merged list of BadComponent from (PCL, RunInfo and FED Errors) ignore for now 

    subprocess.call('cmsRun ' + CMSSW_BASE + testpath +'mergeBadChannel_Template_cfg.py globalTag='+globalTag+' runNumber='+str(Run_Number[i])+' dqmFile='+filepath+'/'+File_Name, shell=True)
    shutil.move('MergedBadComponents.log','MergedBadComponents_run'+str(Run_Number[i])+'.txt')
    
    subprocess.call("mkdir -p " + tkrunspath + DataLocalDir + "/" + dest + " 2> /dev/null", shell=True)
    shutil.copyfile(detIdInfoFileName, tkrunspath + DataLocalDir + '/' + dest + '/' + detIdInfoFileName)

    os.remove(detIdInfoFileName)
    os.remove('MergedBadComponentsTkMap.root')    
    os.remove('MergedBadComponentsTkMap_Canvas.root')

    ############ Counting dead pixels ##############################

    print("counting dead pixel ROCs" )                                         
    if (Run_Number[i] < 290124) :                                 
        subprocess.call(CMSSW_BASE + scriptpath + 'DeadROCCounter.py ' + filepath + '/' + File_Name, shell=True)
    else: 
        subprocess.call(CMSSW_BASE + scriptpath + 'DeadROCCounter_Phase1.py '+ filepath + '/' + File_Name, shell=True)

    if rereco:
        subprocess.call('mkdir -p ' + evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_Number[i]) + '/ReReco 2> /dev/null', shell=True)
    else:
        subprocess.call('mkdir -p ' + evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_Number[i]) + '/' + Run_type + ' 2> /dev/null', shell=True)
    
    shutil.move('PixZeroOccROCs_run'+str(Run_Number[i])+'.txt',workPath+'/PixZeroOccROCs_run'+str(Run_Number[i])+'.txt')

    ############# Counting Dead ROCs and Inefficient DC in the run #
    
    if deadRocMap == True:

        subprocess.call(CMSSW_BASE + scriptpath + 'DeadROC_duringRun.py '+ filepath + File_Name_online + ' ' + filepath + File_Name, shell=True)
        subprocess.call(CMSSW_BASE + scriptpath + 'change_name.py', shell=True)
        subprocess.call(CMSSW_BASE + scriptpath + 'PixelMapPlotter.py MaskedROC_sum.txt -c', shell=True)
        subprocess.call(CMSSW_BASE + scriptpath + 'InefficientDoubleROC.py ' + filepath + File_Name_online, shell=True)
        os.remove('MaskedROC_sum.txt')
    else:
        print('No Online DQM file available, Dead ROC maps will not be produced')
        print('No Online DQM file available, inefficient DC list  will also not be produced')

    ############# Merge Dead ROCs and Occupoancy Plot ##############

    subprocess.call(CMSSW_BASE + scriptpath + 'MergeOccDeadROC.py ' + filepath + File_Name, shell=True)

    ############# Merge PCL and DQM Plot (only StreamExpress) ######

    if Run_type=="StreamExpress" or Run_type=="StreamHIExpress":
        subprocess.call(CMSSW_BASE + scriptpath + 'MergePCLDeadROC.py '+ filepath + File_Name + ' ' + filepath + File_Name_PCL, shell=True)
        subprocess.call(CMSSW_BASE + scriptpath + 'MergePCLFedErr.py ' + filepath + File_Name + ' ' + filepath + File_Name_PCL, shell=True)
        subprocess.call(CMSSW_BASE + scriptpath + 'PCLOthers.py '+ filepath + File_Name + ' ' + filepath + File_Name_PCL, shell=True)

    ############# Copy ouput files #################################

    strip_files = os.listdir('.')
    for file_name in strip_files:
        full_stripfile_name = os.path.join('.', file_name)
        if (os.path.isfile(full_stripfile_name)):
            if rereco:
                shutil.copy(full_stripfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_Number[i]) + '/ReReco')
            else:
                shutil.copy(full_stripfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_Number[i]) + '/' + Run_type)


    ############# Start making pixel maps ##########################

    os.chdir(workPath)
    os.remove('index.html')
    shutil.rmtree(str(Run_Number[i]))

    #produce pixel phase1 TH2Poly maps
    subprocess.call(CMSSW_BASE + scriptpath + 'TH2PolyOfflineMaps.py ' + filepath + '/' + File_Name + ' 3000 2000', shell=True)
    shutil.move(workPath + '/PixZeroOccROCs_run' + str(Run_Number[i]) + '.txt', 'OUT/PixZeroOccROCs_run' + str(Run_Number[i]) + '.txt')

    ############# Copy ouput files #################################

    pixel_files = os.listdir('./OUT')
    for file_name in pixel_files:
        full_pixelfile_name = os.path.join('./OUT/', file_name)
        if (os.path.isfile(full_pixelfile_name)):
            if rereco:
                shutil.copy(full_pixelfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_Number[i]) + '/ReReco')
            else:
                shutil.copy(full_pixelfile_name, evedispath + DataLocalDir + '/' + dest + '/' + str(nnnOut) + '/' + str(Run_Number[i]) + '/' + Run_type)
    shutil.rmtree('OUT')

    ############# Produce pixel phase1 tree for Offline TkCommissioner ####

    pixelTreeFileName = 'PixelPhase1Tree_Run'+str(Run_Number[i])+'_'+Run_type+'.root'
    
    subprocess.call( CMSSW_BASE + scriptpath + 'PhaseITreeProducer.py ' + filepath + '/' + File_Name + ' ' + pixelTreeFileName, shell=True)
    shutil.copyfile(pixelTreeFileName, tkrunspath + DataLocalDir + '/' + dest + '/' + pixelTreeFileName)
    
    os.remove(pixelTreeFileName)
    if File_Name:
        os.remove(filepath+File_Name)
    if File_Name_online:
        os.remove(filepath+File_Name_online)
    os.chdir(workPath)



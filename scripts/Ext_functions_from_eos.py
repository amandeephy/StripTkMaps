from __future__ import print_function  # Needs to be on top
import os
import sys
import codecs
import subprocess
from   ROOT                import TFile, gDirectory

# These could be modified based on application
key         = '/afs/cern.ch/user/a/abakshi/DQM_ML/userkey.pem'
certificate = '/afs/cern.ch/user/a/abakshi/DQM_ML/usercert.pem'

def setRunDirectory(runNumber):
    runKey=0
    # Contains map of run numbeer to directory
    # Don't forget to add an entry when there is a new era
    dirDict = { 325799:['Data2018', 'HIRun2018'],\
                315252:['Data2018', 'Run2018'],\
                308336:['Data2018', 'Commissioning2018'],\
                294644:['Data2017', 'Run2017'],\
                290123:['Data2017', 'Commissioning2017'],\
                284500:['Data2016', 'PARun2016'],\
                271024:['Data2016', 'Run2016'],\
                264200:['Data2016', 'Commissioning2016'],\
                246907:['Data2015', 'Run2015'],\
                232881:['Data2015', 'Commissioning2015'],\
                211658:['Data2013', 'Run2013'],\
                209634:['Data2013', 'HIRun2013'],\
                190450:['Data2012', 'Run2012']}
    
    # Return all directory values for all higher than key value 
    for key in sorted(dirDict):
        if runNumber > key:
            runKey   = key

    return dirDict[runKey]  

def downloadfromeos(Run_number, Run_type):

    runDirval      = setRunDirectory(Run_number)
    DataLocalDir   = runDirval[0]
    DataOfflineDir = runDirval[1]
    nnn            = Run_number/100

    # Copy from eos area using xrootd

    #base_url       = 'root://cms-xrd-global.cern.ch//eos/cms/store/group/comm_dqm/DQMGUI_data/'+ DataOfflineDir + '/' + Run_type + '/000' + str(nnn) + 'xx/'
    base_address    = '/eos/cms/store/group/comm_dqm/DQMGUI_data/'+ DataOfflineDir + '/' + Run_type + '/R000' + str(nnn) + 'xx/'

    print('Directory to fetch the DQM file from :' + base_address)         # Use local eos address for now

    subprocess.call('ls ' + base_address + '> filelist_tmp', shell = True) # List all available DQM Files in the directory

    fileptr  = open('filelist_tmp', 'r')
    filelist = fileptr.readlines()

    File_Name= ''
   
    if (run_number in string for string in filelist) :
    	for string in filelist :
 	        # Splits the string downloads the Prompt Reco file
    		if ( (str(Run_number) in string)  and ("__DQMIO.root" in string) and ('PromptReco') in string):
	    		print('Found DQM File, using the Prompt Reco version as default ')
            		File_Name = str(string.split('\n')[0])                        
    else:
        print('No DQM file available. Please check the Offline server')
        sys.exit(0)

    # Download Offline DQM File from eos area 
    #File_name      = 'DQM_V0001_R000' + str(Run_number) + '__' + str(Run_type) + '__' + str(DataOfflineDir) + '-PromptReco-v1__DQMIO.root'

    print('Downloading DQM file:' + File_Name)

    subprocess.call('cp ' + base_address + File_Name + ' .', shell=True)

    return File_Name

def downloadOfflineDQMhisto(run, Run_type, rereco):
    
    runDirval      = setRunDirectory(run)
    DataLocalDir   = runDirval[0]
    DataOfflineDir = runDirval[1]
    nnn            = run/100
    File_Name      = ' '
    url            = 'https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'+ DataOfflineDir + '/' + Run_type + '/000' + str(nnn) + 'xx/'
    
    print('Processing ' + Run_type + ' in '+ DataOfflineDir + '...')
    print('Directory to fetch the DQM file from :' + url)

    ##### Download and read the index.html file ###### 

    subprocess.call('curl -k --cert ' + certificate + ' --key ' + key + ' -X GET ' + url + ' > index.html', shell=True)

    f     = codecs.open("index.html", 'r')
    index = f.readlines()

    ##### Ensure it contains the right strings ######

    if any(str(run) in s for s in index):
        for s in index:
            if rereco:
                if (str(run) in s) and ("__DQMIO.root" in s) and ("17Sep2018" in s):   
                    File_Name = str(str(s).split("xx/")[1].split("'>DQM")[0])                    
            else:
                if (str(run) in s) and ("__DQMIO.root" in s):                         
                    File_Name = str(str(s).split("xx/")[1].split("'>DQM")[0])                   

    else:
        print('No DQM file available. Please check the Offline server')
        sys.exit(0)

    ##### Download Offline DQM File ################

    print('Downloading DQM file:' + File_Name)
    subprocess.call('curl -k --cert ' + certificate + ' --key ' + key  + ' -X GET ' + url + File_Name + ' > /tmp/' + File_Name, shell=True)
    
    return File_Name



def downloadOfflinePCLhisto(run, Run_type):
    
    runDirval      = setRunDirectory(run)
    DataLocalDir   = runDirval[0]
    DataOfflineDir = runDirval[1]
    nnn            = run/100
    File_Name      = 'Temp'
    url            = 'https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/' + DataOfflineDir + '/' + Run_type + '/000' + str(nnn) + 'xx/'

    print('Processing '+ Run_type + ' in '+DataOfflineDir+"...")
    print('Directory to fetch the DQM file from :' + url)

    ##### Download and read the index.html file ######     
    
    subprocess.Popen('curl -k --cert ' + certificate + ' --key ' + key + ' -X GET ' + url + ' > index.html', shell=True)
    
    f     = codecs.open("index.html", 'r')
    index = f.readlines()

    ##### Ensure it contains the right strings ######

    if any(str(run) in s for s in index):
        for s in index:
            if (str(run) in s) and ("PromptCalibProdSiPixel-Express" in s) and ("__ALCAPROMPT.root" in s):
                File_Name = str(str(s).split("xx/")[1].split("'>DQM")[0])
 
    else:
        print('No DQM file available. Please check the Offline server')
        sys.exit(0)

    ##### Download Offline PCL File ################

    if File_Name!='Temp':
   
        print('Downloading DQM file:'+File_Name)
   
   	subprocess.call('curl -k --cert ' + certificate + ' --key ' + key  + ' -X GET ' + url + File_Name + ' > /tmp/' + File_Name, shell=True)


    return File_Name



def downloadOnlineDQMhisto(run, Run_type):
    
    runDirval        = setRunDirectory(run)
    DataLocalDir     = runDirval[0]
    DataOfflineDir   = runDirval[1]
    nnn              = run/100
    nnnOnline        = run/10000
    File_Name_online = ''
    deadRocMap       = False
    url1             = 'https://cmsweb.cern.ch/dqm/online/data/browse/Original/000' + str(nnnOnline) + 'xxxx/000' + str(nnn) + 'xx/'
    url2             = 'https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OnlineData/original/000'+str(nnnOnline)+'xxxx/000'+str(nnn)+'xx/'
    
    ######### Online File ###########

    subprocess.Popen('curl -k --cert ' + certificate + ' --key ' + key + ' -X GET ' + url1 + ' > index_online.html', shell=True)
    subprocess.Popen('curl -k --cert ' + certificate + ' --key ' + key + ' -X GET ' + url2 + ' > index_online_backup.html', shell=True)

    f_online            = codecs.open("index_online.html", 'r')
    index_online        = f_online.readlines()
    f_online_backup     = codecs.open("index_online_backup.html", 'r')
    index_online_backup = f_online_backup.readlines()

    ##### Ensure it contains the right strings ######

    if any(str(run) in x for x in index_online):
        for x in index_online:
            if (str(run) in x) and ("_PixelPhase1_" in x):
                File_Name_online=str(str(x).split(".root'>")[1].split("</a></td><td>")[0])
                deadRocMap = True

    else:
        print("Can't find any file in offline server, trying the online server")
        if any(str(run) in y for y in index_online_backup):
            for y in index_online:
                if (str(run) in y) and ("_PixelPhase1_" in y):
                    File_Name_online=str(str(y).split(".root'>")[1].split("</a></td><td>")[0])
                    deadRocMap = True
        else:
            print('No Online DQM file available. Skip dead roc map')
            deadRocMap = False

   
    ##### Download Online DQM File ################

    print('Downloading DQM file:'+File_Name_online)

    subprocess.call('curl -k --cert ' + certificate + ' --key ' + key + ' -X GET ' + url1 + File_Name_online +' > /tmp/' + File_Name_online, shell=True)

    os.remove('index_online.html')
    os.remove('index_online_backup.html')

    return deadRocMap, File_Name_online


def getGTfromDQMFile(DQMfile, Run_number, globalTagVar) :

    if not os.path.isfile(DQMfile):
       print("Error: file" + str(DQMfile) + "not found, exit")
       sys.exit(0)

    thefile = TFile( DQMfile )
    globalTagDir = 'DQMData/Run ' + Run_number + '/Info/Run summary/CMSSWInfo'

    if not gDirectory.GetDirectory( globalTagDir ):
       print("Warning: globalTag not found in DQM file")
       sys.exit(0)

    keys = gDirectory.GetDirectory(globalTagDir).GetListOfKeys()

    key = keys[0]

    globalTag = ''

    while key:
       obj = key.ReadObj()
       if globalTagVar in obj.GetName():
          globalTag = obj.GetName()[len("<"+globalTagVar+">s="):-len("</"+globalTagVar+">")]
          break
       key = keys.After(key)

    if len(globalTag) > 1:
        if globalTag.find('::') >= 0:
           print(globalTag[0:globalTag.find('::')])
        else:
           print(globalTag)

    return globalTag
 
def getGT(DQMfile, Run_number, globalTagVar):
   
    globalTag_v0 = getGTfromDQMFile(DQMfile, Run_number, globalTagVar)
    globalTag    = globalTag_v0

    print("Global Tag: " + globalTag_v0)

    #### Clean up the Global Tag ###################

    for z in range(len(globalTag_v0)-2):    
        if (globalTag_v0[z].isdigit()) and  (globalTag_v0[z+1].isdigit()) and (globalTag_v0[z+2].isdigit()) and(globalTag_v0[z+3].isupper()):
            globalTag = globalTag_v0[z:]
            break
   
    if globalTag == "":

    ##### Try from the Data Aggregation Service ####   
    
        print(" No GlobalTag found: trying from DAS.... ")
        globalTag = str(subprocess.Popen('getGTscript.sh ' + filepath + File_Name + ' ' + str(run), shell=True));
   
   	if globalTag == "":
            print(" No GlobalTag found for run: "+str(run))

    return globalTag 

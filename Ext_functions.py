import os
import sys
import codecs                                              
from __future__ import print_function
from getGTfromDQMFile_V2 import getGTfromDQMFile                     #Needs a better name

#This definitely goes outside::
def setRunDirectory(runNumber):
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
    runKey=0
    for key in sorted(dirDict):
        if runNumber > key:
            runKey=key
    return dirDict[runKey]  

def downloadOfflineDQMhisto(run, Run_type,rereco):
    runDirval=setRunDirectory(run)
    DataLocalDir=runDirval[0]
    DataOfflineDir=runDirval[1]
    nnn=run/100
    print('Processing '+ Run_type + ' in '+DataOfflineDir+"...")
    File_Name = ''

    print('Directory to fetch the DQM file from: https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'+DataOfflineDir+'/'+Run_type+'/000'+str(nnn)+'xx/') #maybe just do this once ?
    url = 'https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'+DataOfflineDir+'/'+Run_type+'/000'+str(nnn)+'xx/'                                        #maybe just do this once ?
    
    os.popen("curl -k --cert /data/users/cctrkdata/current/auth/proxy/proxy.cert --key /data/users/cctrkdata/current/auth/proxy/proxy.cert -X GET "+url+" > index.html") 

    f=codecs.open("index.html", 'r')   #Why codecs though?

    index = f.readlines()
    if any(str(Run_Number[i]) in s for s in index): 
        for s in index:                             
            if rereco:
                if (str(Run_Number[i]) in s) and ("__DQMIO.root" in s) and ("17Sep2018" in s):   #RERECO Date and Year??
                    File_Name = str(str(s).split("xx/")[1].split("'>DQM")[0])                   
            else:
                if (str(Run_Number[i]) in s) and ("__DQMIO.root" in s):                         
                    File_Name = str(str(s).split("xx/")[1].split("'>DQM")[0])                   

    else:
        print('No DQM file available. Please check the Offline server')
        sys.exit(0)

    print('Downloading DQM file:'+File_Name)                                                    
    os.system('curl -k --cert /data/users/cctrkdata/current/auth/proxy/proxy.cert --key /data/users/cctrkdata/current/auth/proxy/proxy.cert -X GET https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'+DataOfflineDir+'/'+Run_type+'/000'+str(nnn)+'xx/'+File_Name+' > /tmp/'+File_Name)
    
    return File_Name

def downloadOfflinePCLhisto(run, Run_type):
    runDirval=setRunDirectory(run)
    DataLocalDir=runDirval[0]
    DataOfflineDir=runDirval[1]
    nnn=run/100
    print('Processing '+ Run_type + ' in '+DataOfflineDir+"...")
    File_Name = 'Temp'
    print('Directory to fetch the DQM file from: https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'+DataOfflineDir+'/'+Run_type+'/000'+str(nnn)+'xx/')
    url = 'https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'+DataOfflineDir+'/'+Run_type+'/000'+str(nnn)+'xx/'
    os.popen("curl -k --cert /data/users/cctrkdata/current/auth/proxy/proxy.cert --key /data/users/cctrkdata/current/auth/proxy/proxy.cert -X GET "+url+" > index.html") 
    f=codecs.open("index.html", 'r')
    index = f.readlines()
    if any(str(Run_Number[i]) in s for s in index):
        for s in index:
            if (str(Run_Number[i]) in s) and ("PromptCalibProdSiPixel-Express" in s) and ("__ALCAPROMPT.root" in s):
                File_Name = str(str(s).split("xx/")[1].split("'>DQM")[0])
    else:
        print('No DQM file available. Please check the Offline server')
        sys.exit(0)
    if File_Name!='Temp':
        print('Downloading DQM file:'+File_Name)
        os.system('curl -k --cert /data/users/cctrkdata/current/auth/proxy/proxy.cert --key /data/users/cctrkdata/current/auth/proxy/proxy.cert -X GET https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OfflineData/'+DataOfflineDir+'/'+Run_type+'/000'+str(nnn)+'xx/'+File_Name+' > /tmp/'+File_Name)
    
    return File_Name


def downloadOnlineDQMhisto(run, Run_type): #Whatte name
    runDirval=setRunDirectory(run)
    DataLocalDir=runDirval[0]
    DataOfflineDir=runDirval[1]
    nnn=run/100
    nnnOnline = run/10000
    File_Name_online=''
    deadRocMap = False                   #Make this part of a config file?
    ##################online file########    
    url1 = 'https://cmsweb.cern.ch/dqm/online/data/browse/Original/000'+str(nnnOnline)+'xxxx/000'+str(nnn)+'xx/'
    os.popen("curl -k --cert /data/users/cctrkdata/current/auth/proxy/proxy.cert --key /data/users/cctrkdata/current/auth/proxy/proxy.cert -X GET "+url1+" > index_online.html")
    
    url2 = 'https://cmsweb.cern.ch/dqm/offline/data/browse/ROOT/OnlineData/original/000'+str(nnnOnline)+'xxxx/000'+str(nnn)+'xx/'
    os.popen("curl -k --cert /data/users/cctrkdata/current/auth/proxy/proxy.cert --key /data/users/cctrkdata/current/auth/proxy/proxy.cert -X GET "+url2+" > index_online_backup.html")
    f_online_backup=codecs.open("index_online_backup.html", 'r')
    index_online_backup = f_online_backup.readlines()

    f_online=codecs.open("index_online.html", 'r')
    index_online = f_online.readlines()
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

    print('Downloading DQM file:'+File_Name_online)


    os.system('curl -k --cert /data/users/cctrkdata/current/auth/proxy/proxy.cert --key /data/users/cctrkdata/current/auth/proxy/proxy.cert -X GET https://cmsweb.cern.ch/dqm/online/data/browse/Original/000'+str(nnnOnline)+'xxxx/000'+str(nnn)+'xx/'+File_Name_online+' > /tmp/'+File_Name_online)

    os.remove('index_online.html')
    os.remove('index_online_backup.html')
    return deadRocMap, File_Name_online;


def getGT(DQMfile, RunNumber, globalTagVar):
    globalTag_v0 = getGTfromDQMFile(DQMfile, RunNumber, globalTagVar)
    print("Global Tag: " + globalTag_v0)
    globalTag = globalTag_v0

    for z in range(len(globalTag_v0)-2):     #clean up the garbage string in the GT
        if (globalTag_v0[z].isdigit()) and  (globalTag_v0[z+1].isdigit()) and (globalTag_v0[z+2].isdigit()) and(globalTag_v0[z+3].isupper()):
            globalTag = globalTag_v0[z:]
            break
    if globalTag == "":
        print(" No GlobalTag found: trying from DAS.... ")
        globalTag = str(os.popen('getGTscript.sh '+filepath+ File_Name+' ' +str(Run_Number[i])));
        if globalTag == "":
            print(" No GlobalTag found for run: "+str(Run_Number[i]))

    return globalTag

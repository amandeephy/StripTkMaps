# StripTkMaps
A first repository to collect the restructuring of (strips) TkMaps related scripts for Tracker Offline shifters </br>

These scripts were created to download and generate tracker maps from the /eos/ area at CERN. 
I work with CMSSW_10_4_0, ensure you have the DQM folder in your src area . <br/>
To run in a CMSSW area (10_X_Y or higher):

```bash
cmsrel CMSSW_10_4_0
cd CMSSW_10_4_0/src
cmsenv
git cms-init
git cms-addpkg DQM/SiStripMonitorClient
cd DQM/SiStripMonitorClient/scripts
```
Copy the 2 scripts: TkMaps_from_eos and Ext_functions_from_eos to your to your `scripts/` directory.</br>
Change the default output locations by modifying the tkrunspath and evedispath </br>
Change the location of where the DQM file is temporarily copied by editing filepath </br>
```bash
python TkMaps_from_eos 
--Run_type <Cosmics | ZeroBias | StreamExpress | StreamExpressCosmics> 
--Run_number <List of valid integers> 
--File_name  <This option allows for directly using an xrootd file >
--Output_loc <Location of eos output>
--ML <Boolean (default : False)>
```
Filename is not required and can be reconstructed in the downloadfromeos function in the Ext_functions_from_eos script. <br/>
The --ML flag requires the config file : 
```
StripDQM_OfflineTkMap_Template_cfg_ML.py
```
Alongside the tracker maps this should create a list of attributes of all modules.
The updated	SiStripTrackerMapCreator.cc allows for numTopModules to be unsigned integer, hence passing a -1 will create a dump of all strip variables in topmodules.log.

# StripTkMaps
A first repository to collect the restructuring of (strips) TkMaps related scripts for Tracker Offline shifters </br>
To run in a CMSSW area (10_X_Y or higher) :
```bash
./TkMaps --Run_type <Cosmics | ZeroBias | StreamExpress | StreamExpressCosmics> --Run_number <List ofvalid integers>  --ML <Boolean default : False>
```
The --ML flag requires the config file : 
'''
StripDQM_OfflineTkMap_Template_cfg_ML.py
'''

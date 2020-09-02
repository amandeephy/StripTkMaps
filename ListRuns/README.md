# Generation of lists of Run numbers from EOS, AFS or RR.

## Prerequisites

This script was tested using ```Python``` version ```3.6```. 
Although other versions might work too, this is the only one tested.

Test your python version by running

```bash
python --version
Python 3.6.8
```
## Setup (code is not adapted for use at LPC cluster yet)

At your terminal (choose different port for your case)

The ports are optional to specify, you may want to do this when trying to use a Jupyter notebook
#### At lpc 
```bash
kinit username@FNAL.GOV

ssh -L 127.0.0.1:9999:127.0.0.1:9999 username@cmslpc-sl6.fnal.gov 
cd path/to/your/working/area
```
#### Or at lxplus

```bash

ssh -L 127.0.0.1:9999:127.0.0.1:9999 username@lxplus.cern.ch 
cd path/to/your/working/area
```

You can choose a CMSSW release (but the script has only been tested on release 10_2_10)
```bash
cmsrel CMSSW_10_2_10
cd CMSSW_10_2_10/src/
cmsenv

git clone git@github.com:GuillermoFidalgo/StripTkMaps.git
#or 
git clone https://github.com/GuillermoFidalgo/StripTkMaps.git

cd StripTkMaps

jupyter notebook --port 9999 --ip 127.0.0.1 --no-browser
```
**Check your terminal and copy paste URL into your browser**





### The use of the notebook is deprecated and was present only for initial development so you should ignore the notebook for now.
To use the notebook you must have the appropiate certificate in the same directory as the script (Unless you specify the path to it)
[Open the notebook](ListOfRuns.ipynb) to interact with the code and make the apporpiate changes to your needs.

Notice that there is an `index.html` document. You should ignore this because it is a remnant from earlier versions of the code and it is not necesary at all for now.


**You can see other functionality in the [`ListRuns_cfg.py`](ListRuns_cfg.py) script**


*Side Note* To use the script please look at [Authentication Setup](https://github.com/GuillermoFidalgo/ML4TRKDQM#authentication-setup)
### Virtual environment

*Side Note* **If you clone from this repo please remove `venv/` and all of its contents *before* creating a virtual enviroment**

Unless you know what you are doing, it is recommended to set up a virtual environment such as to not get conflicts between different versions of packages.


You can create a virtual python virtual environment with:

```bash
python3 -m venv venv
```

Then you need to *activate* the virtual environment

```bash
. venv/bin/activate
```

You should now see a ```(venv) ``` in front of you terminal line.

```
(venv) [yourname@yourmachine ML4TKRDQM]$
```


### Installing packages

All tools necessary for data retrieval and data analysis are installable via ```pip```

*pip* comes bundled in Python 3.6 so, you should already have it installed.

These commands install all the tools necessary for this notebook. Each of them have their own documentation. You can start with the general documentation for most of the packages [here](https://github.com/ptrstn/cms-tracker-studies-notebook) and a <ins>seperate documentation</ins> for `runregistry` [here](https://github.com/fabioespinosa/runregistry_api_client) 

```bash
pip install git+https://github.com/CMSTrackerDPG/cernrequests
pip install git+https://github.com/CMSTrackerDPG/runregcrawlr
pip install git+https://github.com/CMSTrackerDPG/dqmcrawlr
pip install git+https://github.com/CMSTrackerDPG/wbmcrawlr
pip install git+https://github.com/CMSTrackerDPG/cms-tracker-studies
pip install runregistry
pip install numpy
pip install matplotlib
pip install pandas
pip install seaborn
pip install scipy
pip install scikit-learn
pip install bs4
```

*Side Note*: ```cernrequests``` is also available in pypi, so you could also install it via:

```bash
pip install cernrequests
```

This would install the current stable version of the package, 
while the github link always installs the latest version inside the master branch of the repository.
In order to update the pypi package, a maintainer is necessary which will leave in April 2019.


## Authentication Setup

A lot of resources at CERN are only accessible with proper authentication. 
Some only require you to be within the CERN GPN, some require you to just authenticate with your Grid User Certificate, while others require cookies.
In general should [request a grid user certificate](https://ca.cern.ch/ca/), if you dont already have.
After that, you should have downloaded a file called ```myCertificate.p12```
Now this file needs to be converted into *public* and *private* key. You can do that using ```openssl```.
The tools for this notebook, assume that your public and private key are inside the ```private``` folder.
If you do not like this behavior you can change the path by exporting the ```CERN_CERTIFICATE_PATH``` environment variable as described [here](https://github.com/CMSTrackerDPG/cernrequests#configuration).

In general you can do the just described steps with:

```bash
mkdir -p ~/private
openssl pkcs12 -clcerts -nokeys -in myCertificate.p12 -out ~/private/usercert.pem
openssl pkcs12 -nocerts -in myCertificate.p12 -out ~/private/userkey.tmp.pem
openssl rsa -in ~/private/userkey.tmp.pem -out ~/private/userkey.pem
```

These commands should ask you for the user certificate password. 
In the simplest case, just enter them twice.

*Note*: Your private key ```userkey.pem``` and public key ```usercert.pem``` have to be **passwordless** for the tools to work.





# Usage

The `ListRuns_cfg.py` is a module which contains different functions and helper scripts in order to extract information from different sources to later produce 
a list of runs found from that source.


The most relevant methods to look at when wanting to change the final list are: 
- `getruntype_eos()` 
- `getRR()`
- `getruns_afs()`

The `ListRunsDriver.py` is an interactive (for now) script that will generate text files with the run numbers found on the specified source.
Note that it is a bit hard coded for ZeroBias runs. This is something to be fixed in the future.

*Side note* The latest version of the `getRR()` method is awaiting athentication fixes and will not always output correctly due to a wierd encoding error which is 
currently being looked at.

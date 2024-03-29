PySIC: a Python toolkit for quantitative analysis of Sea-Ice Core
==========

This module is currently under heavy developement, and some functions may be broken.

With colleagues of the Ice Core Consortium of the MOSAiC Expedition, we are currently writing a data descriptor paper about the sea ice coring methodology used during the expedition, and the post processing of the data.

pysic is a script collection developped to work with ice core data. The project origined with the need of importing ice core data saved under excel xlsx format during the operation of SiZONET project (https://eloka-arctic.org/sizonet) into python for processing. In the later years, pysic has been further developped to compute various pysic properties, based on semi-empirical equations described in the litterature, aggregate ice cores for statistical analysis, plot easily profile of physical variable.

PySIC is currently getting revamped in order to produce a usable module. To facilitate the consistency check of the ice core, starting at version 0.6 profile will be define as xarray, rather than a numpy array.
 
PySIC introduces 3 class
* core: sea ice core, based on python dictionnary
* corestack: collection of sea ice core, based on pandas
* profile : individual profile for various measurement, based on xarray

The functions in PySIC will be organized into the following categories:
* property: compute sea ice, brine or sea water physical property
* stat: compute generic statistic on a sea ice core collection
* tools: various helper function
* visualization: create basic views
* metrics: extract quantitative information

**Cite as:**
> *Oggier, M* **SicPy: A Python Toolkit for Quantitative Analysis of Sea Ice Core**. Version 0.6, Retrieved from https://github.com/megavolts/pysic

**References**
> *Oggier, M., et al.*, AGU 2020, Ice core studies of autumn-to-spring sea ice evolution at the MOSAiC floe 

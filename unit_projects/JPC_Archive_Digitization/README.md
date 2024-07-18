# JPC Archive Digitization

DPO is working with other Smithsonian Units and the Getty to digitize the [Johnson Publishing Company Archive](https://nmaahc.si.edu/about/news/ford-mellon-and-macarthur-foundations-transfer-sole-ownership-historic-ebony-and-jet), which features >4 million prints and negatives, including Ebony and Jet.

This repo contains the scripts used to gather, integrate, and migrate data and identifiers. 

### Current Status: Production

 * ASpace_to_Osprey - Get the data from ASpace into Osprey
 * draft_scripts - old test and draft versions of scripts
 * PostQC - Post QC steps
    1. jpc_generate_hmo_auto.py – Creates the HMO IDs based on the filenames in Osprey
    2. id_manager.py - Send the IDs from the HMO and DAMS to ID Manager
    3. hmo_to_arches.py - Add the item data from ASpace to the data model and create the Arches sub record
 * Reports - SQL to create reports to display in Osprey
 * systems_tests - scripts to test systems

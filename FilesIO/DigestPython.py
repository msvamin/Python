"""
This function reads the run data from hdf5 files and creates the Data Digest Json object
Filename: DigestPython.py
Author: Amin Mousavi
Date: 9/18/2015
"""

__author__ = 'Amin'

import glob
import json
import h5py
import pandas as pd
import requests
import random
import os

# Getting the basic run information from REST Api
def getRunInf(RunID, ddconfig):
    infbject = {}
    runURL = ddconfig["runInf"] %(RunID)
    runInf = requests.get(runURL)
    runInf = json.loads(runInf.content)
    infobj["runInfo"] = {}
    infobj["runInfo"]["id"] = RunID
    BetaID = runInf[0][0]
    infobj["runInfo"]["beta"] = BetaID
    infobj["runInfo"]["startTime"] = runInf[0][2]
    infobj["runInfo"]["endTime"] = runInf[0][3]
    infobj["runInfo"]["type"] = runInf[0][4]
    infobj["runInfo"]["operator"] = runInf[0][5]
    infobj["runInfo"]["chipID"] = runInf[0][6]
    infobj["runInfo"]["scriptID"] = runInf[0][7]
    infobj["runInfo"]["configID"] = runInf[0][8]
    infobj["runInfo"]["description"] = runInf[0][12]
    infobj["runInfo"]["analyte"] = runInf[0][13]
    infobj["runInfo"]["reagent"] = runInf[0][14]
    return infobj

# Getting Check Chip information
def getCheckChip(RunID):
    ccURL = ddconfig["CheckChip"] %(RunID)
    checkchip = requests.get(ccURL)
    checkchip = checkchip.content
    checkchip = json.loads(checkchip)
    return checkchip

# Getting run Data from hdf5 files
def getRunData(h5list, ddconfig):
    temp_series = {}
    frames = []
    tsTag = ddconfig['timestamp']
    # Choosing random with and without magnet sensors
    with h5py.File(h5list[0], 'r') as hf:
        magnetIdx = []
        nomagnetIdx = []
        for i in range(hf['magnet'].shape[0]):
            for j in range(hf['magnet'].shape[1]):
                if hf['magnet'].value[i][j]:
                    magnetIdx.append((i,j))
                else:
                    nomagnetIdx.append((i,j))
    magnetSensors = random.sample(magnetIdx,10)
    nomagnetSensors = random.sample(nomagnetIdx,10)

    mdF = []
    mdL = []
    for fd in ddconfig["metadata"]:
        mdF.append(fd['name'])
        mdL.append(fd['label'])
    senreadTag = ddconfig["SensorRead"]["name"]
    senreadFd = ddconfig["SensorRead"]["subfield"]
    for fpath in h5list:
        # Extracting the instrument state from the name of the hdf5 file
        fp = fpath.split('/')
        fn = fp[-1]
        fm = fn.split('_')
        instrumentState = '_'.join(fm[:-4])
        temp_series["instrumentState"] = pd.Series()
        print instrumentState
        with h5py.File(fpath, "r") as hf:
            timestamp = hf[tsTag].value
            md_key = []
            md_value = []
            for id in range(len(hf.attrs["metadata_key"])):
                md_key.append(hf.attrs["metadata_key"][id])
                md_value.append(hf["metadata_value"].value[:,id])
            #Sensor Reads
            for sid in range(len(ddconfig["SensorRead"]["magnetlabels"])):
                temp_series[ddconfig["SensorRead"]["magnetlabels"][sid]] = pd.Series(hf[senreadTag][senreadFd].value[:,magnetSensors[sid][0],magnetSensors[sid][1]], timestamp)
                temp_series[ddconfig["SensorRead"]["nomagnetlabels"][sid]] = pd.Series(hf[senreadTag][senreadFd].value[:,nomagnetSensors[sid][0],nomagnetSensors[sid][1]], timestamp)
        for k in range(len(md_key)):
            if md_key[k] in mdF:
                md_label = mdL[mdF.index(md_key[k])]
                temp_series[md_label] = pd.Series()
                temp_series[md_label] = temp_series[md_label].append(pd.Series(md_value[k], timestamp))
        temp_series["instrumentState"] = temp_series["instrumentState"].append(pd.Series(instrumentState, timestamp))
        df = pd.DataFrame(temp_series)
        frames.append(df)
    AllData = pd.concat(frames)
    return AllData

# Main function
def main(RunID):

    # Opening Data Digest Config File
    with open('./DigestConfig.json') as json_data:
        ddconfig = json.loads(json_data.read())

    # Load and Save Pathes
    loadpath = ddconfig["load"]["root"] + RunID + ddconfig["load"]["path"]
    savepath = ddconfig["save"]["root"] + RunID + ddconfig["save"]["path"]
    # Create the save path if it doesn't exist
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    # Listing all hdf5 files
    h5l0 = glob.glob(loadpath + '/*.hdf5')
    h5l = [hh for hh in h5l0 if "PRIME" not in hh]
    # Choosing a random block on chip
    sampleh5 = random.choice(h5l)
    samplesplit = sampleh5.split('_')
    h5list = []
    for nm in h5l:
        hfsp = nm.split('_')
        if hfsp[-4]==samplesplit[-4] and hfsp[-3]==samplesplit[-3]:
            h5list.append(nm)

    samplesplit2 = sampleh5.split('/')
    sfn = samplesplit2[-1]
    sfnsplit = sfn.split('_')
    skn = '_'.join(sfnsplit[:-4])
    row = []
    col = []
    rownum = []
    colnum = []
    for nm in h5l:
        nmsplit = nm.split('/')
        nmn = nmsplit[-1]
        nmnsplit = nmn.split('_')
        fkn = '_'.join(nmnsplit[:-4])
        if fkn == skn:
            row.append(nmnsplit[-4])
            col.append(nmnsplit[-3])
            rownum.append(nmnsplit[-2])
            aa = nmnsplit[-1]
            colnum.append(aa[:-5])
    intrownum = [int(r) for r in rownum]
    intcolnum = int(colnum[0])

    print row, col, rownum, colnum
    print sum(intrownum)
    print sum(intrownum)*intcolnum
    # Getting the Run Data from hdf5 files
    Signals = getRunData(h5list, ddconfig)
    # Saving the result as JSON file
    DDobject = {}
    DDobject["Signals"] = Signals.to_json()
    #DDoject["runInfo"] = getRunInf(RunID, ddconfig)
    #DDobject["checkchip"] = getCheckChip(RunID)
    DDobject["readConfig"] = {}
    DDobject["readConfig"]["numFiles"] = len(h5l)
    DDobject["readConfig"]["numBlocks"] = len(h5l)/len(h5list)
    DDobject["readConfig"]["numInstStates"] = len(h5list)
    #ddobject["readConfig"]["numPhases"] = numPhases
    #ddobject["readConfig"]["numReads"] = numReads
    DDobject["readConfig"]["numRows"] = sum(intrownum)
    DDobject["readConfig"]["numSensors"] = sum(intrownum)*intcolnum

    with open(savepath + "DataDigest.json", "w") as outjson:
        json.dump(DDobject, outjson)


if __name__ == "__main__":
    #RunID = "B000020_2015_9_11_17_30"
    #RunID = "B000020_2015_9_10_17_12"
    #RunID = "B000020_2015_8_27_14_43"
    #RunID = "B000020_2015_8_25_16_9"
    #RunID = "B000020_2015_8_21_18_10"
    #RunID = "B000020_2015_8_21_15_5"
    #RunID = "B000020_2015_8_20_18_36"
    #RunID = "B000020_2015_8_18_13_55"
    #RunID = "B000020_2015_8_17_15_55"
    #RunID = "B000020_2015_8_13_17_18"
    RunID = "B000019_2015_9_17_16_47"


    main(RunID)
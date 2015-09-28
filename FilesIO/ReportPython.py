"""
This function reads the Data Digest Json object and generates the png plots, csv tables and Report Template JSON object
Filename: ReportPython.py
Author: Amin Mousavi
Date: 9/16/2015
"""

__author__ = 'Amin'

import json
from pprint import pprint
import matplotlib.pyplot as plt
import csv
import datetime
import pandas as pd

def pngplot(df, nametag, savefile, description):
    bb = []
    for id in df.index:
        aa = datetime.datetime.strptime(id, '%Y-%m-%d_%H:%M:%S.%f')
        bb.append(int(aa.strftime("%s")))
    newid = [int(a)-int(bb[0]) for a in bb]
    #df[nametag].plot()
    plt.plot(newid, df[nametag])
    plt.xlabel('Time (Seconds)')
    plt.title(description)
    plt.savefig(savefile)
    plt.close()

def main(RunID):
    # Opening Data Digest Config File
    with open('./ReportingConfig.json') as json_data:
        rpconfig = json.loads(json_data.read())

    # Creating Report Template JSON
    reporttemp = {}
    reporttemp["RunID"] = RunID
    reporttemp["Date"] = str(datetime.datetime.now())

    # Extracting the config values
    savepath = rpconfig["save"]["root"] + RunID + rpconfig["save"]["path"]
    loadpath = rpconfig["load"]["root"] + RunID + rpconfig["load"]["path"]
    reporttemp["DataPath"] = savepath
    runInfoTag  = rpconfig["fields"]["runInfo"]
    checkchipTag = rpconfig["fields"]["checkchip"]
    instrumentTag = rpconfig["fields"]["instrument"]
    chipTag = rpconfig["fields"]["chip"]
    readconfigTag = rpconfig["fields"]["readConfig"]
    sensorReadTag = rpconfig["fields"]["sensorRead"]

    # Report Template Groups
    reporttemp["Groups"] = [ {"title": "Basic Information", "Tables": [], "Plots":[] },
                             {"title": "Instrument Data", "Tables": [], "Plots":[] },
                             {"title": "Chip Data", "Tables": [], "Plots":[] },
                             {"title": "Sensor Reads", "Tables": [], "Plots":[] }]

    # Opening Run's json File
    with open(loadpath + "DataDigest.json", "r") as datajson:
        datadigest = json.loads(datajson.read())
    df = pd.read_json(datadigest["Signals"])

    # Plotting the instrument data and saving the png files
    for insfield in rpconfig[instrumentTag]:
        nameTag = insfield["name"]
        savefile = savepath + insfield["filename"]
        description = insfield["desc"]
        pngplot(df, nameTag, savefile, description)
        reporttemp["Groups"][1]["Plots"].append({"name": nameTag, "file": insfield["filename"], "caption": description})

    # Plotting the chip data and saving the png files
    for chipfield in rpconfig[chipTag]:
        nameTag = chipfield["name"]
        savefile = savepath + chipfield["filename"]
        description = chipfield["desc"]
        pngplot(df, nameTag, savefile, description)
        reporttemp["Groups"][2]["Plots"].append({"name": nameTag, "file": chipfield["filename"], "caption": description})

    # Plotting random sensor reads
    # Magnet Sensors
    bb = []
    for id in df.index:
        aa = datetime.datetime.strptime(id, '%Y-%m-%d_%H:%M:%S.%f')
        bb.append(int(aa.strftime("%s")))
    newid = [int(a)-int(bb[0]) for a in bb]
    filename = rpconfig[sensorReadTag]["magnetfilename"]
    savefile = savepath + filename
    description = rpconfig[sensorReadTag]['magnetdesc']
    plt.figure()
    for i in range(rpconfig[sensorReadTag]["magnetSensorsNum"]):
        nameTag = rpconfig[sensorReadTag]["magnetSensorsTag"] %(i+1)
        plt.plot(newid, df[nameTag])
        #df[nameTag].plot()
    plt.xlabel('Time (Seconds)')
    plt.title(description)
    plt.savefig(savefile)
    plt.close()
    reporttemp["Groups"][3]["Plots"].append({"name": "WithMagnetSensorRead", "file": filename, "caption": description})

    #No Magnet Sensors
    filename = rpconfig[sensorReadTag]["nomagnetfilename"]
    savefile = savepath + filename
    description = rpconfig[sensorReadTag]['nomagnetdesc']
    plt.figure()
    for i in range(rpconfig[sensorReadTag]["NomagnetSensorsNum"]):
        nameTag = rpconfig[sensorReadTag]["NomagnetSensorsTag"] %(i+1)
        plt.plot(newid, df[nameTag])
        #df[nameTag].plot()
    plt.xlabel('Time (Seconds)')
    plt.title(description)
    plt.savefig(savefile)
    plt.close()
    reporttemp["Groups"][3]["Plots"].append({"name": "NoMagnetSensorRead", "file": filename, "caption": description})

    # Generating the tables and saving csv files
    # runInfo table
    try:
        filename = savepath + rpconfig[runInfoTag]["filename"]
        with open(filename, 'wb') as csv_data:
            writer = csv.writer(csv_data)
            tb = datadigest[runInfoTag]
            for key, value in tb.items():
                writer.writerow([key,value])
        reporttemp["Groups"][0]["Tables"].append({"name": runInfoTag, "file": rpconfig[runInfoTag]["filename"],
                                              "caption": rpconfig[runInfoTag]["description"], "heading": False,
                                              "delimiter":",", "columns":[1,2]})
    except Exception:
        print "Failed to Generate the RunInfo Table"

    # Chip Check table
#    savepath = savefolder + rpconfig[checkchipTag]["filename"]
#    ccRes = datadigest[checkchipTag]
#    tableentry = ["Fail", "Pass"]
#    for i in range(len(ccRes)):
#        k = datadigest[checkchipTag][i][0]
#        filename = rpconfig[checkchipTag]["filename"] %(k)
#        fieldname = checkchipTag + str(k)
#        savepath = savefolder + filename
#        capval = ["First", "Second"]
#        captionstr = rpconfig[checkchipTag]["description"] %capval[i]
#        print savepath
#        tb = {rpconfig[checkchipTag]["data"][1]: tableentry[datadigest[checkchipTag][i][1]+1], \
#              rpconfig[checkchipTag]["data"][2]: tableentry[datadigest[checkchipTag][i][2]+1], \
#              rpconfig[checkchipTag]["data"][3]: tableentry[datadigest[checkchipTag][i][3]+1], \
#              rpconfig[checkchipTag]["data"][4]: tableentry[datadigest[checkchipTag][i][4]+1], \
#              rpconfig[checkchipTag]["data"][5]: tableentry[datadigest[checkchipTag][i][5]+1], \
#              rpconfig[checkchipTag]["data"][6]: tableentry[datadigest[checkchipTag][i][6]+1], \
#              rpconfig[checkchipTag]["data"][7]: tableentry[datadigest[checkchipTag][i][7]+1]
#              }
#        print tb
#        with open(savepath, 'wb') as csv_data:
#            writer = csv.writer(csv_data)
#            for key, value in tb.items():
#                writer.writerow([key,value])
#        reporttemp["Groups"][2]["Tables"].append({"name": fieldname, "file": filename,
#                                            "caption": captionstr, "heading": False,
#                                            "delimiter":",", "columns":[1,2]})

    # Read Configuration Table
    filename = savepath + rpconfig[readconfigTag]["filename"]
    tb = datadigest[readconfigTag]
    with open(filename, 'wb') as csv_data:
        writer = csv.writer(csv_data)
        for key, value in tb.items():
            writer.writerow([key,value])
    reporttemp["Groups"][0]["Tables"].append({"name": readconfigTag, "file": rpconfig[readconfigTag]["filename"],
                                            "caption": rpconfig[readconfigTag]["description"], "heading": False,
                                            "delimiter":",", "columns":[1,2]})

    # Dumping the Report Template JSON
    with open(savepath + "ReportTemplate.json", "w") as outjson:
        json.dump(reporttemp, outjson)

if __name__ == "__main__":
    #RunID = "B000030_2015_9_15_16_54"
    #RunID = "B000030_2015_9_14_17_34"
    #RunID = "B000030_2015_9_11_13_29"
    #RunID = "B000030_2015_9_10_17_13"
    #RunID = "B000030_2015_8_17_18_10"
    #RunID = "B000024_2015_9_9_16_35"
    #RunID = "B000024_2015_9_3_13_45"
    #RunID = "B000024_2015_9_2_16_9"
    #RunID = "B000024_2015_9_2_15_8"
    #RunID = "B000024_2015_9_1_18_32"
    #RunID = "B000020_2015_9_15_16_27"
    #RunID = "B000020_2015_9_14_17_33"
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
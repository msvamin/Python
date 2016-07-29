__author__ = 'Amin'

"""
This script takes the list of run IDs and generates the DataCleaner files
Filename: wrapper.py
Author: Amin Mousavi
Date: 3/24//2016
"""

from DataCleaner import DataCleaner
import requests
import json
import logging
import time

def store_experiment_state(run_id, run_state_id, state_id, username_id):
    """
    Writes the state of the experiment to the cloud database
    :param run_id: The id of the experiment
    :param run_state_id: the state id related to the DataCleaner
    :param state_id: the state of the experiment in DataCleaner
    :param username_id: the username_id
    """

    token_request = dict()
    token_request = {"experimentId": run_id ,"experimentStateList_id": run_state_id, "state": state_id, "username_id": username_id};
    token_request = json.dumps(token_request)
    headers = {'Content-Type' : 'application/json'}
    post_url = 'http://genapsys-data.appspot.com/rest/experimentState'
    r = requests.post(post_url, token_request, headers=headers)


def main():

    date_time = time.strftime("%c")
    logging.basicConfig(filename='/NAS/PipelineReports/DataCleaner/Logs/DataCleanerLog-' + date_time + '.log', level=logging.DEBUG)
    while True:
        logging.info("Waiting for 5 minutes...")
        print "Waiting for 5 minutes..."
        time.sleep(300)
        try:
            get_run_url = "http://genapsys-services.appspot.com/listOfRunsToBeProcessed?stateInclude=6&keywork=&intervalDays=1&stateExclude=8"
            run_list = requests.get(get_run_url)
            run_list = json.loads(run_list.content)
        except:
            logging.info("Error in getting the run list! Trying again ...")
            print "Error in getting the run list! Trying again ..."

        for run_id in run_list:
            logging.info(run_id)
            print run_id
            try:

                # Starting the analysis
                store_experiment_state(run_id, 8, 1, 88)

                print "Hack Waiting for 10 minutes..."
                time.sleep(600)
                # Data Object
                DataObj = DataCleaner(run_id)
                logging.info("Defining the Data Object OKAY")
                print "Defining the Data Object OKAY"

                # Getting config information
                DataObj.getConfig(DataObj._config_file)
                logging.info("Getting config information OKAY")
                print "Getting config information OKAY"

                # Getting basic experiment info from the cloud database
                DataObj.getBasicInfo()
                logging.info("Getting basic experiment info from database OKAY")
                print "Getting basic experiment info from database OKAY"

                # Sets load and save paths
                DataObj.setPaths()
                logging.info("Set load and save paths OKAY")
                print "Set load and save paths OKAY"

                # Calculating the read configuration
                DataObj.calcReadConfig()
                logging.info("Calculating the read configuration OKAY")
                print "Calculating the read configuration OKAY"

                # Dumping the experiment basic info as json file
                DataObj.dumpRunInfo()
                logging.info("Dumping the experiment basic info as json file OKAY")
                print "Dumping the experiment basic info as json file OKAY"

                # Dumping the Experiment basic info successful
                store_experiment_state(run_id, 8, 2, 88)

                # Calculating the location of sensors and no_magnet flag
                DataObj.getChipInfo()
                logging.info("Calculating the location of sensors and no_magnet flag OKAY")
                print "Calculating the location of sensors and no_magnet flag OKAY"

                # Extracting the instrument states
                DataObj.createMask()
                logging.info("Extracting the instrument states OKAY")
                print "Extracting the instrument states OKAY"

                # Exporting the instrument data
                DataObj.instrumentData()
                logging.info("Exporting the instrument data OKAY")
                print "Exporting the instrument data OKAY"

                # Exporting the instrument data successful
                store_experiment_state(run_id, 8, 3, 88)

                # Exporting the sensor reads data
                DataObj.sensorReads()
                logging.info("Exporting the sensor reads data OKAY")
                print "Exporting the sensor reads data OKAY"

                # Exporting the sensor data successful
                store_experiment_state(run_id, 8, 4, 88)

            except:
                print "DataCleaner failed for the run:"
                print run_id
                logging.info("DataCleaner failed for the run:")
                logging.info(run_id)

if __name__ == "__main__":
    main()

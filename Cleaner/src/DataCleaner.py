# The Data Reshaping tool
# Created by Amin 2/17/2016

__author__ = 'Amin'

import os
import json
import pandas as pd
import requests
import h5py
import math
import random
import re
import numpy


# The main class for data reshaping
class DataCleaner(object):

    def __init__(self, run_id, config_file='../config/DataCleanerConfig.json'):

        self.id = run_id
        self._config_file = config_file
        self.config = None
        self.beta = None
        self.start_time = None
        self.end_time = None
        self.type = None
        self.operator = None
        self.chip_id = None
        self.script_id = None
        self.config_id = None
        self.description = None
        self.analyte = None
        self.reagent = None
        self.email = None
        self.first_name = None
        self.last_name = None
        self.load_path = None
        self.save_path = None
        self.num_files = None
        self.check_chip = None
        self.phases = None
        self.num_phases = None
        self.num_sensors = None
        self.num_reads_per_file = None
        self.num_reads = None
        self.num_rows = None
        self.row = None
        self.col = None
        self.no_magnet = None
        self.read_times = None
        self.state_list = None
        self.state_times = None
        self.end_time = None
        self.num_samples = None
        self.instrument_data = None
        self.sensor_reads = None

    ######################
    # Methods
    ######################

    # Get the REST data
    @staticmethod
    def getRestData(url_str):
        """
        :param url_str: the url for the REST API
        :return: the json object receiving from the REST API
        """
        rest_data = requests.get(url_str)
        return json.loads(rest_data.content)

    # Get the config data
    def getConfig(self, config_file):
        # Opening Data Reshaping Config File
        with open(config_file) as json_data:
            self.config = json.loads(json_data.read())

    def getChipCheck(self):
        run_check_chip_url = self.config['RestAPI']['CheckChip'] % self.id
        self.check_chip = self.getRestData(run_check_chip_url)


    # Reading basic run info
    def getBasicInfo(self):
        """
        Gets the experiment metadata from the cloud database
        """
        run_info_url = self.config['RestAPI']['runInf'] % self.id
        run_operator_url = self.config['RestAPI']['Operator'] % self.id

        # basic run info
        run_info = self.getRestData(run_info_url)
        self.beta = run_info[0][0]
        self.start_time = run_info[0][2]
        self.end_time = run_info[0][3]
        self.type = run_info[0][4]
        self.operator = run_info[0][5]
        self.chip_id = run_info[0][6]
        self.script_id = run_info[0][7]
        self.config_id = run_info[0][8]
        self.description = run_info[0][12]
        self.analyte = run_info[0][13]
        self.reagent = run_info[0][14]

        run_operator = self.getRestData(run_operator_url)
        self.email = run_operator[0][0]
        self.first_name = run_operator[0][1]
        self.last_name = run_operator[0][2]

        run_check_chip_url = self.config['RestAPI']['CheckChip'] % self.id
        self.check_chip = self.getRestData(run_check_chip_url)

    # Sets load and save paths
    def setPaths(self):
        """
        Sets the load and save paths
        :return:
        """
        self.load_path = os.path.join(self.config["loadPath"]["root"], self.beta, self.id,
                                      self.config["loadPath"]["path"])
        self.save_path = os.path.join(self.config["savePath"]["root"], self.beta, self.id,
                                      self.config["savePath"]["path"])

        # Create the save path if it doesn't exist
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    # Read Configuration
    def calcReadConfig(self):
        """
        Calculates the read configuration from the h5 files
        """
        file_path = os.path.join(self.load_path, self.config["SensorReads"]["path"])
        key_name = self.config["SensorReads"]["filename"]
        all_files = os.listdir(file_path)
        #files_read = [fl for fl in all_files if key_name in fl]
        files_read = filter(lambda x: key_name in x, all_files)
        self.num_files = len(files_read)

        file_name = os.path.join(file_path, files_read[0])
        with h5py.File(file_name, 'r') as h5_file:
            self.phases = h5_file.keys()
            self.num_phases = len(self.phases)
            dataset_size = h5_file[self.phases[0]].shape
            self.num_sensors = dataset_size[0]
            self.num_reads_per_file = dataset_size[1]
            self.num_reads = self.num_reads_per_file * self.num_files
            self.num_rows = self.num_sensors/1024

    # Dumping the json Run Info
    def dumpRunInfo(self):
        """
        Dumps the basic experiment info as a json file
        """
        run_inf = dict()
        run_inf['Beta'] = self.beta
        run_inf['Analyte'] = self.analyte
        run_inf['Operator'] = dict()
        run_inf['Reagent'] = self.reagent
        run_inf['ConfigName'] = self.config_id
        run_inf['ScriptName'] = self.script_id
        run_inf['Description'] = self.description
        run_inf['Type'] = self.type
        run_inf['CheckChip'] = self.check_chip
        run_inf['LoadPath'] = self.load_path
        run_inf['SavePath'] = self.save_path
        run_inf['Operator']['Email'] = self.email
        run_inf['Operator']['FirstName'] = self.first_name
        run_inf['Operator']['LastName'] = self.last_name
        run_inf['ReadsConfig'] = dict()
        run_inf['ReadsConfig']['NumFiles'] = self.num_files
        run_inf['ReadsConfig']['NumPhases'] = self.num_phases
        run_inf['ReadsConfig']['NumSensors'] = self.num_sensors
        run_inf['ReadsConfig']['NumReadsPerFile'] = self.num_reads_per_file
        run_inf['ReadsConfig']['NumReads'] = self.num_reads
        run_inf['ReadsConfig']['NumRows'] = self.num_rows
        run_inf['ReadsConfig']['Phases'] = self.phases

        json_file = os.path.join(self.save_path, "RunInfo.json")
        with open(json_file, "w") as out_json:
            json.dump(run_inf, out_json, sort_keys=True, indent=4)

    # Reading basic run info
    def getChipInfo(self):
        """
        Calculates the location of the sensors and the no_magnet flag
        """
        # Listing all dac files
        calib_file_path = os.path.join(self.load_path, self.config["DACread"]["path"])
        key_name = self.config["DACread"]["filename"]
        all_calib_files = os.listdir(calib_file_path)

        dac_files = [fl for fl in all_calib_files if key_name in fl]
        dac_files.sort()

        idac = list()
        for fn in dac_files:
            fp = os.path.join(calib_file_path, fn)
            with h5py.File(fp, 'r') as h5_file:
                file_keys = h5_file.keys()
                fk = file_keys[0]
                vv = h5_file[fk+'/idac']
                idac.extend(vv.value.tolist())

        sensor_id = [idac[i][0] for i in range(len(idac))]
        sensor_id.sort()
        row = [int(math.ceil(s/1024.0)) for s in sensor_id]
        col = [((s-1) % 1024)+1 for s in sensor_id]
        no_magnet = [row[i] % 32 == 0 or row[i] % 32 == 1 or col[i] % 32 == 0 or col[i] % 32 == 1 or
                     col[i] % 32 == 2 for i in range(len(sensor_id))]

        self.row = row
        self.col = col
        self.no_magnet = no_magnet

    # Windowing functions
    # Gettnig read times from the h5 file names
    def getReadTimes(self):
        """
        Parses the time stamps off a list of h5 file names
        """
        file_path = os.path.join(self.load_path, self.config["SensorReads"]["path"])
        key_name = self.config["SensorReads"]["filename"]
        all_files = os.listdir(file_path)
        files_list = [fl for fl in all_files if key_name in fl]
        files_list.sort()

        # :param h5file_list: a list of sensor read h5 file names
        # :param reads_per_file: number of reads per file
        # :return: TimeStamp - a list of posix-time (ms since 1/1/70) timestamps for each read

        expr = r'(\d+)-(\d+)-(\d+)_(\d+)-(\d+)-(\d+)-(\d+)'
        write_times = list()

        # here is what is going on here
        # time stamps are parsed off of h5 file names
        # they are reformatted for use with pandas built-in to_datetime function
        # they are localized, then converted to ms-based Epoch time (which, for some reason is in ns in panda)
        for fn in files_list:
            m = re.findall(expr, fn)
            end_time = pd.to_datetime('{}-{}-{} {}:{}:{}.{}'.format(*m[1]))
            end_time_epoch = end_time.tz_localize('US/Pacific').value/10**6
            write_times.append(end_time_epoch)

        mean_write_diff = pd.np.diff(write_times).mean()

        time_stamp = list()
        for ts in write_times:
            for k in range(self.num_reads_per_file):
                time_stamp.append(ts - mean_write_diff + (k+1)*mean_write_diff/self.num_reads_per_file)

        self.read_times = [int(t) for t in time_stamp]

    def alignNOOP(self):
        """
        Extracts the time stamps for instrument states from the ScriptHandler log
        """
        script_key = self.id + self.config["ScriptLog"]
        script_file = os.path.join(self.load_path, script_key)
        with open(script_file, "r") as script_handler:
            script_str = script_handler.readlines()

        script_lines = list()
        for line_str in script_str:
            st_str = line_str.rstrip("\n")
            script_lines.append(st_str.replace(' ', ',').split(','))

        # Finding the lines with NOOP
        state_lines = [sl for sl in script_lines if "NOOP" in sl]
        state_times = [st[0] for st in state_lines]
        state_list = [st[3] for st in state_lines]
        state_list = [st[6:] for st in state_list]

        end_line = script_lines[-1]
        end_time = end_line[0]
        self.state_list = state_list
        self.state_times = state_times
        self.end_time = end_time

    def alignBS2CR(self):
        pass

    def createMask(self):
        """
        Calculates the instrument states and their related time stamps
        """

        script_key = self.id + self.config["ScriptLog"]
        script_file = os.path.join(self.load_path, script_key)
        with open(script_file, "r") as script_handler:
            script_str = script_handler.readlines()

        script_lines = list()
        for line_str in script_str:
            st_str = line_str.rstrip("\n")
            script_lines.append(st_str.replace(' ', ',').split(','))

        is_NOOP = sum(["NOOP" in sl for sl in script_lines]) > 0
        is_discrete = sum(["readInParallelOn" in sl for sl in script_lines]) > 2

        if is_discrete:
            self.num_samples = 32
        else:
            self.num_samples = 64

        self.getReadTimes()

        if is_NOOP:
            self.alignNOOP()
        else:
            self.alignBS2CR()

    def instrumentState(self, time_stamp):
        """
        :param time_stamp: it takes a time stamp as parameter
        :return: the instrument state related to the time stamp
        """
        for i in range(len(self.state_times)-1):
            if time_stamp < int(self.state_times[i+1]):
                return self.state_list[i]
        if time_stamp <= int(self.end_time):
            return self.state_list[-1]
        return "No matching state"

    # Reading the Instrument Data
    def instrumentData(self):
        """
        Reads all the instrument data from the csv file and integrate them as a dataframe exported as a csv file
        """
        instrument_data = None
        for instrument_sensor in self.config["instrument"]:
            file_name = os.path.join(self.load_path, instrument_sensor["path"], self.id + "." +
                                     instrument_sensor["filename"])
            with open(file_name, 'r') as csv_file:
                read_frame = pd.read_csv(csv_file)
            if instrument_data is None:
                instrument_data = read_frame
            else:
                instrument_data = pd.merge(instrument_data, read_frame, how='outer', on='TimeStamp')
        instrument_state = list()
        instrument_data = instrument_data.sort('TimeStamp', ascending=True)
        for ts in instrument_data["TimeStamp"]:
            instrument_state.append(self.instrumentState(ts))

        instrument_data["InstrumentState"] = instrument_state

        # Exporting dataframe to csv file
        instrument_data.to_csv(os.path.join(self.save_path, self.id + '-InstrumentData.csv'))

        self.instrument_data = instrument_data

    # Class for sensor reads
    def sensorReads(self):
        """
        Reads some sample sensors out of the h5 files, and calculates the averages,
        integrate them as a dataframe and dumps it as a csv file
        """

        # Creates the paths to h5 files
        file_path = os.path.join(self.load_path, self.config["SensorReads"]["path"])
        key_name = self.config["SensorReads"]["filename"]
        all_files = os.listdir(file_path)
        files_list = [fl for fl in all_files if key_name in fl]
        files_list.sort()
        num_rand_sen = self.config['SensorReads']['numRandSen']

        # Choosing random With-Magnet and No-Magnet Sensors
        no_magnet_ids = numpy.where(self.no_magnet)
        with_magnet_ids = numpy.where(numpy.invert(self.no_magnet))
        no_magnet_ids = no_magnet_ids[0]
        with_magnet_ids = with_magnet_ids[0]

        no_magnet_sample = random.sample(no_magnet_ids, num_rand_sen)
        with_magnet_sample = random.sample(with_magnet_ids, num_rand_sen)

        no_magnet_reads = numpy.zeros((num_rand_sen, len(self.read_times)))
        no_magnet_avg = numpy.zeros(len(self.read_times))
        with_magnet_reads = numpy.zeros((num_rand_sen, len(self.read_times)))
        with_magnet_avg = numpy.zeros(len(self.read_times))

        # Reading the h5 files
        k = 0
        for fn in files_list:
            if k % 100 == 0:
                print k
            #if k==200:
            #    break
            # try this for every h5 file
            try:
                file_name = os.path.join(file_path, fn)
                with h5py.File(file_name, 'r') as h5_file:
                    if self.num_phases == 4:
                        read_nm = h5_file[self.phases[0]].value[no_magnet_sample] - \
                            h5_file[self.phases[2]].value[no_magnet_sample]
                        read_wm = h5_file[self.phases[0]].value[with_magnet_sample] - \
                            h5_file[self.phases[2]].value[with_magnet_sample]
                        mean_nm = read_nm.mean(axis=0)
                        mean_wm = read_wm.mean(axis=0)
                    elif self.num_phases == 2 and self.phases[1] == '040':
                        read_nm = h5_file[self.phases[0]].value[no_magnet_sample] - \
                            h5_file[self.phases[1]].value[no_magnet_sample]
                        read_wm = h5_file[self.phases[0]].value[with_magnet_sample] - \
                            h5_file[self.phases[1]].value[with_magnet_sample]
                        mean_nm = read_nm.mean(axis=0)
                        mean_wm = read_wm.mean(axis=0)
                    else:
                        read_nm = h5_file[self.phases[0]].value[no_magnet_sample]
                        read_wm = h5_file[self.phases[0]].value[with_magnet_sample]
                        mean_nm = read_nm.mean(axis=0)
                        mean_wm = read_wm.mean(axis=0)

                    for n in range(len(no_magnet_sample)):
                        no_magnet_reads[n][range(k*self.num_reads_per_file, (k+1)*self.num_reads_per_file)] = read_nm[n]

                    for n in range(len(with_magnet_sample)):
                        with_magnet_reads[n][range(k*self.num_reads_per_file, (k+1)*self.num_reads_per_file)] = \
                            read_wm[n]

                    with_magnet_avg[range(k*self.num_reads_per_file, (k+1)*self.num_reads_per_file)] = mean_wm
                    no_magnet_avg[range(k*self.num_reads_per_file, (k+1)*self.num_reads_per_file)] = mean_nm

                k = k+1

            # Failed to read the h5 file
            except:
                print "The h5 file is corrupted!"

        num_sample_sen = no_magnet_reads.shape[0]

        # Defining the column names of the dataframe
        nm_col_names = ['NoMagnetSensor%d' % (i+1) for i in range(num_sample_sen)]
        wm_col_names = ['WithMagnetSensor%d' % (i+1) for i in range(num_sample_sen)]

        nm_df = pd.DataFrame(no_magnet_reads.transpose(), index=self.read_times, columns=nm_col_names)
        wm_df = pd.DataFrame(with_magnet_reads.transpose(), index=self.read_times, columns=wm_col_names)
        avg_df = pd.DataFrame({'noMagentAverage': no_magnet_avg, 'withMagnetAverage': with_magnet_avg},
                              index=self.read_times)

        # Extracting instrument states
        instrument_state = list()
        for ts in self.read_times:
            instrument_state.append(self.instrumentState(ts))

        # Adding the instrument states to the dataframe
        avg_df["InstrumentState"] = instrument_state
        sensor_reads = pd.concat([avg_df, nm_df, wm_df], axis=1)

        # Exporting the dataframe to a csv file
        sensor_reads.to_csv(os.path.join(self.save_path, self.id + '-SensorData.csv'))
        self.sensor_reads = sensor_reads
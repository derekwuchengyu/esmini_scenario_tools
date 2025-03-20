# extract log file parameters information into csv file, for saving storage space and easy to read

import os
import csv
import pandas as pd
import numpy as np
import sys
import os.path
import argparse

from ttc_util import extract_pextract_parameters_from_log, read_csv_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract log file parameters information into csv file')
    parser.add_argument('--scenario', required=True, help='Scenario name to process')
    parser.add_argument('--log_folder', required=True, help='Folder containing log files')
    args = parser.parse_args()

    scenario_name = args.scenario
    log_folder = args.log_folder

    permutation_csv = f'{log_folder}/{scenario_name}_permutation_value.csv'
    if os.path.exists(permutation_csv):
        print(f"Permutat csv already exists, delete it first!")
        exit(0)
    logs = [file_name for file_name in os.listdir(log_folder) if file_name.startswith(f'{scenario_name}_') and file_name.endswith('.txt')]
    if not logs:
        print(f"No log files found for scenario {scenario_name}")
        exit(0)

    param = extract_pextract_parameters_from_log(f'{log_folder}/{logs[0]}')
    if not param:
        print(f"No parameters found in log file {logs[0]}, ecexuting scenario may failed!")
        exit(0)

    columns = ['permutation'] + list(param.keys())
    # flush csv file everytime
    with open(permutation_csv, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(columns)

    for log in logs:
        param = extract_pextract_parameters_from_log(f'{log_folder}/{log}')
        permutation = log.split('_')[-1].split('.')[0]
        row = [log] + list(param.values())
        with open(permutation_csv, mode='a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(row)

    # print(f"Extracted parameters from {len(logs)} log files for scenario {scenario_name}")
    # delete log files
    for log in logs:
        os.remove(f'{log_folder}/{log}')

    




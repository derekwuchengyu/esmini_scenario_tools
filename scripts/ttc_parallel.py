# Launch parallel esmini runs as defined by a parameter value distribution

#
# Example:
# python ./scripts/run_distribution.py --osc .\resources\xosc\cut-in.xosc --param_dist .\resources\xosc\cut-in_parameter_set.xosc --fixed_timestep 0.05 --headless

"""
print('Time {:.2f} ObjId {} roadId {} laneId {} s {:.2f} laneOffset {:.2f} s {:.2f} x {:.2f} y {:.2f} heading {:.2f}'.format(
    ego_state.timestamp, ego_state.id, ego_state.roadId, ego_state.laneId, ego_state.s, ego_state.laneOffset,
    ego_state.s, ego_state.x, ego_state.y, ego_state.h))
"""


from multiprocessing.pool import ThreadPool
import subprocess
import sys
import os.path
from ttc_util import *
from ttc_config import *
import csv
import ctypes
import pandas as pd
import os
import argparse
from tqdm import tqdm


if len(sys.argv) < 3 and 0:
    print('Usage: {} <esmini args>'.format(os.path.basename(sys.argv[0])))
    print('\nMake sure to add at least:')
    print('  --osc <scenario file>')
    print('  --param_dist <parameter distribution file>')
    print('  --fixed_timestep <timestep>')
    print('  --headless')
    print('\nExample:\n  python {} --osc cut-in.xosc --param_dist param_set.xosc --fixed_timestep 0.05 --headless'.
        format(os.path.basename(sys.argv[0])))
    exit(-1)


TTC_THRESHOLD = 2.5
START = 1 # start time for ttc calculation, in seconds. For discarding the initial jitter

# globals
launched = 0
done = 0
n_runs = 0

metrifcs_csv = '{scenario_name}_metrics.csv'

def calculate_ttc_for_scenario(scenario_name, dat_folder, log_folder, metrics_folder):
    record_csv = [file_name for file_name in os.listdir(dat_folder) if file_name.endswith('.csv') and file_name.startswith(scenario_name+'_')]


    metrics_csv = os.path.join(metrics_folder, metrifcs_csv.format(scenario_name=scenario_name))
    log_file_name = f"{record_csv[0].split('.')[0]}.txt"
    parameters = get_parameters_from_log_csv(log_file_name, log_folder)
    with open(metrics_csv, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        header = ['min_ttc'] + [col for col in RECORD_PARAMS if col in parameters.keys()]
        if '_02' in scenario_name:
            header = ['min_ttc'] + [col for col in RECORD_PARAMS if col in parameters.keys()] + ['ego_a1_ttc', 'ego_a2_ttc', 'a1_a2_ttc']
        csv_writer.writerow(header)
    
    for file_name in tqdm(record_csv, desc="Calculating TTC"):
        log_file_name = f"{file_name.split('.')[0]}.txt"
        parameters = get_parameters_from_log_csv(log_file_name, log_folder)
        
        
        csv_path = os.path.join(dat_folder, file_name)
        csv_data = read_csv_data(csv_path)

        ttc_record = []
        min_ttc = float('inf')
        min_ego_a1_ttc = float('inf')
        min_ego_a2_ttc = float('inf')
        min_a1_a2_ttc = float('inf')
        min_ttc_current_time = None
        min_ttc_ego_pos = None
        min_ttc_agent1_pos = None
        min_ttc_agent2_pos = None
        min_ttc_ego_speed = None
        min_ttc_agent1_speed = None
        min_ttc_agent2_speed = None

        for _, row in csv_data.iterrows():
            current_time = float(row['time'])
            if current_time < START: #Avoid initial jitter
                continue
            if row['name'] == 'Ego':
                ego_pos = [float(row['x']), float(row['y'])]
                ego_speed = float(row['speed'])
                ego_h = float(row['h'])
            elif row['name'] == 'Agent1':
                agent1_pos = [float(row['x']), float(row['y'])]
                agent1_speed = float(row['speed'])
                agent1_h = float(row['h'])
            elif row['name'] == 'Agent2':
                agent2_pos = [float(row['x']), float(row['y'])]
                agent2_speed = float(row['speed'])
                agent2_h = float(row['h'])

            if 'ego_pos' in locals() and 'agent1_pos' in locals():
                ego_a1_ttc, _ = calculate_ttc(ego_pos, ego_speed, ego_h, agent1_pos, agent1_speed, agent1_h)
                # ttc_record.append(ego_a1_ttc)
                min_ego_a1_ttc = min(min_ego_a1_ttc, ego_a1_ttc)
                min_ttc = min(min_ttc, ego_a1_ttc)
                if min_ttc == ego_a1_ttc:
                    min_ttc_current_time = current_time
                    min_ttc_ego_pos = ego_pos
                    min_ttc_agent1_pos = agent1_pos
                    min_ttc_ego_speed = ego_speed
                    min_ttc_agent1_speed = agent1_speed

            if 'ego_pos' in locals() and 'agent2_pos' in locals():
                ego_a2_ttc, _ = calculate_ttc(ego_pos, ego_speed, ego_h, agent2_pos, agent2_speed, agent2_h)
                # ttc_record.append(ego_a2_ttc)
                min_ego_a2_ttc = min(min_ego_a2_ttc, ego_a2_ttc)
                min_ttc = min(min_ttc, ego_a2_ttc)
                if min_ttc == ego_a2_ttc:
                    min_ttc_current_time = current_time
                    min_ttc_ego_pos = ego_pos
                    min_ttc_agent2_pos = agent2_pos
                    min_ttc_ego_speed = ego_speed
                    min_ttc_agent2_speed = agent2_speed
            # Agent1 and agent2 's ttc calculation
            if 'agent1_pos' in locals() and 'agent2_pos' in locals():
                a1_a2_ttc, _ = calculate_ttc(agent1_pos, agent1_speed, agent1_h, agent2_pos, agent2_speed, agent2_h)
                # ttc_record.append(ttc)
                min_a1_a2_ttc = min(min_a1_a2_ttc, a1_a2_ttc)
                min_ttc = min(min_ttc, a1_a2_ttc)
                if min_ttc == a1_a2_ttc:
                    min_ttc_current_time = current_time
                    min_ttc_agent1_pos = agent1_pos
                    min_ttc_agent2_pos = agent2_pos
                    min_ttc_agent1_speed = agent1_speed
                    min_ttc_agent2_speed = agent2_speed

        with open(metrics_csv, mode='a', newline='') as file:
            # min ttc float format %.4f
            formatted_min_ttc = "{:.3f}".format(min_ttc)
            csv_writer = csv.writer(file)
            if '_02' in scenario_name:
                csv_writer.writerow([formatted_min_ttc] + [parameters[col] for col in RECORD_PARAMS if col in parameters.keys()] + [min_ego_a1_ttc, min_ego_a2_ttc, min_a1_a2_ttc])
            else:
                csv_writer.writerow([formatted_min_ttc] + [parameters[col] for col in RECORD_PARAMS if col in parameters.keys()])

        # print(f"Processed {file_name}: Min TTC: {min_ttc:.2f}, Time: {min_ttc_current_time:.2f}")

def update_csv_param_range_all(scenario_name, metrics_folder, config_folder):
    metrics_file = f"{scenario_name}_metrics.csv"
    metrics_csv = os.path.join(metrics_folder, metrics_file)
        
    if 1:
        data = pd.read_csv(metrics_csv)
    # else:
        # print(f"File not found: {metrics_csv}")
        # return
    
    # 計算最大最小值
    filtered_data = data[data['min_ttc'] < TTC_THRESHOLD]
    if filtered_data.empty:
        filtered_data = data[data['min_ttc'] == data['min_ttc'].min()].iloc[0:1]
        # # 把file name 記錄下來
        # with open("none_critical_scenario_combined_0115.txt", "a") as f:
        #     f.write(os.path.basename(metrics_csv) + "\n")

    
    # Filter UPDATE_PARAMS to only include columns that exist in filtered_data
    valid_update_params = [param for param in UPDATE_PARAMS if param in filtered_data.columns]
    stats = filtered_data[valid_update_params].agg(['max', 'min'])

    # 解析文件路徑
    scenario_folder = '_'.join(os.path.basename(metrics_csv).split('_')[:-2])
    scenario_id_csv = os.path.basename(metrics_csv).split('_')[-2] + ".csv"
    parameter_csv = os.path.join(config_folder, scenario_folder, scenario_id_csv)
    # print(scenario_folder, scenario_id_csv, parameter_csv)
        
    # 讀取數據
    original_data = pd.read_csv(parameter_csv)

    # 參數範圍篩選、調整
    changed = False
    changed_params = {}
    for param in valid_update_params:
        max_value = stats.loc['max', param]
        min_value = stats.loc['min', param]
        old_max_value = float(original_data[param].values[0].split('~')[1])
        old_min_value = float(original_data[param].values[0].split('~')[0])
        # print(f"Parameter: {param}")
        # print(f"New: {min_value}~{max_value}")
        # print(f"Old: {old_min_value}~{old_max_value}")
        if old_max_value != max_value or old_min_value != min_value:
            changed = True
            changed_params[param] = (old_min_value, old_max_value, min_value, max_value)
        original_data[param] = f"{min_value}~{max_value}"

    # 保存文件  
    original_data.to_csv(parameter_csv, index=False)
    # print(f"Updated {parameter_csv}")

    if changed:
        print("Changed!", changed_params)
        # with open("changed_scenario_combined_0115.txt", "a") as f:
        #     f.write(scenario_name + "\n")

def delete_scenario_csv_files(scenario_name, metrics_folder, dat_folder):
    # if scenario metric are calculated, and exit in ttc_result, delete the csv files
    metrics_csv = os.path.join(metrics_folder, metrifcs_csv.format(scenario_name=scenario_name))
    if not os.path.exists(metrics_csv):
        return
    csv_files = [file_name for file_name in os.listdir(dat_folder) if file_name.startswith(scenario_name) and file_name.endswith('.csv')]
    for csv_file in csv_files:
        os.remove(os.path.join(dat_folder, csv_file))
        # print(f"Deleted {csv_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate TTC and update parameter ranges for scenarios')
    parser.add_argument('--scenario', help='Scenario name to process')
    parser.add_argument('--dat_folder', required=True, help='Folder containing .dat files')
    parser.add_argument('--log_folder', required=True, help='Folder containing log files')
    parser.add_argument('--metrics_folder', required=True, help='Folder to save metrics CSV files')
    parser.add_argument('--config_folder', required=True, help='Folder containing scenario configuration files')
    args = parser.parse_args()

    # if metrics file already exist, skip
    metrics_csv = os.path.join(args.metrics_folder, metrifcs_csv.format(scenario_name=args.scenario))
    if 0 and os.path.exists(metrics_csv):
        print(f"Metrics file already exists.")
        exit(0)

    # calculate_ttc_for_scenario(args.scenario, args.dat_folder, args.log_folder, args.metrics_folder)
    update_csv_param_range_all(args.scenario, args.metrics_folder, args.config_folder)
    # delete_scenario_csv_files(args.scenario, args.metrics_folder, args.dat_folder)

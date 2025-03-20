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
from ttc_util import SEScenarioObjectState, SEParameter, init_esmini, evaluate_run_with_args,calculate_distance,calculate_ttc, get_parameter_value
import csv
import ctypes
import pandas as pd
import os
from tqdm import tqdm


if len(sys.argv) < 3:
    print('Usage: {} <esmini args>'.format(os.path.basename(sys.argv[0])))
    print('\nMake sure to add at least:')
    print('  --osc <scenario file>')
    print('  --param_dist <parameter distribution file>')
    print('  --fixed_timestep <timestep>')
    print('  --headless')
    print('\nExample:\n  python {} --osc cut-in.xosc --param_dist param_set.xosc --fixed_timestep 0.05 --headless'.
        format(os.path.basename(sys.argv[0])))
    exit(-1)


se = init_esmini()

TTC_THRESHOLD = 2.5

# globals
launched = 0
done = 0
n_runs = 0
metrics_csv = 'ttc_result/{scenario_name}_metrics.csv'
parameter_names = ['Agent1_S', 'Agent1_Speed', 'Agent1_1_SA_EndSpeed', 'Agent1_1_TA_DynamicDuration', 'Agent1_1_SA_DynamicDuration','Ego_Speed']

# 定義參數名稱
update_parameter_names = [
    # 'Agent1_S', 
    'Agent1_Speed',
    'Agent1_1_SA_EndSpeed',
    'Agent1_1_TA_DynamicDuration',
    'Agent1_1_SA_DynamicDuration'
    # , 'Ego_Speed'
    ]


# Agent1_init_lat_pos,Agent1_init_long_pos,Agent1_S,Agent1_Speed,Agent1_1_SA_EndSpeed,Agent1_1_SA_DynamicDuration,Agent1_1_SA_DynamicDelay,Agent1_1_DynamicDelay,Agent1_1_TA_Offset,Agent1_1_TA_Period,Agent1_1_TA_Times
# 1,01FL-ZZ_1,Bike zigzag at FL-M1 - keepingZZ,junction,noTrafficLight,,drivingForward,cruising,goingStraight,,M1,drivingForward,cruising,goingStraight,,sameAsEgo,moving,leftOfEgo,inFrontOfEgo,0~20,40~60,40~60,5~5,0~0,0~0,-1,0.2~1,3

def print_status():
    print('Launched: {}/{} Done: {}'.format(launched, n_runs, done), end='\r', flush=True)
    
def launch_scenario(index):
    """Launch a single Esmini scenario and calculate TTC."""
    global launched, done
    launched += 1
    print_status()

    args = list(sys.argv[1:]) + ['--disable_stdout'] + \
        ['--param_permutation'] + [str(index)]
    # print(args)
    argc = len(args)
    argv = (ctypes.POINTER(ctypes.c_char) * (argc))()
    for i, arg in enumerate(args):
        argv[i] = ctypes.create_string_buffer(arg.encode('utf-8'))
        if arg == '--fixed_timestep':
            dt = float(args[i+1])


    # init esmini
    if se.SE_InitWithArgs(argc, argv) != 0:
        exit(-1)


    # print("================>Initialized esmini")


    # Initialize scenario objects and variables
    ego_state = SEScenarioObjectState()
    agent1_state = SEScenarioObjectState()
    param_value = SEParameter()
    ttc_record = []
    min_ttc = float('inf')
    ego_name = ctypes.create_string_buffer(b"Ego")
    agent1_name = ctypes.create_string_buffer(b"Agent1")
    



    while se.SE_GetQuitFlag() == 0:
        
        # break
        if se.SE_GetObjectNumberOfCollisions(0) != 0:
            for i in range(se.SE_GetObjectNumberOfCollisions(0)):
                agent_name = ctypes.string_at(se.SE_GetObjectName(se.SE_GetObjectCollision(0, i))).decode('utf-8')
                print(f'Collision between Ego and {agent_name}')
            break

        # Get simulation time and object states
        current_time = se.SE_GetSimulationTime()
        se.SE_GetObjectState(se.SE_GetIdByName(ego_name), ctypes.byref(ego_state))
        se.SE_GetObjectState(se.SE_GetIdByName(agent1_name), ctypes.byref(agent1_state))



        ego_pos = [ego_state.x, ego_state.y]
        agent_pos = [agent1_state.x, agent1_state.y]
        # print("========>Ego pos: ", ego_pos, "Ego speed: ", ego_speed, "Agent pos: ", agent_pos, "Agent speed: ", agent_speed)

        # Calculate TTC
        ttc, rel_dist_along_heading = calculate_ttc(ego_pos, ego_state.speed, ego_state.h, agent_pos, agent1_state.speed, agent1_state.h)
        # print("===========>ttc: ", ttc, "rel_dist_along_heading: ", rel_dist_along_heading)
        
        ttc_record.append(ttc)
        min_ttc = min(min_ttc, ttc)
        if min_ttc == ttc:
            min_ttc_current_time = current_time
            min_ttc_ego_pos = ego_pos
            min_ttc_agent_pos = agent_pos
            min_ttc_ego_speed = ego_state.speed
            min_ttc_agent_speed = agent1_state.speed


        # Step simulation
        # se.SE_StepDT(0.05)
        se.SE_StepDT(dt)
        

    # Open the CSV file for writing
    with open(metrics_csv, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        parameter_values = [get_parameter_value(name, se) for name in parameter_names]
        print("=====>Parameter values: ",list(zip(parameter_names, parameter_values)))

        # Write the row to the CSV
        csv_writer.writerow([min_ttc] + parameter_values)

    done += 1
    print("=====>Min TTC: {:.2f}, Time: {:.2f}".format(min_ttc, min_ttc_current_time))
    # print("========>Ego pos: ", min_ttc_ego_pos, "Ego speed: ", min_ttc_ego_speed, "Agent pos: ", min_ttc_agent_pos, "Agent speed: ", min_ttc_agent_speed)
    print_status()

    return min_ttc


if __name__ == '__main__':
    if 'ZZ' in os.path.basename(sys.argv[2]):
        parameter_names = [
              'Agent1_S',
              'Agent1_Speed',
              'Agent1_1_SA_EndSpeed',
              'Agent1_1_TA_Offset',
              'Agent1_1_TA_Period',
              'Agent1_1_TA_Times',
              'Ego_Speed']
        update_parameter_names = [
            #   'Agent1_S',
              'Agent1_Speed',
              'Agent1_1_SA_EndSpeed',
            #   'Agent1_1_TA_Offset',
              'Agent1_1_TA_Period',
            #   'Agent1_1_TA_Times',
            #   'Ego_Speed'
              ]
        
    print("parameter_names: ",parameter_names, update_parameter_names, os.path.basename(sys.argv[2]), 'ZZ' in os.path.basename(sys.argv[2]))
    # 創建CSV
    metrics_csv = metrics_csv.format(scenario_name=os.path.splitext(os.path.basename(sys.argv[2]))[0])
    with open(metrics_csv, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        
        
        # Write the column names
        header = ['min_ttc'] + parameter_names
        csv_writer.writerow(header)


    p = subprocess.run(
        ['./bin/esmini', '--disable_stdout'] + list(sys.argv[1:]) + ['--return_nr_permutations'],
        stdout=subprocess.DEVNULL
    )
    n_runs = p.returncode

    # Run scenarios in parallel
    print_status()


    # with ThreadPool() as pool:
    #     pass
    #     min_ttc_results = pool.map(launch_scenario, range(n_runs))

    min_ttc = [0] * n_runs
    for i in tqdm(range(n_runs)):
        # continue
        current_ttc = launch_scenario(i)



    # 讀取 CSV 文件
    data = pd.read_csv(metrics_csv)
    # 計算最大最小值
    filtered_data = data[data['min_ttc'] < TTC_THRESHOLD]
    if filtered_data.empty:
        filtered_data = data[data['min_ttc'] == data['min_ttc'].min()]
        # 把file name 記錄下來
        with open("none_critical_scenario.txt", "a") as f:
            f.write(os.path.basename(metrics_csv) + "\n")
    stats = filtered_data[parameter_names].agg(['max', 'min'])
  

    # 解析文件路徑
    scenario_folder = '_'.join(os.path.basename(metrics_csv).split('_')[:-2])
    scenario_id_csv = os.path.basename(metrics_csv).split('_')[-2] + ".csv"
    parameter_csv = os.path.join("/home/hcis-s19/Documents/ChengYu/hcis_scenario_generation/scenario_config_combined", scenario_folder, scenario_id_csv)
    # print(scenario_folder, scenario_id_csv, parameter_csv)
    # exit()
   
    # 讀取數據
    original_data = pd.read_csv(parameter_csv)

    # 參數範圍篩選、調整
    for param in update_parameter_names:
        max_value = stats.loc['max', param]
        min_value = stats.loc['min', param]
        print(f"Parameter: {param}, Max: {max_value}, Min: {min_value}")
        original_data[param] = f"{min_value}~{max_value}"

    # 保存更新後的數據
    original_data.to_csv(parameter_csv, index=False)


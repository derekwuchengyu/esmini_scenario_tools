import os
from scenariogeneration import xosc, prettyprint


def create_xosc_range(lower_bound, upper_bound, step_size):
    ret = xosc.DistributionRange(
        step_size, xosc.Range(lower_bound, upper_bound))
    return ret


def generate_pvd(ScenarioFileName, ParaDict):
    det = xosc.Deterministic()
    for key in ParaDict:
        det.add_single_distribution(key, create_xosc_range(*ParaDict[key]))
    pvd = xosc.ParameterValueDistribution(
        "test", "hcis", ScenarioFileName, det)
    return pvd
# # some names used in both scenario and
# scenario_filename = "hcistest.xosc"


# det = xosc.Deterministic()
# # DistributionRange = xosc.DistributionRange(0.5, xosc.Range(0, 1.5))
# # # sgd = xosc.DistributionSet([DistributionRange])

# # det.add_single_distribution(ego_param_name, DistributionRange)

# det.add_single_distribution("NAME", create_xosc_range(0, 1.5, 0.5))
# det.add_single_distribution("NAME2", create_xosc_range(10, 20, 3))
# pvd = xosc.ParameterValueDistribution("test", "SYS", scenario_filename, det)

# prettyprint(pvd.get_element())

# pvd.write_xml(os.path.basename(__file__).replace(".py", ".xosc"))

import sys
import pandas as pd
import os

def get_parameter_default_range(scenario_name):

    if '01' in scenario_name:
        Agent = 'Agent1'
    elif '02' in scenario_name:
        Agent = 'Agent2'

    para_default_range = {
                    #    "Agent1_S": [0, 20, 10],  
                    f"{Agent}_1_TA_DynamicDuration": [0, 4, 2],
                    f"{Agent}_Speed": [40, 60, 10], # [lower_bound, upper_bound, step_size]
                    f"{Agent}_1_SA_EndSpeed": [40, 60, 10],
                    f"{Agent}_1_SA_DynamicDuration": [0, 4, 2]
                    }
    if 'ZZ' in scenario_name:
        para_default_range = {
                    #    "Agent1_S": [0, 20, 10],  
                        f"{Agent}_Speed": [40, 60, 10], # [lower_bound, upper_bound, step_size]
                        f"{Agent}_1_SA_EndSpeed": [40, 60, 10],
                        f"{Agent}_1_SA_DynamicDuration": [0, 4, 2],
                        # f"{Agent}_1_TA_Offset": [-1, 1, 0.2],
                        f"{Agent}_1_TA_Period": [0.2, 1, 0.4],
                        # f"{Agent}_1_TA_Times": [1, 3, 1],
                        } 
 
    return para_default_range

ESMINI_ROOT = '/home/hcis-s19/Documents/ChengYu/esmini-demo'


if __name__ == "__main__":

    test_scenario = sys.argv[2].split('.')[0]
    config_folder_root = sys.argv[6]
    
    scenario_folder = '_'.join(os.path.basename(test_scenario).split('_')[:-1])
    scenario_id_csv = os.path.basename(test_scenario).split('_')[-1] + ".csv"
    parameter_csv = os.path.join(f"{config_folder_root}", scenario_folder, scenario_id_csv)
    parameter_data = pd.read_csv(parameter_csv)

    ScenarioName = f"{ESMINI_ROOT}/scripts/para_test.xosc"

    ParaDict = {}
    for simple_scenario in scenario_folder.split('_'):
        p = get_parameter_default_range(simple_scenario)
        ParaDict.update(p)

    # from pprint import pprint
    # pprint(ParaDict);
    # exit()
    
    # 固定長度
    title_length = 30
    data_length = 15

    # 印表頭
    DISPLAY_INFO = int(sys.argv[4])
    if DISPLAY_INFO:
        print(f"{'Parameter'.ljust(title_length)} {'Value'.ljust(data_length)}")
        print("-" * (title_length + data_length))

    for key, val in ParaDict.items():
        if DISPLAY_INFO:
            print(f"{key.ljust(title_length)} {str(parameter_data[key].values).ljust(data_length)}")

        if '~' not in str(parameter_data[key].values[0]):
            continue
        min_val, max_val = parameter_data[key].values[0].split("~")
        ParaDict[key] = [float(min_val), float(max_val), val[2]] 
    pvd = generate_pvd(ScenarioName, ParaDict)

    # prettyprint(pvd.get_element())

    pvd.write_xml(ScenarioName)

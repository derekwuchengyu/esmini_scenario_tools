import ctypes
import evaluate
from sys import platform
import pandas as pd
import numpy as np
import re
import os

class SEScenarioObjectState(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("model_id", ctypes.c_int),
        ("control", ctypes.c_int),
        ("timestamp", ctypes.c_float),
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("h", ctypes.c_float),
        ("p", ctypes.c_float),
        ("r", ctypes.c_float),
        ("roadId", ctypes.c_int),
        ("junctionId", ctypes.c_int),
        ("t", ctypes.c_float),
        ("laneId", ctypes.c_int),
        ("laneOffset", ctypes.c_float),
        ("s", ctypes.c_float),
        ("speed", ctypes.c_float),
        ("centerOffsetX", ctypes.c_float),
        ("centerOffsetY", ctypes.c_float),
        ("centerOffsetZ", ctypes.c_float),
        ("width", ctypes.c_float),
        ("length", ctypes.c_float),
        ("height", ctypes.c_float),
        ("objectType", ctypes.c_int),
        ("objectCategory", ctypes.c_int),
        ("wheelAngle", ctypes.c_float),
        ("wheelRot", ctypes.c_float),
    ]


class SEParameter(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("value", ctypes.c_void_p),
    ]


def init_esmini():
    # print("Initializing esmini")
    if platform == "linux" or platform == "linux2":
        se = ctypes.CDLL("./bin/libesminiLib.so")
    elif platform == "darwin":
        se = ctypes.CDLL("./bin/libesminiLib.dylib")
    elif platform == "win32":
        se = ctypes.CDLL("./bin/esminiLib.dll")
    else:
        print("Unsupported platform: {}".format(platform))
        quit()

    # specify arguments types of esmini function
    se.SE_InitWithArgs.argtypes = [
        ctypes.c_int, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
    se.SE_StepDT.argtypes = [ctypes.c_float]
    se.SE_ReportObjectSpeed.argtypes = [ctypes.c_int, ctypes.c_float]
    se.SE_GetObjectAcceleration.argtypes = [ctypes.c_int]
    se.SE_GetObjectName.restype = ctypes.POINTER(ctypes.c_char)
    se.SE_GetSimTimeStep.restype = ctypes.c_float
    se.SE_GetSimulationTime.restype = ctypes.c_float
    se.SE_GetObjectAcceleration.restype = ctypes.c_float
    se.SE_GetParameterDouble.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)]
    se.SE_GetParameterDouble.restype = ctypes.c_int

    return se

def evaluate_run_with_args(se, index):
    return evaluate.run(se, 'ori', False, 0.05, index)


def calculate_distance(pos1, pos2):
    return np.linalg.norm(np.array(pos1) - np.array(pos2))

def calculate_ttc(ego_pos, ego_raw_vel, ego_heading, other_pos, other_raw_vel, other_heading):
    """
    Calculate TTC considering the relative position and velocity of two agents.

    Args:
        ego_pos (tuple): (x, y) position of the ego vehicle.
        ego_vel (tuple): (vx, vy) velocity of the ego vehicle.
        ego_heading (float): Heading angle of the ego vehicle (in radians).
        other_pos (tuple): (x, y) position of the other vehicle.
        other_vel (tuple): (vx, vy) velocity of the other vehicle.

    Returns:
        tuple: The TTC value and the relative distance along heading. Returns (float('inf'), None) if no collision is expected.
    """
    ego_vel = [ego_raw_vel * np.cos(ego_heading), ego_raw_vel * np.sin(ego_heading)]
    other_vel = [other_raw_vel * np.cos(other_heading), other_raw_vel * np.sin(other_heading)]
    # print("ego_heading: ", ego_heading, "ego_vel: ", ego_vel, "other_heading: ", other_heading, "other_vel: ", other_vel)

    # Relative position and velocity
    rel_pos = np.array([other_pos[0] - ego_pos[0], other_pos[1] - ego_pos[1]])
    rel_vel = np.array([other_vel[0] - ego_vel[0], other_vel[1] - ego_vel[1]])

    # Project relative position onto ego heading
    ego_direction = np.array([np.cos(ego_heading), np.sin(ego_heading)])
    rel_dist_along_heading = np.dot(rel_pos, ego_direction)
    # print("rel_dist_along_heading: ", rel_dist_along_heading)

    # Skip objects behind ego or too far away
    if rel_dist_along_heading < -5.0:  # Behind ego and more than 1 meter away
        return float('inf'), None

    # Distance magnitude
    distance = np.linalg.norm(rel_pos)

    # Relative speed along heading
    rel_speed_along_heading = np.dot(rel_vel, ego_direction)

    if rel_speed_along_heading >= 0:
        # Vehicles are moving apart or stationary relative to each other
        return float('inf'), None

    # Calculate TTC
    ttc = distance / abs(rel_speed_along_heading)
    return ttc, rel_dist_along_heading


def get_parameter_value(param_name, se):
    param_value = ctypes.c_double()  # Assuming all parameters are doubles
    result = se.SE_GetParameterDouble(param_name.encode('utf-8'), ctypes.byref(param_value))
    if result == 0:  # Assuming 0 indicates success
        return param_value.value
    else:
        return None  # If retrieval fails, return None
    
def update_csv_param_range():
    import csv
    with open('param_range.csv', mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(['param_name', 'min', 'max'])


def extract_pextract_parameters_from_log(log_file_path):
    parameters = {}
    with open(log_file_path, 'r') as file:
        for line in file:
            match = re.match(r'Parameters\.cpp / \d+ / Print\(\):\s+(\w+)\s+=\s+(.+)', line)
            if match:
                key, value = match.groups()
                try:
                    value = float(value)
                except ValueError:
                    pass
                parameters[key] = value
    return parameters

def extract_parameters_from_log_2(log_file_path):
    parameters = {}
    with open(log_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'ScenarioReader.cpp / 158 / loadOSCFile():' in line:
                parts = line.split(':')
                param_name = parts[1].strip()
                param_value = float(parts[2].strip())
                parameters[param_name] = param_value
    return parameters

def read_csv_data(file_path):
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        if first_line.startswith("Version:"):
            data = pd.read_csv(file_path, skiprows=1)
        else:
            data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()  # Remove whitespace from column names
    data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Remove whitespace from values
    return data

def get_parameters_from_log_csv(log_file_name, log_folder):
    scenario_name = "_".join(log_file_name.split('_')[:-3])
    log_csv_path = f'{log_folder}/{scenario_name}_permutation_value.csv'
    # print(log_file_name,scenario_name, log_csv_path);exit()
    data = pd.read_csv(log_csv_path)
    data = data[data.permutation == log_file_name]
    if data.empty:
        return None
    parameters = data.iloc[0, 1:].to_dict()
    return parameters

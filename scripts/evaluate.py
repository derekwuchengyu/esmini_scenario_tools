import ctypes
from sys import platform
import sys
from fastdtw import fastdtw
import numpy as np

# Definition of SE_ScenarioObjectState struct


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


def init():
    print("Initializing esmini")
    if platform == "linux" or platform == "linux2":
        se = ctypes.CDLL("../bin/libesminiLib.so")
    elif platform == "darwin":
        se = ctypes.CDLL("../bin/libesminiLib.dylib")
    elif platform == "win32":
        se = ctypes.CDLL("../bin/esminiLib.dll")
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
    se.SE_GetObjectAcceleration.restype = ctypes.c_float

    return se


def run(se, mode, visualize=False, timestep=None, index=None):
    # create the list of arguments
    args = [
        "--window", "1920", "60", "1920", "1080",
        "--osc", "../resources/xosc/cut_example.xosc",
        "--fixed_timestep", "0.1",
        # "--disable_controllers",
        # "--headless",
        # "--collision"
        "--text_scale", "3"
    ]

    if timestep:
        args += ["--fixed_timestep", str(timestep)]

    if visualize:
        args += ["--window", "1920", "60", "1920", "1080"]
    else:
        args += ["--headless"]

    if mode == 'ori':
        args += ["--disable_controllers"]

    if index:
        args += ["--param_permutation", str(index)]

    args = sys.argv + args

    dt = -0.1  # default value for timestep
    # prepare argument list for ctypes use
    argc = len(args)
    argv = (ctypes.POINTER(ctypes.c_char) * (argc))()
    for i, arg in enumerate(args):
        argv[i] = ctypes.create_string_buffer(arg.encode('utf-8'))
        if arg == '--fixed_timestep':
            dt = float(args[i+1])

    "---------------------------------"

    # init esmini
    if se.SE_InitWithArgs(argc, argv) != 0:
        exit(-1)

    # object that will be passed and filled in with object state info
    obj_state = SEScenarioObjectState()

    min_acc = [0]*se.SE_GetNumberOfObjects()
    speed = 10
    acc = 0.1
    ego_acc = []
    agent_acc = []

    while se.SE_GetQuitFlag() == 0:
        # se.SE_ReportObjectSpeed(1, 0)

        # Get number of collisions for object with id 0 (ego)
        if se.SE_GetObjectNumberOfCollisions(0) != 0:
            for i in range(se.SE_GetObjectNumberOfCollisions(0)):
                agentName = ctypes.string_at(se.SE_GetObjectName(
                    se.SE_GetObjectCollision(0, i))).decode('utf-8')
                print('Collision between Ego and', agentName)
            break
        for j in range(se.SE_GetNumberOfObjects()):
            se.SE_GetObjectState(se.SE_GetId(j), ctypes.byref(obj_state))
            accerlation = se.SE_GetObjectAcceleration(j)
            # accerlation = obj_state.speed * 3.6
            # print('Acceleration: {:.2f}'.format(accerlation), 'time: {:.2f}'.format(obj_state.timestamp))
            if j == 0:
                ego_acc.append(accerlation)
            else:
                agent_acc.append(accerlation)
            if accerlation < min_acc[j]:
                # print('Acceleration: {:.2f}'.format(accerlation), 'time: {:.2f}'.format(obj_state.timestamp))
                min_acc[j] = accerlation

        if dt < 0.0:
            se.SE_Step()
        else:
            se.SE_StepDT(dt)

    for i in range(se.SE_GetNumberOfObjects()):
        print('Max acceleration for object {} is {:.2f}'.format(i, min_acc[i]))

    # def z_score_normalize(data):
    #     return (data - np.mean(data)) / np.std(data)

    # ego_acc = z_score_normalize(ego_acc)
    # agent_acc = z_score_normalize(agent_acc)
    # remove peak values of ego acceleration and make ego acceleration smooth
    ego_acc = [x for x in ego_acc if x < 10 and x > -10]
    lr = 30
    for i in range(lr, len(ego_acc)-lr):
        ego_acc[i] = sum(ego_acc[i-lr:i+lr+1]) / (2*lr+1)

    # for i in range(lr, len(agent_acc)-lr):
    #     agent_acc[i] = sum(agent_acc[i-lr:i+lr+1]) / (2*lr+1)
    # agent_acc = [x for x in agent_acc if x < 10 and x > -10]

    # visualize ego acceleration
    import matplotlib.pyplot as plt
    plt.plot(ego_acc)
    plt.show()

    # # visualize agent acceleration
    # plt.plot(agent_acc)
    # plt.show()

    return ego_acc, agent_acc


def eval(Acc1, Acc2):
    # 計算 DTW 距離
    distance, path = fastdtw(Acc1, Acc2)
    return distance, path


if __name__ == '__main__':
    se = init()
    OriginalEgoAcc, *OriginalAgentAcc = run(se, 'ori', visualize=True)
    AffectedEgoAcc, *AffectedAgentAcc = run(se, 'eval', visualize=True)
    distance, path = eval(OriginalEgoAcc, AffectedEgoAcc)
    print('DTW distance:', distance)

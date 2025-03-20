# Launch parallel esmini runs as defined by a parameter value distribution
#
# Example:
# python ./scripts/run_distribution.py --osc .\resources\xosc\cut-in.xosc --param_dist .\resources\xosc\cut-in_parameter_set.xosc --fixed_timestep 0.05 --headless


from multiprocessing.pool import ThreadPool
import subprocess
from sys import platform
import sys
import os.path
import evaluate
import ctypes


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

# globals
launched = 0
done = 0
n_runs = 0





def print_status():
    print('Launched: {}/{} Done: {}'.format(launched,
          n_runs, done), end='\r', flush=True)

    # p = subprocess.run(
    #     ['./bin/esmini', '--disable_stdout'] +
    #     list(sys.argv[1:]) + ['--param_permutation'] + [str(index)],
    #     stdout=subprocess.DEVNULL
    # )


se = init_esmini()


def launch_scenario(index):
    global launched
    global done
    launched += 1
    print_status()
    args = list(sys.argv[1:]) + \
        ['--param_permutation'] + [str(index)]
    print("sys.argv[1:]",sys.argv[1:])
    argc = len(args)
    argv = (ctypes.POINTER(ctypes.c_char) * (argc))()
    for i, arg in enumerate(args):
        argv[i] = ctypes.create_string_buffer(arg.encode('utf-8'))
        if arg == '--fixed_timestep':
            dt = float(args[i+1])

    # print(args)
    # print(argc)
    # print(argv) ffmpeg -i out.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" -c:v pam -f image2pipe - | convert -delay 10 - -loop 0 -layers optimize demo2.gif
    "---------------------------------"

    # #　Argument list寫法
    # args = [
    #     # "--window", "2060", "2060", "1600", "800",
    #     '--osc', '/home/hcis-s19/Documents/ChengYu/esmini-demo/resources/xosc/built_from_conf/keeping/01FL-TL_1.xosc',
    #     '--param_dist', '/home/hcis-s19/Documents/ChengYu/esmini-demo/scripts/para_test.xosc',
        
    #     # '--osc', './resources/xosc/cut-in.xosc',
    #     # '--param_dist', './resources/xosc/cut-in_parameter_set.xosc',
    #     # './scripts/para_test.xosc',
    #     # '--fixed_timestep', '0.05'
    #     # '--disable_stdout',
    #     '--headless',
    #     '--param_permutation', str(index),
    #     '--return_nr_permutations',

        
    #     ]

    # dt = 0.05

    # # prepare argument list for ctypes use
    # argc = len(args)
    # argv = (ctypes.POINTER(ctypes.c_char) * (argc))()
    # for i, arg in enumerate(args):
    #     argv[i] = ctypes.create_string_buffer(arg.encode())

    "---------------------------------"

    # init esmini
    if se.SE_InitWithArgs(argc, argv) != 0:
        print('Error initializing esmini')
        exit(-1)

    ego_state = SEScenarioObjectState()
    agent1_state = SEScenarioObjectState()

    ego_acc = []
    agent_acc = []
    ttc_record = []

    agent_list = {}

    if se.SE_GetQuitFlag() == 0:
        for j in range(se.SE_GetNumberOfObjects()):
            agentName =  ctypes.string_at(se.SE_GetObjectName(
                    se.SE_GetId(j))).decode('utf-8')
            agent_list[agentName] = j

    print(agent_list)

    while se.SE_GetQuitFlag() == 0:
        print("In se.SE_GetQuitFlag()")
        if se.SE_GetObjectNumberOfCollisions(0) != 0:
            for i in range(se.SE_GetObjectNumberOfCollisions(0)):
                agentName = ctypes.string_at(se.SE_GetObjectName(
                    se.SE_GetObjectCollision(0, i))).decode('utf-8')
                print('Collision between Ego and', agentName)
            break

        # =====
        current_time = se.SE_GetSimulationTime()

        # Get vehicle positions and speeds
        se.SE_GetObjectState(se.SE_GetId(agent_list['Ego']), ctypes.byref(ego_state))
        se.SE_GetObjectState(se.SE_GetId(agent_list['Agent1']), ctypes.byref(agent1_state))
        ego_pos = [ego_state.x, ego_state.y]
        ego_speed = ego_state.speed
        vehicle_1_pos = [agent1_state.x, agent1_state.y]
        vehicle_1_speed = agent1_state.speed
        # Calculate distance and relative speed
        distance = calculate_distance(ego_pos, vehicle_1_pos)
        relative_speed = abs(ego_speed - vehicle_1_speed)

        # Calculate TTC
        ttc = calculate_ttc(distance, relative_speed)
        ttc_record.append(ttc)
        # print(f"Time: {current_time:.2f}s, TTC: {ttc:.2f}s")





        # for j in range(se.SE_GetNumberOfObjects()):
        #     se.SE_GetObjectState(se.SE_GetId(j), ctypes.byref(obj_state))
            
        #     # print(agentName, end=' ')
        #     # print('Time {:.2f} ObjId {} roadId {} laneId {} s {:.2f} laneOffset {:.2f} s {:.2f} x {:.2f} y {:.2f} heading {:.2f}'.format(
        #     # obj_state.timestamp, obj_state.id, obj_state.roadId, obj_state.laneId, obj_state.s, obj_state.laneOffset,
        #     # obj_state.s, obj_state.x, obj_state.y, obj_state.h))
        #     accerlation = se.SE_GetObjectAcceleration(j)
        #     # accerlation = obj_state.speed * 3.6
        #     # print('Acceleration: {:.2f}'.format(accerlation), 'time: {:.2f}'.format(obj_state.timestamp))
        #     if j == 0:
        #         ego_acc.append(accerlation)
        #     else:
        #         agent_acc.append(accerlation)
        #     # if accerlation < min_acc[j]:
        #     #     # print('Acceleration: {:.2f}'.format(accerlation), 'time: {:.2f}'.format(obj_state.timestamp))
        #     #     min_acc[j] = accerlation

        if dt < 0.0:
            se.SE_Step()
        else:
            se.SE_StepDT(dt)

    "---------------------------------"
    print(f"Time: {current_time:.2f}s, min TTC: {(ttc_record):.2f}s")
    done += 1
    print_status()

    return ttc_record, 



if __name__ == '__main__':
    # print(sys.argv[1:])
    # p = subprocess.run(
    #     ['./bin/esmini', '--disable_stdout'] +
    #     list(sys.argv[1:]) + ['--return_nr_permutations'],
    #     stdout=subprocess.DEVNULL
    # )
    p = subprocess.run(
    [
        './bin/esmini', 
        # '--disable_stdout',
        # "--window", "2060", "2060", "1600", "800",
        '--osc', '/home/hcis-s19/Documents/ChengYu/esmini-demo/resources/xosc/built_from_conf/keeping/01FL-TL_1.xosc',
        '--param_dist', '/home/hcis-s19/Documents/ChengYu/esmini-demo/scripts/para_test.xosc',
        # '--logfile_path',  'logs/01FL-TL_1.txt',
        # '--osc', './resources/xosc/cut-in.xosc',
        # '--param_dist', './resources/xosc/cut-in_parameter_set.xosc',
        '--fixed_timestep', '0.05',
        '--headless',
        # '--param_permutation', str(index),
        '--record','sim.dat',
        ],
        stdout=subprocess.DEVNULL,
        # capture_output=True
    )
    n_runs = p.returncode
    print("total runs: ", n_runs)
    print_status()
    # with ThreadPool() as p:
    #     p. map(launch_scenario, range(n_runs))
    # # run(se, mode, visualize=False, timestep=None):
    # # p.map(evaluate.run(se, 'ori', False, None), range(n_runs))
    # results = p.map(lambda i: evaluate_run_with_args(se, i), range(n_runs))

    min_ttc = [0] * n_runs
    for i in range(n_runs):
        current_ttc = launch_scenario(i)
        min_ttc[i] = min(current_ttc)

    print(min_ttc)
    print("min ttc: ", (min_ttc),
          " at index: ", min_ttc)
    print()

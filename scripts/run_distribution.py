# Launch parallel esmini runs as defined by a parameter value distribution
#
# Example:
# python ./scripts/run_distribution.py --osc .\resources\xosc\cut-in.xosc --param_dist .\resources\xosc\cut-in_parameter_set.xosc --fixed_timestep 0.05 --headless
# python ./scripts/run_distribution.py --osc ./resources/xosc/built_from_conf/0105/01BL-KEEP_02FS-ZZ_1.xosc     --param_dist /home/hcis-s19/Documents/ChengYu/esmini-demo/scripts/para_test.xosc     --logfile_path logs_comb/01BL-KEEP_02FS-ZZ_1.txt     --record dat_comb/01BL-KEEP_02FS-ZZ_1.dat     --fixed_timestep 0.05     --headless

from multiprocessing.pool import ThreadPool
import subprocess
import sys
import os.path


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

# globals
launched = 0
done = 0
n_runs = 0

def print_status():
    print('Launched: {}/{} Done: {}'.format(launched, n_runs, done), end='\r', flush=True)

def launch_scenario(index):
    global launched
    global done
    launched += 1
    print_status()
    p = subprocess.run(
        ['./bin/esmini', '--disable_stdout'] + list(sys.argv[1:]) + ['--param_permutation'] + [str(index)],
        stdout=subprocess.DEVNULL
    )
    done += 1
    print_status()


if __name__ == '__main__':

    osc = os.path.basename(sys.argv[2].split('.')[0])
    record_folder = (os.path.dirname( sys.argv[8]))
    # prio name prefix is in dat folder , then pass
    if any(filename.startswith(f'{osc}_') and filename.endswith('.dat') for filename in os.listdir(record_folder)):
        # print('Scenario dat already exists.')
        exit(0)
    else:
        p = subprocess.run(
            ['./bin/esmini', '--disable_stdout'] + list(sys.argv[1:]) + ['--return_nr_permutations'],
            stdout=subprocess.DEVNULL
        )
        n_runs = p.returncode

        print_status()

        with ThreadPool() as p:
            p.map(launch_scenario, range(n_runs))

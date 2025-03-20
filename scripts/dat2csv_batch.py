import os
import argparse
from dat import DATFile


def convert_dat_to_csv(scenario_name, dat_folder):
    dat_files = [file_name for file_name in os.listdir(dat_folder) if file_name.startswith(f'{scenario_name}_') and file_name.endswith('.dat')]
    if not dat_files:
        print(f"No .dat files found for scenario {scenario_name}")
        return

    for dat_file in dat_files:
        dat_path = os.path.join(dat_folder, dat_file)
        # csv_path = os.path.join(CSV_FOLDER, f"{os.path.splitext(dat_file)[0]}.csv")
        dat = DATFile(dat_path)
        dat.save_csv(extended=True)
        # print(f"Converted {dat_file} to csv")
        dat.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert .dat files to .csv based on scenario name')
    parser.add_argument('--scenario', required=True, help='Scenario name to process')
    parser.add_argument('--dat_folder', required=True, help='Folder containing .dat files')
    args = parser.parse_args()

    scenario_name = args.scenario
    dat_folder = args.dat_folder

    dat_csv = f'{dat_folder}/{scenario_name}_permutation_value.csv'
    if os.path.exists(dat_csv):
        print(f"Dat csv file already exists.")
        exit(0)

    convert_dat_to_csv(args.scenario, args.dat_folder)

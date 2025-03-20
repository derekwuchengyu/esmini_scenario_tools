import os
import random
import argparse
from collections import defaultdict
"""
一次傳全部數量太大，隨機挑部分scenario 上傳
"""
def list_files(directory, extension):
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def group_by_prefix(files):
    groups = defaultdict(list)
    for file in files:
        prefix = file.split('_')[0]
        groups[prefix].append(file)
    return groups

def random_pick(groups, percentage=0.5):
    picked_files = []
    for prefix, files in groups.items():
        pick_count = max(1, int(len(files) * percentage))
        picked_files.extend(random.sample(files, pick_count))
    return picked_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Randomly pick 50% of files grouped by prefix')
    parser.add_argument('--directory', required=True, help='Directory containing the files')
    parser.add_argument('--extension', required=True, help='File extension to filter by')
    parser.add_argument('--percentage', type=float, default=0.5, help='Percentage of files to pick from each group')
    args = parser.parse_args()

    files = list_files(args.directory, args.extension)
    groups = group_by_prefix(files)
    picked_files = random_pick(groups, args.percentage)

    print("Picked files:")
    for file in picked_files:
        print(file)

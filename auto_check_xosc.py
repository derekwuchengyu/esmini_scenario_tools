import os
import random
import subprocess
from collections import defaultdict

# 設定目錄路徑
directory = "/home/hcis-s19/Documents/ChengYu/esmini-demo/resources/xosc/built_from_conf/keeping/"

# 獲取目錄下所有 .xosc 檔案
xosc_files = [f for f in os.listdir(directory) if f.endswith('.xosc')]

# 根據檔名前綴分組
prefix_groups = defaultdict(list)
for file in xosc_files:
    prefix = file.split('_')[0]  # 假設前綴是以 '_' 分隔的第一部分
    prefix_groups[prefix].append(file)

# 從每個前綴組中隨機選擇一個 .xosc 檔案
selected_files = [random.choice(files) for files in prefix_groups.values()]

# 執行每個選擇的 .xosc 檔案
for selected_file in selected_files:
    print(f"================={selected_file}=================")
    command = [
        "./bin/esmini",
        "--window", "2060", "2060", "1920", "1080",
        "--text_scale", "3",
        "--info_text", "1",
        # "--repeat",
        "--disable_controllers",
        "--fixed_timestep", "0.02",
        "--osc", os.path.join(directory, selected_file)
    ]
    subprocess.run(command)
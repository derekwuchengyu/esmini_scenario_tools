esmini_path="/home/hcis-s19/Documents/ChengYu/esmini-demo"
param_dist=$esmini_path"/scripts/para_test.xosc"
test_xosc_folder=$esmini_path"/resources/xosc/built_from_conf/0115" #single scenario
# test_xosc_folder=$esmini_path"/resources/xosc/built_from_conf/0105" #combined scenario


# scenarios="01SR-ZZ_9.xosc"
# scenarios="01BL-KEEP_1.xosc"
# scenarios="01SR-CI_1.xosc"
# scenarios="01BL-KEEP_02FS-ZZ_1.xosc"
# scenarios="01SR-TL_02FR-TL_996.xosc"
scenarios="*.xosc"
# scenarios="01FL-KEEP_9.xosc"
# scenarios="01BR-TR_2.xosc"



log_folder="/media/hcis-s19/DATA/derek/itri/logs"
dat_folder="/media/hcis-s19/DATA/derek/itri/dat"
# log_folder=$esmini_path"/scripts/logs_comb"
# dat_folder=$esmini_path"/scripts/dat_comb"
metrics_folder="/media/hcis-s19/DATA/derek/itri/ttc_result"
# config_folder="/home/hcis-s19/Documents/ChengYu/hcis_scenario_generation/scenario_config"
config_folder="/home/hcis-s19/Documents/ChengYu/hcis_scenario_generation/scenario_config_combined"

# filter='^[^_]+_[^_]+\.xosc$'
filter='^[^_]+_[^_]+_[^_]+\.xosc$'
total_files=$(ls $test_xosc_folder | grep -E $filter | wc -l)
current_file=1

# for file in $(ls $test_xosc_folder | grep -E '^[^_]+_[^_]+_[^_]+\.xosc$'); do
for file in $(ls $test_xosc_folder | grep -E $filter); do
    file="$test_xosc_folder/$file"
    scenario_name=$(basename "$file" .xosc)
    echo "Processing file: $file ($current_file/$total_files)"
    # echo "Processing scenario_name: $scenario_name"
    python scripts/paragen.py --osc "$file" --display_param 0 --config_folder "$config_folder"
    python scripts/run_distribution.py \
        --osc "$file" \
        --param_dist "$param_dist" \
        --logfile_path "${log_folder}/${scenario_name}.txt" \
        --record "${dat_folder}/${scenario_name}.dat" \
        --fixed_timestep 0.1 \
        --headless \
        --disable_controllers \
    && \
    python scripts/log2csv_batch.py \
        --scenario "${scenario_name}" \
        --log_folder "${log_folder}"

    python scripts/dat2csv_batch.py \
        --scenario  "${scenario_name}" \
        --dat_folder "${dat_folder}"

    python scripts/ttc_parallel.py \
        --scenario  "${scenario_name}" \
        --dat_folder "${dat_folder}" \
        --log_folder "${log_folder}" \
        --metrics_folder "${metrics_folder}" \
        --config_folder "${config_folder}"
        
    current_file=$((current_file + 1))
done | tqdm --total $total_files  # >> /dev/null  


    # ./bin/replayer --window 2060 2060 1600 800 --res_path "$test_xosc_folder" --file "${scenario_name}_" --dir "$dat_folder" \
    # --capture_screen

    # ffmpeg -f image2 -framerate 30 -i screen_shot_%5d.tga -c:v libx264 -vf format=yuv420p -crf 20 ttc.mp4 -y && ffmpeg -i ttc.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" -c:v pam -f image2pipe - | convert -delay 10 - -loop 0 -layers optimize "${scenario_name}".gif
    # rm -rf screen_shot_*.tga
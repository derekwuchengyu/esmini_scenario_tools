esmini_path="/home/hcis-s19/Documents/ChengYu/esmini-demo"
param_dist=$esmini_path"/scripts/para_test.xosc"
test_xosc_folder=$esmini_path"/resources/xosc/built_from_conf/0105"


scenarios="*.xosc"
scenarios="01SR-ZZ_9.xosc"
scenarios="01BL-KEEP_1.xosc"
scenarios="01BL-KEEP_02FS-ZZ_1.xosc"
scenarios="*.xosc"


log_folder="/media/hcis-s19/DATA/derek/itri/logs"
dat_folder="/media/hcis-s19/DATA/derek/itri/dat"
# log_folder=$esmini_path"/scripts/logs_comb"
# dat_folder=$esmini_path"/scripts/dat_comb"
metrics_folder="/media/hcis-s19/DATA/derek/itri/ttc_result"
config_folder="/home/hcis-s19/Documents/ChengYu/hcis_scenario_generation/scenario_config_combined"

total_files=$(ls $test_xosc_folder/$scenarios | wc -l)
current_file=0

# for file in $(ls $test_xosc_folder/$scenarios); do
#     scenario_name=$(basename "$file" .xosc)
#     echo "Processing file: $file ($current_file/$total_files)"
#     echo "Processing scenario_name: $scenario_name"
#     python scripts/paragen.py --osc "$file"
#     python scripts/run_distribution.py \
#         --osc "$file" \
#         --param_dist "$param_dist" \
#         --logfile_path "${log_folder}/${scenario_name}.txt" \
#         --record "${dat_folder}/${scenario_name}.dat" \
#         --fixed_timestep 0.05 \
#         --headless
#     python ./scripts/log2csv_batch.py \
#         --scenario "${scenario_name}" \
#         --log_folder "${log_folder}"
#     python ./scripts/dat2csv_batch.py \
#         --scenario  "${scenario_name}" \
#         --dat_folder "${dat_folder}"
#     python scripts/ttc_parallel.py \
#         --scenario  "${scenario_name}" \
#         --dat_folder "${dat_folder}" \
#         --log_folder "${log_folder}" \
#         --metrics_folder "${metrics_folder}" \
#         --config_folder "${config_folder}"
#     current_file=$((current_file + 1))
#     echo $current_file | pv -s $total_files > /dev/null
# done


total_files=$(ls $test_xosc_folder/$scenarios | wc -l)
current_file=0

# Collect all files and feed them to pv for progress tracking
ls $test_xosc_folder/$scenarios | pv -l -s $total_files -N "Processing scenarios" | while read file; do
    scenario_name=$(basename "$file" .xosc)
    # echo "Processing file: $file ($current_file/$total_files)"
    # echo "Processing scenario_name: $scenario_name"
    # python scripts/paragen.py --osc "$test_xosc_folder/$scenarios/$file"
    current_file=$((current_file + 1))
    echo $current_file | pv -s $total_files > /dev/null
done | pv -l -s $total_files -N "Processing scenarios"
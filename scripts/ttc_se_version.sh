param_dist="/home/hcis-s19/Documents/ChengYu/esmini-demo/scripts/para_test.xosc"
test_xosc_folder="/home/hcis-s19/Documents/ChengYu/esmini-demo/resources/xosc/built_from_conf/1231"
scenarios="*.xosc"
# scenarios="01SR-ZZ_9.xosc"
# scenarios="01BL-KEEP_1.xosc"


total_files=$(ls $test_xosc_folder/$scenarios | wc -l)
current_file=0
for file in $test_xosc_folder/$scenarios; do
    current_file=$((current_file + 1))
    scenario_name=$(basename "$file" .xosc)
    echo "Processing file: $file ($current_file/$total_files)"
    echo "Processing scenario_name: $scenario_name"
    python scripts/paragen.py --osc "$file"
    python scripts/ttc.py \
    --osc "$file" \
    --fixed_timestep 0.05 \
    --logfile_path "logs/${scenario_name}.txt" \
    --param_dist "$param_dist" \
    --record dat/${scenario_name}.dat \
    --disable_controllers
done

    # break


# python scripts/ttc.py  \
# --osc /home/hcis-s19/Documents/ChengYu/esmini-demo/resources/xosc/built_from_conf/1227/01FL-TL_1.xosc \
# --param_dist /home/hcis-s19/Documents/ChengYu/esmini-demo/scripts/para_test.xosc \
# --fixed_timestep 0.05 \
# --logfile_path logs/my_scenario.txt \
# --record dat/sim.dat \
# --disable_controllers \
# # --log_level debug \
# # --headless

# ./bin/replayer --window 2060 2060 1600 800 --res_path /home/hcis-s19/Documents/ChengYu/esmini-demo/resources/xosc/ --file sim_ --dir ./dat/ 

#--capture_screen

# ffmpeg -f image2 -framerate 30 -i screen_shot_%5d.tga -c:v libx264 -vf format=yuv420p -crf 20 ttc.mp4 -y && ffmpeg -i ttc.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" -c:v pam -f image2pipe - | convert -delay 10 - -loop 0 -layers optimize ttc.gif

# python scripts/run_distribution.py  \
# --osc .\resources\xosc\cut-in.xosc \
# --param_dist .\resources\xosc\cut-in_parameter_set.xosc \
# --fixed_timestep 0.05 \
# --headless \

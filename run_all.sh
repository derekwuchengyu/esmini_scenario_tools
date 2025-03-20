#!/bin/bash

# Directory containing the .xosc files
SCENARIO_DIR="./resources/xosc/built_from_conf"

# Command to run each scenario
COMMAND="./bin/esmini --window 60 60 1920 1080 --text_scale 3 --info_text 3 --osc"

# Loop through each .xosc file in the directory
for scenario in "$SCENARIO_DIR"/*.xosc; 
do
    echo "Running scenario: $scenario"
    $COMMAND "$scenario"

    # Prompt the user to continue or stop
    read -p "Press [Enter] to continue to the next scenario or type 'stop' to cancel: " user_input
    if [ "$user_input" == "stop" ]; then
        echo "Execution stopped by user."
        break
    fi
done

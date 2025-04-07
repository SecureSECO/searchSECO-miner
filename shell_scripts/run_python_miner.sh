#!/bin/bash

# Activate the Conda environment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate rnd

while true; do
    echo "Starting auto_miner.py with 10-minute timeout..."

    start_time=$(date +%s)

    # Run the script with a 10-minute timeout
    timeout 600 python ../auto_miner.py N 1
    exit_code=$?  # Capture exit status IMMEDIATELY after timeout

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo "Process took around $duration seconds to complete."

    sleep_time=$((duration / 10))
    # Ensure minimum sleep time of at least 1 second to avoid 0
    if [ $sleep_time -lt 1 ]; then
        sleep_time=1
    fi

    if [ $exit_code -eq 124 ]; then
        echo "Process timed out after 10 minutes and was terminated."
    else
        echo "Process completed within time limit."
    fi

    echo "Restarting in $sleep_time seconds..."
    sleep $sleep_time
done

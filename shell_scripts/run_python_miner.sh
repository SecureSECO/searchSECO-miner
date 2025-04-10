#!/bin/bash

# Activate the Conda environment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate rnd

TEMP_DIR="../.tmp"
elapsed_time=0  # Tracks total runtime in seconds

while true; do
    echo "Starting auto_miner.py with 10-minute timeout..."

    start_time=$(date +%s)

    # Run the script with a 10-minute timeout (600 seconds)
    timeout 600 python ../auto_miner.py N 1
    exit_code=$?

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    elapsed_time=$((elapsed_time + duration))

    echo "Process took around $duration seconds to complete."

    sleep_time=$((duration / 10))
    # Ensure minimum sleep time of at least 1 second
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

    # Check if 3 hours (10800 seconds) have passed
    if [ $elapsed_time -ge 10800 ]; then
        echo "3 hours reached. Sleeping for 5 minutes and cleaning temp directory..."
        sleep 300  # Sleep for 5 minutes

        # Delete all files in TEMP_DIR
        if [ -d "$TEMP_DIR" ]; then
            rm -rf "$TEMP_DIR"/* || echo "Some files couldn't be deleted."
            echo "Deleted files in $TEMP_DIR"
        else
            echo "Temp directory $TEMP_DIR does not exist."
        fi

        # Reset elapsed time counter
        elapsed_time=0
    fi
done

#!/bin/bash

# Activate the Conda environment
# Check which conda.sh exists and source it
if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
elif [ -f "/root/miniconda3/etc/profile.d/conda.sh" ]; then
    source "/root/miniconda3/etc/profile.d/conda.sh"
else
    echo "No conda.sh found. Please install Conda."
    exit 1
fi


TEMP_DIR="../.tmp"
elapsed_time=0  # Tracks total runtime in seconds

timeout_sec=1200
timeout_min=$((timeout_sec / 60))

while true; do
    echo "Starting searchseco_batch_miner.py with $timeout_min-minute timeout..."

    start_time=$(date +%s)

    # Run the script with a timeout
    timeout "${timeout_sec}" python ../searchseco_batch_miner.py 1
    
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
        echo "Process timed out after $timeout_min minutes and was terminated."
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

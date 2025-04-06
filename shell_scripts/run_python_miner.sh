#!/bin/bash

# Activate the Conda environment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate rnd

while true; do
    echo "Starting auto_miner.py with 15-minute timeout..."
    
    # Run the script with a 60-minute timeout
    timeout 3600 python ../auto_miner.py N 20

    if [ $? -eq 124 ]; then
        echo "Process timed out after 60 minutes and was terminated."
    else
        echo "Process completed within time limit."
    fi

    echo "Restarting in 60 seconds..."
    sleep 60
done
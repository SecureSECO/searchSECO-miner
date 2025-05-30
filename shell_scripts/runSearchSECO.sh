#!/bin/bash

trap "echo '$(date '+%Y-%m-%d %H:%M:%S') - Script interrupted. Exiting...'; exit 1" SIGINT SIGTERM
TIMEOUT=1800           # 20 minutes
SLEEP_DIVISOR=10
MAX_ELAPSED=10800      # 3 hours
COOLDOWN=300           # 5 minutes
TEMP_DIR="../.tmp"
elapsed_time=0  # Tracks total runtime in seconds

# Load NVM and use Node.js version 18
export NVM_DIR="$HOME/.nvm"
# Load NVM if not already loaded
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" || {
    echo "NVM not found. Please ensure NVM is installed and set up correctly."
    exit 1
}
nvm use 18 || {
    echo "Failed to switch to Node.js version 18. Please ensure Node.js v18 is installed via NVM."
    exit 1
}


while true; do
    {
    echo "--------------------------------------------------"

    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting SearchSECOminer with 20-minute timeout..."

    start_time=$(date +%s)

    # Run the script with a 20-minute timeout
    timeout $TIMEOUT bash -c "cd ../src && npm run execute -- start -V 5"
    exit_code=$?

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    elapsed_time=$((elapsed_time + duration))

    echo "Process took around $duration seconds to complete."

    sleep_time=$((duration / $SLEEP_DIVISOR))
    # Ensure minimum sleep time of at least 1 second
    if [ $sleep_time -lt 1 ]; then
        sleep_time=1
    fi

    if [ $exit_code -eq 124 ]; then
        echo "Process timed out after 20 minutes and was terminated."
    else
        echo "Process completed within time limit."
    fi

    echo "Restarting in $sleep_time seconds..."
    sleep $sleep_time

    # Check if 3 hours (10800 seconds) have passed
    if [ $elapsed_time -ge $MAX_ELAPSED ]; then
        echo "3 hours reached. Sleeping for 5 minutes and cleaning temp directory..."
        sleep $COOLDOWN  # Sleep for 5 minutes

        if [[ -d "$TEMP_DIR" && "$TEMP_DIR" != "/" && -n "$TEMP_DIR" ]]; then
            find "$TEMP_DIR" -mindepth 1 -delete || echo "Some files couldn't be deleted."
            echo "Deleted files in $TEMP_DIR"
        else
            echo "Temp directory $TEMP_DIR is invalid or does not exist."
        fi

        # Reset elapsed time counter
        elapsed_time=0
    fi
    } > searchsecominer.log 2>&1
done

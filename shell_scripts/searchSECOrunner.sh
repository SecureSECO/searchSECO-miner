#!/bin/bash

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

# Directory to save logs
LOG_DIR="/home/mislam/searchSECO-miner/logs"
mkdir -p "$LOG_DIR" # Ensure the directory exists

# Array of unique log file prefixes
declare -a PREFIXES=("log_file_1" "log_file_2")

# Function to start and restart a program
start_program() {
  local prefix=$1

  while true; do
    # Generate a unique log file name with a timestamp
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    LOG_FILE="${LOG_DIR}/${prefix}_${TIMESTAMP}.log"

    echo "Starting application with prefix $prefix... Logs will be stored in $LOG_FILE"

    # Run the application
    nohup npm run execute -- start -V 5 > "$LOG_FILE" 2>&1 &

    # Get PID of the process to monitor
    PID=$!
    echo "Started application (PID: $PID) with prefix $prefix."

    # Wait for the application to exit
    wait $PID

    echo "Application with prefix $prefix stopped. Restarting..."
    sleep 120 # Optional: delay before restarting
    
    ##### Remove Directory from .tmp ######
    TMP_DIR="/home/mislam/searchSECO-miner/.tmp"

    # Navigate to the directory
    cd "$TMP_DIR" || exit

    # Get the list of files sorted by modification time (newest first) and skip the first 6
    FILES_TO_REMOVE=$(ls -t | tail -n +7)

    # Remove the older files
    for FILE in $FILES_TO_REMOVE; do
        rm -rf "$FILE"
    done

    echo "Removed files, keeping only the latest 6 in $TMP_DIR"
    sleep 300

  done
}

# Start each program in the background
for prefix in "${PREFIXES[@]}"; do
  start_program "$prefix" &
done

# Wait for all background processes to complete
wait
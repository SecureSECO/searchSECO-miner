#!/bin/bash

# Directories and script path
LOG_DIR="/home/mislam/searchSECO-miner/logs"
TEMP_DIR="/home/mislam/searchSECO-miner/.tmp"
SCRIPT="searchSECOrunner.sh"
CMD="npm run execute -- start -V 5"
MAX_PROCESSES=8

# Ensure the log directory exists
mkdir -p "$LOG_DIR"

# Infinite loop to monitor the directories
while true; do
    # Check if the temp directory exists and is not empty
    if [ -d "$TEMP_DIR" ] && [ "$(ls -A "$TEMP_DIR")" ]; then
        echo "Temp directory exists and is not empty. Checking latest file modification time..."

        # Find the latest modified file in the temp directory
        LATEST_FILE=$(find "$TEMP_DIR" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2)

        # Find the latest modified file in the log directory
        LATEST_LOG_FILE=$(find "$LOG_DIR" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2)

        if [ -n "$LATEST_FILE" ]; then
            # Get the last modification time of the latest temp file
            LAST_MODIFIED_TIME=$(stat -c %Y "$LATEST_FILE")
            CURRENT_TIME=$(date +%s)
            TIME_DIFF=$((CURRENT_TIME - LAST_MODIFIED_TIME))

            if [ -n "$LATEST_LOG_FILE" ]; then
                # Get the last modification time of the latest log file
                LAST_MODIFIED_TIME_LOG=$(stat -c %Y "$LATEST_LOG_FILE")
                CURRENT_TIME_LOG=$(date +%s)
                TIME_DIFF_LOG=$((CURRENT_TIME_LOG - LAST_MODIFIED_TIME_LOG))
            else
                # No log files found, treat as needing restart
                TIME_DIFF_LOG=999999
            fi

            # Check if conditions are met to restart
            if [ $TIME_DIFF -gt 1800 ] || [ $TIME_DIFF_LOG -gt 600 ]; then
                # Check current process count for the specific command
                PROCESS_COUNT=$(pgrep -f "$CMD" | wc -l)

                if [ "$PROCESS_COUNT" -lt $MAX_PROCESSES ]; then
                    echo "Conditions met to restart, and process count is below maximum ($MAX_PROCESSES)."

                    if [ $TIME_DIFF -gt 1800 ]; then
                        echo "Latest temp file modified > 30 minutes ago."
                    fi
                    if [ $TIME_DIFF_LOG -gt 600 ]; then
                        echo "Latest log file modified > 10 minutes ago."
                    fi

                    # Stop the running processes matching the command
                    pkill -f "$CMD" || echo "No running instance of '$CMD' found."

                    # Generate a unique log file name
                    UNIQUE_LOG_FILE="$LOG_DIR/restart_$(date +'%Y%m%d_%H%M%S').log"

                    # Restart the command with unique log file
                    nohup $CMD > "$UNIQUE_LOG_FILE" 2>&1 &

                    echo "Commands executed successfully. Logs are written to $UNIQUE_LOG_FILE."
                else
                    echo "Maximum process limit ($MAX_PROCESSES) reached. No new processes will be started."
                fi
            else
                echo "Temp and log files are recent. No action required."
            fi
        else
            echo "No files found in $TEMP_DIR, skipping modification time check."
        fi
    else
        echo "Temp directory is empty or does not exist."

        # Check if the log directory does not exist
        if ! [ -d "$LOG_DIR" ]; then
            echo "Log directory does not exist. Restarting the script..."

            # Stop the running processes matching the command
            pkill -f "$CMD" || echo "No running instance of '$CMD' found."

            # Generate a unique log file name
            UNIQUE_LOG_FILE="$LOG_DIR/restart_$(date +'%Y%m%d_%H%M%S').log"

            # Restart the command with unique log file
            nohup $CMD > "$UNIQUE_LOG_FILE" 2>&1 &

            echo "Commands executed successfully. Logs are written to $UNIQUE_LOG_FILE."
        else
            echo "Log directory exists. No action required."
        fi
    fi

    # Sleep for 5 minutes (300 seconds) before checking again
    sleep 300
done

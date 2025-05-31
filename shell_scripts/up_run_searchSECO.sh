#!/bin/bash

trap "echo '$(date '+%Y-%m-%d %H:%M:%S') - Script interrupted. Exiting...'; exit 1" SIGINT SIGTERM
TIMEOUT=9000
SLEEP_DIVISOR=10
MAX_ELAPSED=10800
COOLDOWN=900
TEMP_DIR="../.tmp"
LOGFILE="searchsecominer.log"
elapsed_time=0

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" || {
    echo "NVM not found. Please ensure NVM is installed and set up correctly."
    exit 1
}
nvm use 18 || {
    echo "Failed to switch to Node.js version 18."
    exit 1
}

while true; do
    echo "--------------------------------------------------" | tee "$LOGFILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting SearchSECOminer..." | tee -a "$LOGFILE"

    start_time=$(date +%s)

    # Start the process in background
    (
        cd ../src && npm run execute -- start -V 5
    ) >> "$LOGFILE" 2>&1 &
    pid=$!

    # Monitor the log file for changes
    log_timeout=1200  # 20 minutes
    last_mod=$(stat -c %Y "$LOGFILE")

    while kill -0 $pid 2>/dev/null; do
        sleep 100
        current_time=$(date +%s)
        current_mod=$(stat -c %Y "$LOGFILE")

        if (( current_mod > last_mod )); then
            last_mod=$current_mod
        fi

        if (( current_time - last_mod > log_timeout )); then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - No log update in 20 minutes. Terminating process..." | tee -a "$LOGFILE"
            kill $pid 2>/dev/null
            wait $pid
            exit_code=124
            break
        fi
    done

    if [[ -z "$exit_code" ]]; then
        wait $pid
        exit_code=$?
    fi

    end_time=$(date +%s)
    duration=$((end_time - start_time))
    elapsed_time=$((elapsed_time + duration))

    echo "Process took around $duration seconds to complete." | tee -a "$LOGFILE"

    sleep_time=$((duration / SLEEP_DIVISOR))
    (( sleep_time < 1 )) && sleep_time=1

    if [ $exit_code -eq 124 ]; then
        echo "Process timed out or was killed due to inactivity." | tee -a "$LOGFILE"
    else
        echo "Process completed within time limit." | tee -a "$LOGFILE"
    fi

    echo "Restarting in $sleep_time seconds..." | tee -a "$LOGFILE"
    sleep $sleep_time

    if (( elapsed_time >= MAX_ELAPSED )); then
        echo "3 hours reached. Sleeping 5 minutes and cleaning temp directory..." | tee -a "$LOGFILE"
        sleep $COOLDOWN
        if [[ -d "$TEMP_DIR" && "$TEMP_DIR" != "/" && -n "$TEMP_DIR" ]]; then
            find "$TEMP_DIR" -mindepth 1 -delete || echo "Some files couldn't be deleted." | tee -a "$LOGFILE"
            echo "Deleted files in $TEMP_DIR" | tee -a "$LOGFILE"
        else
            echo "Temp directory $TEMP_DIR is invalid or does not exist." | tee -a "$LOGFILE"
        fi
        elapsed_time=0
    fi
done

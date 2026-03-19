#!/bin/bash

#############################################
# DATABASE CONFIG
#############################################

DB_NAME=pg_database
DB_USER=postgres
DB_HOST=localhost
DB_PORT=5432
GITHUB_TOKEN=
DB_PASSWORD=
export PGPASSWORD=$DB_PASSWORD
#ENV_FILE="../python_script/.env"

#if [ ! -f "$ENV_FILE" ]; then
#    echo ".env file not found at $ENV_FILE!"
#    exit 1
#fi

# Load .env variables
#export $(grep -v '^#' "$ENV_FILE" | xargs)

#############################################
# MINER CONFIG
#############################################

TEMP_DIR="../.tmp"
timeout_sec=3600
timeout_min=$((timeout_sec / 60))
elapsed_time=0

PER_PAGE=100   # max per GitHub API
LANGUAGES=("C" "C++" "C#" "Java" "JavaScript" "Python")

#############################################
# GITHUB TOKEN
#############################################

if [ -z "$GITHUB_TOKEN" ]; then
    echo "No GitHub token detected (60 requests/hr limit)"
    AUTH_HEADER=""
else
    echo "Using GitHub token"
    AUTH_HEADER="Authorization: token $GITHUB_TOKEN"
fi

#############################################
# INIT DATABASE & TABLE
#############################################

init_db() {
    # Create database if not exists
    DB_EXISTS=$(psql -U $DB_USER -h $DB_HOST -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")
    if [ "$DB_EXISTS" != "1" ]; then
        echo "Database $DB_NAME does not exist. Creating..."
        createdb -U $DB_USER -h $DB_HOST $DB_NAME
    fi

    # Create table if not exists
    psql -U $DB_USER -h $DB_HOST -d $DB_NAME -c "
    CREATE TABLE IF NOT EXISTS repositories (
        repo_url TEXT PRIMARY KEY,
        language TEXT,
        processed BOOLEAN DEFAULT FALSE,
        processed_at TIMESTAMP
    );"
}

#############################################
# FETCH REPOS FROM GITHUB
#############################################

fetch_repos() {

    echo "Fetching repositories from GitHub..."

    for lang in "${LANGUAGES[@]}"; do

        echo "Collecting $lang repositories..."

        curl -s -H "$AUTH_HEADER" \
        "https://api.github.com/search/repositories?q=language:${lang}+stars:>100&sort=stars&order=desc&per_page=${PER_PAGE}" \
        | grep -oP '"html_url": "\K(https://github.com/[^"]+)' \
        | while read repo; do

            # Insert only new records
            psql -U $DB_USER -h $DB_HOST -d $DB_NAME -p $DB_PORT \
            -c "INSERT INTO repositories(repo_url, language)
                VALUES ('$repo','$lang')
                ON CONFLICT (repo_url) DO NOTHING;" >/dev/null

        done

    done

}

#############################################
# GET NEXT REPOSITORY
#############################################

get_next_repo() {

    repo=$(psql -U $DB_USER -h $DB_HOST -d $DB_NAME -t -A -c "
    SELECT repo_url
    FROM repositories
    WHERE processed=false
    LIMIT 1
    FOR UPDATE SKIP LOCKED;
    ")

    echo $repo
}

#############################################
# MARK REPO AS PROCESSED
#############################################

mark_processed() {

    repo=$1

    psql -U $DB_USER -h $DB_HOST -d $DB_NAME -p $DB_PORT \
    -c "UPDATE repositories
        SET processed=true,
            processed_at=NOW()
        WHERE repo_url='$repo';" >/dev/null

}

#############################################
# CLEAN TEMP DIRECTORY
#############################################

clean_tmp() {

    echo "Cleaning temp directory..."

    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"/* || echo "Some files couldn't be deleted."
        echo "Deleted files in $TEMP_DIR"
    fi

}

#############################################
# RUN SEARCHSECO
#############################################

run_repo() {

    repo=$1

    echo "Running SearchSECO on $repo"

    start_time=$(date +%s)

    timeout "${timeout_sec}" npm run execute -- checkupload "$repo" -V 5

    exit_code=$?

    end_time=$(date +%s)

    duration=$((end_time - start_time))
    elapsed_time=$((elapsed_time + duration))

    echo "Process took $duration seconds."

    sleep_time=$((duration / 10))
    [ $sleep_time -lt 1 ] && sleep_time=1

    if [ $exit_code -eq 124 ]; then
        echo "Process timed out after $timeout_min minutes."
    else
        echo "Process completed."
    fi

    sleep $sleep_time

}

#############################################
# MAIN
#############################################

init_db       # Ensure DB & table exist

while true; do

    repo_count=$(psql -U $DB_USER -h $DB_HOST -d $DB_NAME -t -A -c "SELECT COUNT(*) FROM repositories;")

    if [ "$repo_count" -lt 100000 ]; then
        fetch_repos
    fi

    repo=$(get_next_repo)

    if [ -z "$repo" ]; then
        echo "No unprocessed repositories available. Sleeping..."
        sleep 60
        continue
    fi

    run_repo "$repo"

    mark_processed "$repo"

    if [ $elapsed_time -ge 10800 ]; then
        echo "3 hours reached. Sleeping 5 minutes..."
        sleep 300
        clean_tmp
        elapsed_time=0
    fi

done

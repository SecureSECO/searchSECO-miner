import os
import glob
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values

def get_db_conn():

    # Database connection details
    DB_NAME = "github_repos"
    DB_USER = "postgres"
    DB_PASSWORD = "Sphings@19"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    return conn

def update_searchrepos(input_project_id, input_project_version, repo_id):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE searchrepos SET is_active = %s, project_id = %s,  project_version = %s WHERE _id = %s;", (False, input_project_id, input_project_version, repo_id))
    conn.commit()
    cur.close()
    conn.close()

def get_search_repos(search_repo):
    conn = get_db_conn()
    cur = conn.cursor()

    if search_repo and search_repo.isdigit():
        cur.execute("SELECT _id, repository_url, license, language, licenseconflicts, is_active FROM searchrepos WHERE is_active=True LIMIT %s;", (int(search_repo),))
    else:
        #print("search_repo: ", search_repo)
        # Run for a particular repository for unit testing
        # 'https://github.com/microsoft/cocos2d-x'
        cur.execute("UPDATE searchrepos SET is_active = %s WHERE repository_url = %s;", (True, search_repo))
        if cur.rowcount == 0:
            # If no rows were updated, insert a new record
           cur.execute("""
                INSERT INTO searchrepos (
                    _id, organization, project_id, repository_url, license, language, licenseConflicts, is_active
                ) VALUES (
                    TO_CHAR(NOW(), 'YYYYMMDDHH24MISSUS'),  -- Unique timestamp-based ID
                    'alibaba',  -- Organization
                    '',  -- project_id (Empty)
                    %s,  -- repository_url
                    NULL,  -- License (Unknown)
                    NULL,  -- Language (Unknown)
                    0,  -- licenseConflicts (Default)
                    %s  -- is_active (Default)
                );
            """, (search_repo, True))
        cur.execute("SELECT _id, repository_url, license, language, licenseconflicts, is_active, project_id FROM searchrepos WHERE repository_url = %s;", (search_repo,))

    repos = cur.fetchall()
    cur.close()
    conn.close()
    return repos

def insert_into_rp_data(df):
    try:
        # Connect to PostgreSQL
        conn = get_db_conn()

        cur = conn.cursor()

        # Rename CSV columns to match the database
        df.rename(columns={
            'Hash': 'hash',
            'Project ID': 'project_id',
            'Version': 'version',
            'License': 'license',
            'Method Name': 'method_name',
            'File Location': 'file_location',
            'Function Code': 'function_code',
            'Repository URL': 'repository_url',
            'Query Project': 'query_project',
            'Violation': 'violation',
            'Source_project': 'source_project',
            'Source_project_version':'source_project_version'
        }, inplace=True)

        df = df[df['query_project'].str.len() <= 5]
        # Remove duplicates based on (hash, project_id)
        df.drop_duplicates(subset=['hash', 'project_id', 'version'], inplace=True)

        # Generate unique ID by combining hash and project_id
        df['_id'] = df['hash'].astype(str) + "_" + df['project_id'].astype(str)

        # Convert DataFrame to a list of tuples for batch insert
        records_to_insert = [
            (
                row['_id'], row['hash'], row['project_id'], row['version'], row['license'], row['method_name'],
                row['file_location'], row['function_code'], row['repository_url'], row['query_project'], row['violation'],
                row['source_project'], row['source_project_version']
            ) for _, row in df.iterrows()
        ]

        # Insert all records in bulk
        insert_query = """
        INSERT INTO repository_data (
            _id, hash, project_id, version, license, method_name,
            file_location, function_code, repository_url, query_project, violation, source_project, source_project_version
        ) VALUES %s
        ON CONFLICT (hash, project_id, version) DO NOTHING;
        """
        
        execute_values(cur, insert_query, records_to_insert)

        # Commit changes
        conn.commit()
        print(f"Inserted {len(records_to_insert)} new records successfully.")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close connection
        if conn:
            cur.close()
            conn.close()
    return df


"""
CREATE DATABASE github_repos;

CREATE TABLE repo_collection (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50),
    organization TEXT,
    html_url TEXT,
    fork BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    pushed_at TIMESTAMP,
    git_url TEXT,
    size INT,
    stargazers_count INT,
    watchers_count INT,
    language TEXT,
    forks_count INT,
    archived BOOLEAN,
    disabled BOOLEAN,
    open_issues_count INT,
    license TEXT NULL, -- Some values are empty, so allow NULL
    allow_forking BOOLEAN
);

CREATE TABLE searchrepos (
    _id VARCHAR(50) PRIMARY KEY,
    organization VARCHAR(50),
    project_id VARCHAR(100),
    project_version VARCHAR(100),
    repository_url TEXT,
    license TEXT,
    language TEXT,
    licenseConflicts INT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE repository_data (
    _id VARCHAR(100) PRIMARY KEY,
    hash TEXT NOT NULL,
    project_id VARCHAR(50),
    version TEXT,
    license TEXT,
    method_name TEXT,
    file_location TEXT,
    function_code TEXT,
    repository_url TEXT,
    query_project TEXT,
    violation TEXT, 
    source_project TEXT, 
    source_project_version TEXT,
    UNIQUE (hash, project_id, version)
);

DROP TABLE repository_data;


######## Support queries #######

UPDATE repositories SET is_active = TRUE WHERE is_active = FALSE;

ALTER TABLE repositories ADD COLUMN project_id VARCHAR(50);

SELECT COUNT(*) 
FROM repository_data 
WHERE violation ILIKE '%incompatible%';

SELECT COUNT(DISTINCT project_id) 
FROM repository_data
WHERE query_project = 'Yes' AND violation ILIKE '%incompatible%';

INSERT INTO searchrepos (_id, organization, project_id, repository_url, license, language, licenseConflicts, is_active) VALUES (
    TO_CHAR(NOW(), 'YYYYMMDDHH24MISSUS'),  -- Unique timestamp-based ID
    'alibaba',  -- Organization
    '',  -- project_id (Empty)
    'https://github.com/shibingli/webconsole',
    NULL,  -- License (Unknown)
    NULL,  -- Language (Unknown)
    0,  -- licenseConflicts (Default)
    TRUE  -- is_active (Default)
)

DELETE FROM searchrepos 
WHERE organization = 'alibaba' 
AND repository_url = 'https://github.com/alibaba/arthas';

DELETE FROM searchrepos 
WHERE epository_url = 'https://github.com/microsoft/simple-filter-mixer';

SELECT * 
FROM repository_data 
WHERE hash IN (
    SELECT DISTINCT hash 
    FROM repository_data 
    WHERE project_id = '2416460407' 
    AND violation ILIKE '%incompatible%'
) 
ORDER BY hash, version;

#Commands

sudo -u postgres psql
\c github_repos;
\l
# Check other sources for linces
- keep a note even if not violated license

### Vilation examples ###

1. https://github.com/alibaba/arthas
2. https://github.com/shibingli/webconsole

"""
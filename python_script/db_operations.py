import psycopg2
import csv

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
    violation TEXT
);

DROP TABLE repository_data;

UPDATE repositories SET is_active = TRUE WHERE is_active = FALSE;

ALTER TABLE repositories ADD COLUMN project_id VARCHAR(50);

SELECT COUNT(*) 
FROM repository_data 
WHERE violation ILIKE '%incompatible%';

SELECT COUNT(DISTINCT project_id) 
FROM repository_data
WHERE query_project = 'Yes' AND violation ILIKE '%incompatible%';

INSERT INTO searchrepos (
    _id, organization, project_id, repository_url, license, language, 
    licenseConflicts, is_active
) VALUES (
    TO_CHAR(NOW(), 'YYYYMMDDHH24MISSUS'),  -- Unique timestamp-based ID
    'alibaba',  -- Organization
    '',  -- project_id (Empty)
    'https://github.com/alibaba/arthas',  -- Repository URL
    NULL,  -- License (Unknown)
    NULL,  -- Language (Unknown)
    0,  -- licenseConflicts (Default)
    TRUE  -- is_active (Default)
);

DELETE FROM searchrepos 
WHERE organization = 'alibaba' 
AND repository_url = 'https://github.com/alibaba/arthas/';

#Commands

sudo -u postgres psql
\c github_repos;
\l
# Check other sources for linces
- keep a note even if not violated license

"""

# Get repository links from a csv file

try:
    CSV_FILE_PATH = "../input_files/match_repo_links.csv"
    cur = conn.cursor()

    # Open the CSV file
    with open(CSV_FILE_PATH, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row

            for row in reader:
                _id, link, license, language, licenseconflicts = row
                licenseconflicts = int(licenseconflicts)  # Convert to integer
                is_active = True # Convert to boolean

                # Check if the repository already exists
                cur.execute("SELECT COUNT(*) FROM repositories WHERE _id = %s;", (_id,))
                exists = cur.fetchone()[0]

                if exists:
                    print(f"Skipping {_id}: Already exists in the database.")
                else:
                    # Insert new record
                    cur.execute("""
                        INSERT INTO repositories (_id, link, license, language, licenseconflicts, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """, (_id, link, license, language, licenseconflicts, is_active))
                    print(f"Inserted {_id} into the database.")

    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()
    print("CSV data imported successfully!")

except Exception as e:
    print("Error:", e)
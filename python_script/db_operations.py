import psycopg2

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
    UNIQUE (hash, project_id, version)
);

ALTER TABLE repository_data 
ADD CONSTRAINT unique_hash_project_version UNIQUE (hash, project_id, version);

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
AND repository_url = 'https://github.com/alibaba/arthas/';

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
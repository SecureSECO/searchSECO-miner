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
    same_license INT,
    dif_license_comply INT,
    license_conflicts INT,
    high_risks INT,
    undetermined INT,
    no_match INT,
    has_picked BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    processing_start_time TIMESTAMP,
    processing_end_time TIMESTAMP,
    project_type INT DEFAULT 0
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
    relational_id VARCHAR(50),
    
    -- Correct UNIQUE constraint to match ON CONFLICT
    UNIQUE (hash, project_id, version),
    
    -- Keep the foreign key constraint
    FOREIGN KEY (relational_id) REFERENCES searchrepos(_id) ON DELETE CASCADE
);


##### Stats on Undefined license #####

## Count Number of Projects Undefined license

WITH first_per_hash AS (
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY hash ORDER BY _id) AS rn
        FROM repository_data
    ) sub
    WHERE rn = 1
)
SELECT COUNT(*) AS unique_count
FROM (
    SELECT DISTINCT project_id, version
    FROM first_per_hash
    WHERE license IN ('Other', '-', 'other', '')
) AS filtered_unique;


## Count Number of Hit for the Projects with Undefined license

 WITH first_per_hash AS (
    SELECT *
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY hash ORDER BY _id) AS rn
        FROM repository_data
    ) sub
    WHERE rn = 1
)
SELECT COUNT(*) AS total_first_per_hash
FROM first_per_hash;
 total_first_per_hash 

######## Support queries #######

UPDATE searchrepos SET is_active = TRUE WHERE is_active = FALSE;

UPDATE searchrepos SET is_active = FALSE WHERE repository_url = 'https://github.com/microsoft/Pyjion';

SELECT COUNT(*) FROM searchrepos WHERE is_active = FALSE;

SELECT COUNT(*) 
FROM repository_data 
WHERE violation ILIKE '%incompatible%';

SELECT COUNT(DISTINCT project_id) 
FROM repository_data
WHERE query_project = 'Yes' AND violation ILIKE '%incompatible%';

DELETE FROM searchrepos 
WHERE repository_url = 'https://github.com/microsoft/simple-filter-mixer';

SELECT * 
FROM repository_data 
WHERE hash IN (
    SELECT DISTINCT hash 
    FROM repository_data 
    WHERE project_id = '2416460407' 
    AND violation ILIKE '%incompatible%'
) 
ORDER BY hash, version;

DROP TABLE repository_data;

#Commands

sudo -u postgres psql
\c github_repos;
\l


### Replication  Package Data pulling ###

\copy (SELECT * FROM repository_data LIMIT 10) TO '/tmp/validation_mined_data.csv' WITH CSV HEADER;

sudo mv /tmp/valication_mined_data.csv /datadisk/SearchSECOminer/searchSECO-miner/data_files/

"""
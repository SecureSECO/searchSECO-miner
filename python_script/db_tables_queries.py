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
    has_picked BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    processing_start_time TIMESTAMP,
    processing_end_time TIMESTAMP
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

UPDATE searchrepos SET is_active = TRUE WHERE is_active = FALSE;

UPDATE searchrepos SET is_active = FALSE WHERE repository_url = 'https://github.com/microsoft/Pyjion';

SELECT COUNT(*) FROM searchrepos WHERE is_active = FALSE;

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

### Violation examples ###

1. https://github.com/alibaba/arthas
2. https://github.com/shibingli/webconsole


Next:
- update searchrepos with the number of conflicts
- update searchrepos with the processing start and end time
- number of match found/not -1/conflict
- keep a note even if not violated license

"""
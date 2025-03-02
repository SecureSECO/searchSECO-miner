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

CREATE TABLE repositories (
    _id VARCHAR(50) PRIMARY KEY,
    link TEXT,
    license TEXT,
    language TEXT,
    licenseConflicts INT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE repository_data (
    _id VARCHAR(100) PRIMARY KEY,
    hash TEXT NOT NULL,
    project_id BIGINT NOT NULL,
    version BIGINT NOT NULL,
    license TEXT,
    method_name TEXT,
    file_location TEXT,
    function_code TEXT,
    repository_url TEXT,
    query_project TEXT,
    violation TEXT
);

UPDATE repositories SET is_active = TRUE WHERE is_active = FALSE;

ALTER TABLE repositories ADD COLUMN project_id VARCHAR(50);

#Commands

sudo -u postgres psql
\c github_repos;
\l


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
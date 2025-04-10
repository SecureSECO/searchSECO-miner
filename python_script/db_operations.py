import os
import glob
import psycopg2
import pandas as pd
import datetime
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

def update_searchrepos(input_project_id, input_project_version, repo_id, incompatibility_count):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("UPDATE searchrepos SET is_active = %s, project_id = %s,  project_version = %s, licenseConflicts = %s WHERE _id = %s;", (False, input_project_id, input_project_version, incompatibility_count, repo_id))
    conn.commit()
    cur.close()
    conn.close()

def update_process_time(field: str, repo_id: str, repo_url: str):
    if field not in ("processing_start_time", "processing_end_time"):
        raise ValueError("Invalid field. Must be 'processing_start_time' or 'processing_end_time'.")

    conn = get_db_conn()
    cur = conn.cursor()
    query = f"UPDATE searchrepos SET {field} = NOW() WHERE _id = %s AND repository_url = %s;"
    cur.execute(query, (repo_id, repo_url))
    conn.commit()
    cur.close()
    conn.close()

def get_search_repos(search_repo, repo_org):
    conn = get_db_conn()
    cur = conn.cursor()

    if search_repo and search_repo.isdigit():
        # run with the N number of repos from database
        if len(repo_org):
            cur.execute("SELECT _id, repository_url, license, language, licenseconflicts, is_active, organization FROM searchrepos WHERE organization= %s AND is_active=True AND has_picked=False LIMIT %s;", (repo_org, int(search_repo)))
        else:
            cur.execute("SELECT _id, repository_url, license, language, licenseconflicts, is_active, organization FROM searchrepos WHERE is_active=True AND has_picked=False LIMIT %s;", (int(search_repo),))
        
    else:
        #print("search_repo: ", search_repo)
        # Run for a particular repository for unit testing
        # 'https://github.com/microsoft/cocos2d-x'
        cur.execute("UPDATE searchrepos SET is_active = %s WHERE repository_url = %s;", (True, search_repo))
        if cur.rowcount == 0:
            # If no rows were updated, insert a new record
           cur.execute("""INSERT INTO searchrepos (_id, organization, project_id, repository_url, license, language, licenseConflicts, is_active
                ) VALUES (TO_CHAR(NOW(), 'YYYYMMDDHH24MISSUS'), %s, '', %s, NULL, NULL, 0, %s);""", (repo_org,search_repo, True))
        
        cur.execute("SELECT _id, repository_url, license, language, licenseconflicts, is_active, project_id FROM searchrepos WHERE repository_url = %s;", (search_repo,))

    repos = cur.fetchall()
    if repos:
        picked_ids = [record[0] for record in repos]

        cur.execute(
            "UPDATE searchrepos SET has_picked=True WHERE _id IN %s;",
            (tuple(picked_ids),)
        )
        conn.commit()
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
        df = df[df['violation'].str.len() <= 100]
        
        # Remove duplicates based on (hash, project_id)
        df.drop_duplicates(subset=['hash', 'project_id', 'version'], inplace=True)

        # Generate unique ID by combining hash and project_id
        # df['hash'].astype(str) + "_" + df['project_id'].astype(str) + "_" +
        df['_id'] = df['hash'].astype(str) + "_" + df['project_id'].astype(str)
        #df['organization'] = repo_org

        # Convert DataFrame to a list of tuples for batch insert
        records_to_insert = [
            (
                row['_id']+ datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"), row['hash'], row['project_id'], row['version'], row['license'], row['method_name'],
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

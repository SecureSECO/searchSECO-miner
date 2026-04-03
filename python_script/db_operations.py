import os
import psycopg2
import uuid
import pandas as pd
import traceback
import datetime
from dotenv import load_dotenv
from psycopg2.extras import execute_values

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

load_dotenv(dotenv_path)


def get_db_conn():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    return conn


def update_searchrepos(input_project_id, input_project_version, repo_id, stat_count):
    conn = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()

        update_query = """UPDATE searchrepos SET is_active = %s, project_id = %s, project_version = %s, no_match = %s, same_license = %s, dif_license_comply = %s, license_conflicts = %s,  high_risks = %s, undetermined = %s WHERE _id = %s;"""

        cur.execute(update_query, (False, input_project_id, input_project_version, stat_count[0], stat_count[1], stat_count[2], stat_count[3], stat_count[4], stat_count[5], repo_id))

        conn.commit()
        print("Rows affected:", cur.rowcount)

    except Exception as e:
        print("Error updating searchrepos:")
        print(e)
        traceback.print_exc()

    finally:
        if conn:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass


def update_process_time(field: str, repo_id: str, repo_url: str):
    if field not in ("processing_start_time", "processing_end_time"):
        raise ValueError("Invalid field. Must be 'processing_start_time' or 'processing_end_time'.")

    conn = get_db_conn()
    cur = conn.cursor()
    query = f"UPDATE searchrepos SET {field} = NOW() WHERE _id = %s AND repository_url = %s;"
    cur.execute(query, (repo_id, repo_url))
    conn.commit()
    print("Rows affected:", cur.rowcount)
    cur.close()
    conn.close()


def get_search_repos(search_repo, repo_org):
    conn = get_db_conn()
    cur = conn.cursor()

    if search_repo and search_repo.isdigit():
        # run with the N number of repos from database
        if len(repo_org):
            cur.execute("SELECT _id, repository_url, license, language, license_conflicts, is_active, organization FROM searchrepos WHERE organization= %s AND is_active=True AND has_picked=False LIMIT %s;", (repo_org, int(search_repo)))
        else:
            cur.execute("SELECT _id, repository_url, license, language, license_conflicts, is_active, organization FROM searchrepos WHERE is_active=True AND has_picked=False LIMIT %s;", (int(search_repo),))
        
    else:
        #print("search_repo: ", search_repo)
        # Run for a particular repository for unit testing
        # 'https://github.com/microsoft/cocos2d-x'
        cur.execute("UPDATE searchrepos SET is_active = %s WHERE repository_url = %s;", (True, search_repo))
        if cur.rowcount == 0:
            # If no rows were updated, insert a new record
           cur.execute("""INSERT INTO searchrepos (_id, organization, project_id, repository_url, license, language, license_conflicts, is_active
                ) VALUES (TO_CHAR(NOW(), 'YYYYMMDDHH24MISSUS'), %s, '', %s, NULL, NULL, 0, %s);""", (repo_org,search_repo, True))
        
        cur.execute("SELECT _id, repository_url, license, language, license_conflicts, is_active, project_id FROM searchrepos WHERE repository_url = %s;", (search_repo,))

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


def insert_into_rp_data(df1, repo_id):
    try:
        # Connect to PostgreSQL
        conn = get_db_conn()
        cur = conn.cursor()

        # Rename CSV columns to match the database
        df= df1.rename(columns={
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
            'Source_project_version': 'source_project_version'
        })

        # Remove duplicates based on (hash, project_id, version)
        df.drop_duplicates(subset=['hash', 'project_id', 'version'], inplace=True)

        # Generate unique _id using hash + project_id + timestamp + uuid
        df['_id'] = df.apply(
            lambda row: f"{row['hash']}_{row['project_id']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}_{uuid.uuid4().hex[:8]}",
            axis=1
        )

        # Add foreign key reference
        df['relational_id'] = repo_id

        # Replace NaNs with None (PostgreSQL handles None as NULL)
        df = df.where(pd.notnull(df), None)

        # Convert DataFrame to list of tuples for batch insert
                
        records_to_insert = [
            (
                row['_id'], row['hash'], row['project_id'], row['version'], row['license'],
                row['method_name'], row['file_location'], row['function_code'], row['repository_url'],
                row['query_project'], row['violation'], row['source_project'], row['source_project_version'],
                row['relational_id']
            ) for _, row in df.iterrows()
        ]

        # Bulk insert query
        insert_query = """
        INSERT INTO repository_data (
            _id, hash, project_id, version, license, method_name,
            file_location, function_code, repository_url, query_project, violation,
            source_project, source_project_version, relational_id
        ) VALUES %s
        ON CONFLICT (hash, project_id, version) DO NOTHING;
        """

        execute_values(cur, insert_query, records_to_insert)

        # Commit changes
        conn.commit()
        print(f"Inserted {len(records_to_insert)} new records successfully.")

    except Exception as e:
        print("Error occurred during insert:")
        print(e)
        traceback.print_exc()

    finally:
        # Close connection
        if conn:
            cur.close()
            conn.close()

    return df

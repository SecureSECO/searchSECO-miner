import psycopg2
import psycopg2.extras
import datetime
from db_operations import get_db_conn

GLOBAL_TABLE = "global_trivial_names"

def build_and_store_global_trivial_names(threshold=20, sample_limit=10, replace=True):
    """
    Build global trivial list (method names appearing in >= threshold distinct projects)
    and persist into `global_trivial_names` table.
    """
    conn = get_db_conn()
    cur = conn.cursor()

    sql = f"""
    SELECT method_name,
           COUNT(DISTINCT project_id) AS project_count,
           ARRAY_TO_STRING(ARRAY_AGG(DISTINCT project_id)[:%s], ',') AS sample_projects
    FROM repository_data
    WHERE method_name IS NOT NULL AND method_name <> ''
    GROUP BY method_name
    HAVING COUNT(DISTINCT project_id) >= %s
    ORDER BY project_count DESC;
    """

    cur.execute(sql, (sample_limit, threshold))
    rows = cur.fetchall()  # [(method_name, project_count, sample_projects), ...]

    # Option: replace table contents (atomically)
    if replace:
        cur.execute(f"DELETE FROM {GLOBAL_TABLE};")

    insert_sql = f"""
    INSERT INTO {GLOBAL_TABLE} (name, project_count, example_projects, last_updated)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (name) DO UPDATE
      SET project_count = EXCLUDED.project_count,
          example_projects = EXCLUDED.example_projects,
          last_updated = EXCLUDED.last_updated;
    """

    now = datetime.datetime.utcnow()
    to_insert = [(r[0], int(r[1]), r[2] or '', now) for r in rows]

    psycopg2.extras.execute_batch(cur, insert_sql, to_insert, page_size=500)
    conn.commit()
    cur.close()
    conn.close()

    return len(to_insert)


def load_global_trivial_set(min_count=None):
    """
    Load the global trivial names from DB. Optionally filter by minimum project_count.
    Returns a set of names.
    """
    conn = get_db_conn()
    cur = conn.cursor()
    params = []
    sql = f"SELECT name, project_count FROM {GLOBAL_TABLE}"
    if min_count is not None:
        sql += " WHERE project_count >= %s"
        params.append(min_count)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {r[0] for r in rows}


def filter_df_using_global_trivial(df, name_col="Method Name", whitelist=None, min_count=None):
    """
    Filters out rows whose method name exists in the global trivial list.
    - whitelist: iterable of names to keep even if they are in the global list.
    - min_count: if provided, load only names with project_count >= min_count.
    """
    if df is None or df.empty:
        return df.copy()
    if name_col not in df.columns:
        raise KeyError(f"{name_col} not found in df")

    global_set = load_global_trivial_set(min_count=min_count)
    if whitelist:
        global_set = set(global_set) - set(whitelist)

    # Do filtering using pandas vectorized isin (fast)
    mask = ~df[name_col].isin(global_set)
    return df[mask].reset_index(drop=True)

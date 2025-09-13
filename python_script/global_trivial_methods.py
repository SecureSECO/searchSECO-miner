# global_trivial_names.py

from collections import defaultdict
import json
import os
import re
from python_script.db_operations import get_db_conn


def filter_dataframe(df):
    valid_qp = {"0", "Yes"} | set(map(str, range(1, 6)))
    qp_clean = df["Query Project"].astype(str).str.strip()
    df_filtered = df[qp_clean.isin(valid_qp)]
    return df_filtered.copy()


def filter_trivial_functions_by_name(df, file_col="file_location"):
    
    if df.empty:
        return df.copy()

    if file_col not in df.columns:
        raise KeyError(f"Column '{file_col}' not found in DataFrame")

    df = df.copy()

    # --- Filter by Method Name ---
    df = df[df['Method Name'].str.match(r'^[A-Za-z_][A-Za-z0-9_]{2,}$', na=False)]

    # --- Filter by File Location ---
    df = df[df[file_col].str.contains(r'\w+/\w+.*\.\w+', na=False)]

    if df.empty:
        return df  # no rows left after filtering

    # --- Detect language from file extension ---
    def detect_language(path):
        ext = os.path.splitext(str(path))[1].lower()
        mapping = {
            ".c": "c", ".h": "c",
            ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
            ".cs": "cs", ".java": "java",
            ".js": "js", ".ts": "js",
            ".py": "py",
        }
        return mapping.get(ext, "other")

    df["Language"] = df[file_col].apply(detect_language)

    # --- Trivial patterns ---
    trivial_patterns = {
        "c": [r'^(get|set|init|reset|free|alloc|load|save|open|close|input|output|error|message|complete)$', r'^(main)$'],
        "cpp": [r'^(get|set|init|reset|copy|assign|release|load|save|open|close|input|output|error|message|complete)$', r'^(main|operator.*)$'],
        "cs": [r'^(get|set|reset|dispose|clone|load|save|open|close|input|output|error|message|complete|is[A-Z][A-Za-z0-9_]*)$', r'^(Main)$'],
        "java": [r'^(get|set|load|save|open|close|input|output|error|message|complete|is[A-Z][A-Za-z0-9_]*|clone|toString|hashCode|equals)$', r'^(main)$'],
        "js": [r'^(get|set|reset|constructor|load|save|open|close|input|output|error|message|complete)$', r'^(main)$'],
        "py": [r'^__.*__$', r'^(init|get|set|reset|load|save|open|close|input|output|error|message|complete|is_[a-z0-9_]+)$', r'^(main)$'],
        "other": [r'^__.*__$', r'^(init|get|set|reset|load|save|open|close|input|output|error|message|complete|is_[a-z0-9_]+)$', r'^(main)$'],
    }

    compiled_patterns = {lang: re.compile("|".join(pats), re.IGNORECASE) for lang, pats in trivial_patterns.items()}

    # --- Filtering ---
    def is_trivial(name, lang):
        regex = compiled_patterns.get(lang)
        return bool(regex and regex.match(str(name)))

    mask = ~df.apply(lambda row: is_trivial(row["Method Name"], row["Language"]), axis=1)

    # Drop "Language" safely
    if "Language" in df.columns:
        return df[mask].drop(columns=["Language"]).reset_index(drop=True)
    else:
        return df[mask].reset_index(drop=True)


def build_and_store_global_trivial_names(threshold=20, sample_limit=10, replace=True):
    """
    Build a global set of trivial method names based on how many distinct
    projects they appear in, and store them in the database.
    """
    conn = get_db_conn()
    cur = conn.cursor()

    # 1. Fetch all method_name + project_id pairs
    cur.execute("""
        SELECT method_name, project_id
        FROM repository_data
        WHERE method_name IS NOT NULL AND method_name <> ''
    """)
    rows = cur.fetchall()

    # 2. Build mapping: method_name -> distinct projects
    project_map = defaultdict(set)
    for method, proj in rows:
        project_map[method].add(proj)

    # 3. Count how many distinct projects each method appears in
    project_counts = {m: len(p) for m, p in project_map.items()}

    # 4. Select trivial names
    trivial_names = {m for m, cnt in project_counts.items() if cnt >= threshold}
    print(f"Identified {len(trivial_names)} global trivial names (threshold={threshold})")

    # Print top frequent method names for diagnostics
    top = sorted(project_counts.items(), key=lambda x: x[1], reverse=True)[:sample_limit]
    print("Top frequent method names:")
    for name, count in top:
        print(f"  {name}: {count} projects")

    # 5. Ensure global_trivial_names table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS global_trivial_names (
            method_name TEXT PRIMARY KEY,
            project_count INTEGER NOT NULL
        )
    """)

    if replace:
        cur.execute("DELETE FROM global_trivial_names")

    # 6. Insert trivial names
    for method in trivial_names:
        cur.execute(
            """
            INSERT INTO global_trivial_names (method_name, project_count)
            VALUES (%s, %s)
            ON CONFLICT (method_name)
            DO UPDATE SET project_count = EXCLUDED.project_count
            """,
            (method, project_counts[method]),
        )

    conn.commit()
    cur.close()
    conn.close()

    return trivial_names


def export_global_trivial_names(file_path="global_trivial_names.json"):
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT method_name, project_count FROM global_trivial_names")
    data = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    conn.close()
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def load_global_trivial_names(file_path="global_trivial_names.json"):
    """
    Load global trivial names from a JSON file.
    """

    with open(file_path, "r") as f:
        data = json.load(f)
    # Only keys (method names) are needed for filtering
    return set(data.keys())


def filter_with_global_trivial_names(df, file_path="global_trivial_names.json"):
    trivial_names = load_global_trivial_names(file_path)
    return df[~df["Method Name"].isin(trivial_names)].reset_index(drop=True)


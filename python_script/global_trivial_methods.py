# global_trivial_methods.py

from collections import defaultdict
import json
import os
import re
import hashlib
from db_operations import get_db_conn


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
    def detect_language(path: str) -> str:
        # Remove any trailing line number (e.g. file.py:123 -> file.py)
        clean_path = re.sub(r":\d+$", "", str(path))
        
        ext = os.path.splitext(clean_path)[1].lower()
        
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
        "java": [r'^(get|set|load|run|save|open|close|input|output|error|message|complete|is[A-Z][A-Za-z0-9_]*|clone|toString|hashCode|equals)$', r'^(main)$'],
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


def build_and_store_global_trivial_names(file_path="global_trivial_names.json", sample_limit=10, seen_limit=100):
    """
    Build a global set of trivial method names, keeping counts of distinct projects.
    Uses a compact JSON format to avoid large file size.
    """

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT method_name, project_id FROM repository_data WHERE method_name IS NOT NULL AND method_name <> ''")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Load existing data if present
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = {}

    # Convert existing seen_projects to sets for easy updating
    for k, v in data.items():
        v["seen_projects"] = set(v.get("seen_projects", []))

    for method_name, project_id in rows:
        # Use a short hash of project_id to save space
        proj_hash = hashlib.sha1(str(project_id).encode()).hexdigest()[:8]

        if method_name not in data:
            data[method_name] = {"count": 0, "seen_projects": set()}

        if proj_hash not in data[method_name]["seen_projects"]:
            data[method_name]["count"] += 1
            if len(data[method_name]["seen_projects"]) < seen_limit:
                data[method_name]["seen_projects"].add(proj_hash)

    # Convert seen_projects back to lists for JSON
    for v in data.values():
        v["seen_projects"] = list(v["seen_projects"])

    # Save JSON
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    
    """
    # Print top frequent method names for diagnostics
    top = sorted(data.items(), key=lambda x: x[1]["count"], reverse=True)[:sample_limit]
    
    print("Top frequent method names:")
    for name, info in top:
        print(f"  {name}: {info['count']} projects")
    """
    return None


def load_global_trivial_names(file_path="global_trivial_names.json", threshold=None):
    """
    Load global trivial names from JSON.
    Only return method names meeting the optional threshold (count of distinct projects).
    """
    import os, json

    if not os.path.exists(file_path):
        return set()

    with open(file_path, "r") as f:
        data = json.load(f)

    if threshold is not None:
        # Filter methods by count
        data = {method: info for method, info in data.items() if info.get("count", 0) >= threshold}

    return set(data.keys())


def filter_with_global_trivial_names(df, file_path="global_trivial_names.json", threshold=20):
    """
    Filter dataframe by removing global trivial method names.
    """
    trivial_names = load_global_trivial_names(file_path, threshold)
    return df[~df["Method Name"].isin(trivial_names)].reset_index(drop=True)


"""
#Periodically (e.g., daily or after ingesting N new repos) run

from global_trivial_methods import build_and_store_global_trivial_names

build_and_store_global_trivial_names(file_path="../input_files/global_trivial_names.json")
"""
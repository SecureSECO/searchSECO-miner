import csv
import os
import time
import requests
import re
import psycopg2
from psycopg2 import sql
from datetime import datetime, timezone
from typing import Optional
from db_operations import get_db_conn
from dotenv import load_dotenv

load_dotenv("../../src/config/.env")

GITHUB_PAT = os.getenv("GITHUB_TOKEN")

API_CALL_DELAY_SECONDS = 1.2

# Granular 1
def github_repo_exists(repo_url: str) -> bool:
    try:
        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            return False
        owner = match.group(1)
        repo = match.group(2)
        base_repo_url = f"https://github.com/{owner}/{repo}"
        response = requests.head(base_repo_url, allow_redirects=True)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Granular 2
def check_version_and_get_sha(repo_url, version):
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        print(f"--> Invalid GitHub URL: {repo_url}")
        return None, None, None
    owner, repo = match.groups()

    try:
        timestamp_sec = int(version) / 1000
        dt_object = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
        iso_timestamp = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')
    except (ValueError, TypeError):
        print(f"--> Invalid timestamp format: {version}")
        return None, None, None

    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {'Authorization': f'token {GITHUB_PAT}', 'Accept': 'application/vnd.github.v3+json'}
    params = {'until': iso_timestamp, 'per_page': 1}
    
    time.sleep(API_CALL_DELAY_SECONDS)

    try:
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code in [404, 409, 403]: # Added 403 for PAT issues
            print(f"--> Repo not found, empty, private, or PAT invalid: {owner}/{repo} (Status: {response.status_code})")
            return None, None, None
        
        response.raise_for_status()
        commits = response.json()
        
        if commits:
            commit_sha = commits[0]['sha']
            print(f"--> Found version for timestamp {version} in {owner}/{repo}. Commit SHA: {commit_sha}")
            return commit_sha, owner, repo
        else:
            print(f"--> No version found for timestamp {version} in {owner}/{repo}")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"--> Request failed for {owner}/{repo}: {e}")
        return None, None, None

#Granular 3
def find_file_at_exact_path(full_file_url: str) -> bool:
    url_without_fragment = full_file_url.split('#')[0]
    try:
        response = requests.head(url_without_fragment, allow_redirects=True, timeout=10)
        return response.status_code == 200

    except requests.exceptions.RequestException:
        return False



#Granular 4
def find_method_in_file(url: str, method_name: str) -> Optional[str]:
    try:
        # 1. Convert URL to raw format and fetch content
        base_url = url.split('#')[0]
        raw_url = base_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/').replace('/./', '/')

        
        response = requests.get(raw_url, timeout=10)
        response.raise_for_status()  # Check for HTTP errors (like 404 Not Found)

        # 2. Search for the method in the content
        for line in response.text.splitlines():
            if method_name in line:
                return line  

    except requests.exceptions.RequestException as e:
        # This block handles network, timeout, or HTTP errors
        print(f"Failed to process '{url}'. Reason: {e}")
        return None  # Return None on any exception

    # 3. If the loop completes, the method wasn't found
    return None

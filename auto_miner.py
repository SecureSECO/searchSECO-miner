import subprocess
import os
import re
from datetime import datetime
import requests
import time
import sys
import pandas as pd
import logging
from logging.handlers import RotatingFileHandler
import traceback
from python_script.licenses import compatibility_matrix, license_mapping, LICENSE_LIST
from python_script.db_operations import update_searchrepos, get_search_repos, insert_into_rp_data, update_process_time
from dotenv import load_dotenv

load_dotenv("./src/config/.env")


'''
def get_function_code_from_github(url, retry_count=2):
    """Extract function code from GitHub URL with retries and better error handling"""
    
    if not url:
        return "Not a valid url"
        
    for attempt in range(retry_count):
        try:
            #print(f"Fetching code from {url}...")
            raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/').replace('\\', '/')
        
            response = requests.get(raw_url, timeout=10)
            
            if response.status_code == 200:
                lines = response.text.split('\n')
                try:
                    # Find the line number from URL
                    line_parts = url.split('#L')
                    if len(line_parts) < 2:
                        print(f"Warning: No line number found in URL {url}")
                        return "No line number found in URL"
                    
                    # Handle line range if present (e.g., #L20-L30)
                    line_range = line_parts[-1].split('-')
                    start_line = int(line_range[0])
                    
                    # Extract function starting from the specified line
                    function_code = []
                    brace_count = 0
                    in_function = False
                    
                    # Look for function start (first opening brace)
                    for i, line in enumerate(lines[start_line-1:], start_line):
                        if not in_function:
                            function_code.append(line)
                            if '{' in line:
                                in_function = True
                                brace_count = line.count('{') - line.count('}')
                                if brace_count == 0 and line.strip().endswith(';'):
                                    break
                        else:
                            function_code.append(line)
                            brace_count += line.count('{') - line.count('}')
                            
                            if brace_count == 0:
                                # Check if next non-empty line is part of the function
                                next_lines = [l for l in lines[i:i+3] if l.strip()]
                                if not next_lines or not any(l.strip().startswith(('else', 'catch', 'finally')) for l in next_lines):
                                    break
                        
                        # Safety limit to prevent infinite loops
                        if len(function_code) > 1000:
                            print(f"Warning: Function too long, truncating at 1000 lines for {url}")
                            break
                    
                    return '\n'.join(function_code)
                    
                except IndexError:
                    print(f"Warning: Line number {start_line} out of range for {url}")
                    return "Line number {start_line} out of range "
            else:
                print(f"HTTP {response.status_code} error for {url}")
                
            if attempt < retry_count - 1:
                time.sleep(2)  
                
        except Exception as e:
            print(f"Error fetching code from {url}: {e}")
            if attempt < retry_count - 1:
                time.sleep(2) 
                
    return "Error fetching code"
'''

def get_default_branch(owner, repo):
    """Fetch the default branch of a GitHub repository using GitHub API with authentication"""
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json().get('default_branch')
    else:
        raise Exception(f"Failed to fetch repo info: {response.status_code} - {response.text}")


def get_function_code_from_github(url, retry_count=2):
    """Extract function code from GitHub URL with retries and better error handling"""
    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    if not url:
        return "Not a valid url"

    for attempt in range(retry_count):
        try:
            # Extract owner, repo, and file path
            parts = url.strip().split('/')
            if len(parts) < 7 or 'blob' not in parts:
                return "Invalid GitHub blob URL"

            owner = parts[3]
            repo = parts[4]
            commit_or_branch = parts[6]
            file_path = '/'.join(parts[7:]).split('#')[0]

            # GitHub API URL to get file contents
            api_contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={commit_or_branch}"

            response = requests.get(api_contents_url, headers=headers, timeout=10)

            print("response: ", response)

            #requests.get(license_url, headers=headers)

            if response.status_code == 200:
                import base64
                file_content = response.json().get('content', '')
                if response.json().get('encoding') == 'base64':
                    decoded = base64.b64decode(file_content).decode('utf-8')
                    lines = decoded.split('\n')
                else:
                    return "Unsupported file encoding"
            else:
                print(f"GitHub API returned {response.status_code} for {url}")
                if attempt < retry_count - 1:
                    time.sleep(2)
                continue

            # Extract line number
            line_parts = url.split('#L')
            if len(line_parts) < 2:
                print(f"Warning: No line number found in URL {url}")
                return "No line number found in URL"

            line_range = line_parts[-1].split('-')
            start_line = int(line_range[0])

            # Extract function starting from the specified line
            function_code = []
            brace_count = 0
            in_function = False

            for i, line in enumerate(lines[start_line - 1:], start_line):
                if not in_function:
                    function_code.append(line)
                    if '{' in line:
                        in_function = True
                        brace_count = line.count('{') - line.count('}')
                        if brace_count == 0 and line.strip().endswith(';'):
                            break
                else:
                    function_code.append(line)
                    brace_count += line.count('{') - line.count('}')
                    if brace_count == 0:
                        next_lines = [l for l in lines[i:i + 3] if l.strip()]
                        if not next_lines or not any(l.strip().startswith(('else', 'catch', 'finally')) for l in next_lines):
                            break

                if len(function_code) > 1000:
                    print(f"Warning: Function too long, truncating at 1000 lines for {url}")
                    break

            return '\n'.join(function_code)

        except IndexError:
            print(f"Warning: Line number out of range for {url}")
            return f"Line number out of range"
        except Exception as e:
            print(f"Error fetching code from {url}: {e}")
            if attempt < retry_count - 1:
                time.sleep(2)

    return "Error fetching code"

def parse_matches(output, repo_url):
    """Parse the output to extract matched functions and their repositories"""
    
    print("\nParsing matches from SearchSECO output...")
    matches = []
    current_match = None
    current_hash = None
    
    lines = output.split('\n')
    #total_matches = sum(1 for line in lines if line.startswith('Hash '))
    current_match_num = 0
    #database=1
    
    for line in lines:
        # Look for start of new match group (hash line)
        if line.startswith('Hash '):
            current_match_num += 1
            #print(f"\nProcessing match group {current_match_num}/{total_matches}")
            if current_match:
                matches.append(current_match)
            current_match = None
            current_hash = line.split()[1]  # Extract the hash value
            #print(f"Hash: {current_hash}")
            database=1
            
        # Look for method match lines
        elif line.strip().startswith('* Method') and 'in file' in line:
            # If we find a new method in the same hash group, add it as a variant
            if current_match and current_hash:
                match = re.search(r'\* Method (.*?) in file (.*?), line (\d+)', line)
                if match:
                    
                    variant = {
                        'method_name': match.group(1),
                        'method_file': match.group(2),
                        'method_line': match.group(3),
                        'url': None,
                        'function_code': None
                    }
                    if 'variants' not in current_match:
                        current_match['variants'] = []
                    current_match['variants'].append(variant)
            else:
                
                current_match = {
                    'hash': current_hash,
                    'method_name': '',
                    'method_file': '',
                    'method_line': '',
                    'found_in': [],
                    'function_code': None,
                    'variants': []
                }
                
                match = re.search(r'\* Method (.*?) in file (.*?), line (\d+)', line)
                if match:
                    file_path=match.group(2).split('./')[1]
                    line_number= match.group(3)
                    url=f"{repo_url}/blob/main/{file_path}#L{line_number}"

                    current_match['method_name'] = match.group(1)
                    current_match['method_file'] = match.group(2)
                    current_match['method_line'] = match.group(3)
                    current_match['found_in'].append(url)
                
        # Look for database match URLs
        elif 'URL:' in line:
            if current_match:
                url = line.strip().split('URL:')[1].strip()
                # Add URL to the last variant if it exists, otherwise to main match
                if current_match['variants'] and current_match['variants'][-1]['url'] is None:
                    #print("found in url variants: ", url)
                    current_match['variants'][-1]['url'] = url
                else:
                    #print("found in url: ", url)
                    current_match['found_in'].append(url)
    
    # Add the last match if exists
    if current_match:
        matches.append(current_match)
    
    if not matches:
        return []

    return matches


def get_github_repo_info(repo_url):
    match = re.match(r"https://github.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        return "Invalid GitHub URL", "Invalid GitHub URL", "Invalid GitHub URL"
    
    owner, repo = match.groups()
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    try:
        # Get License Information
        license_url = f"{base_url}/license"
        license_response = requests.get(license_url, headers=headers)
        license_info = license_response.json().get("license", {}).get("spdx_id", "Not Found")
        
        # Get Latest Release Version and Date
        releases_url = f"{base_url}/releases/latest"
        release_response = requests.get(releases_url, headers=headers)
        if release_response.status_code == 200:
            release_data = release_response.json()
            release_info = release_data.get("tag_name", "No Releases Found")
            release_date = release_data.get("published_at")
        else:
            release_info = "No Releases Found"
            release_date = None
        
        # Determine timestamp from release or last commit
        if release_date:
            timestamp = int(datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000)
        else:
            # Fetch last commit date
            last_commit_url = f"{base_url}/commits?per_page=1&page=1"
            last_commit_response = requests.get(last_commit_url, headers=headers)
            
            if last_commit_response.status_code == 403:  # Forbidden error
                print("⚠️ 403 Forbidden: Trying repository metadata instead...")
                repo_metadata_response = requests.get(base_url, headers=headers)
                
                if repo_metadata_response.status_code == 200:
                    repo_metadata = repo_metadata_response.json()
                    if repo_metadata.get("archived", False):
                        print("⚠️ Repository is archived, commit data not available.")
                        timestamp = "Repository Archived"
                    else:
                        timestamp = int(datetime.strptime(repo_metadata.get("pushed_at", "1970-01-01T00:00:00Z"), "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000)
                else:
                    timestamp = "Metadata Fetch Failed"
            
            elif last_commit_response.status_code == 200:
                last_commit_data = last_commit_response.json()
                if last_commit_data:
                    last_commit_date = last_commit_data[0].get("commit", {}).get("author", {}).get("date", "No Commits Found")
                    timestamp = int(datetime.strptime(last_commit_date, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000) if last_commit_date != "No Commits Found" else "No Commits Found"
                else:
                    timestamp = "No Commits Found"
            else:
                timestamp = f"Commit Fetch Failed ({last_commit_response.status_code})"
    
    except requests.exceptions.RequestException as e:
        return "Error fetching data", "Error fetching data", f"Error: {str(e)}"
    
    return license_info, release_info, timestamp


def save_to_csv(df, incompatibility_count, actual_violation, repo_url, input_project_id, save_dir):
    """Save matches to CSV file with function code and all repositories."""
    
    filename = f"{repo_url.split('.com/')[1].replace('/','_')}_matches_{input_project_id}_{incompatibility_count}_{actual_violation}.csv"
    
    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    filepath = os.path.join(save_dir, filename)
    
    df.drop(columns=['_id'], errors='ignore').to_csv(filepath, index=False)

    print(f"Results saved to {filepath}")


def create_dataFrame(matches, repo_url):

    try:

        data = []
        input_project_id = None
        # Iterate over matches and process data
        for i, match in enumerate(matches, 1):
            try:

                method_name = match['method_name'].split(',')[0]
                project_id = match['method_name'].split(',')[1].split(':')[1].strip()
                project_version = match['method_name'].split(',')[2].split(':')[1].strip()
                project_license = match['method_name'].split(',')[3].split(':')[1].strip()

                input_project_id = project_id
                input_project_version = project_version

                # Add original function to the data list
                data.append([
                    match['hash'],
                    project_id,
                    project_version,
                    project_license,
                    method_name,
                    f"{match['method_file']}:{match['method_line']}",
                    match['function_code'] or "Didn't pull code",
                    '; '.join(match['found_in']),
                    "Yes"
                ])

                if (i%100==0):
                    print("{} hash has been processed".format(i))

                # Process and add variants
                for variant in match['variants']:
                    elements= variant['method_name'].split(',')
                    if(len(elements)<4): 
                        continue
                    #print("Variant method_name: ",  variant['method_name'])
                    method_name = match['method_name'].split(',')[0]
                    project_id = variant['method_name'].split(',')[1].split(':')[1].strip()
                    project_version = variant['method_name'].split(',')[2].split(':')[1].strip()
                    project_license = variant['method_name'].split(',')[3].split(':')[1].strip()
                    
                    data.append([
                        match['hash'],
                        project_id,
                        project_version,
                        project_license,
                        method_name,
                        f"{variant['method_file']}:{variant['method_line']}",
                        variant['function_code'] or "Didn't pull code",
                        variant['url'],
                        "No"
                    ])
                
                #if(i==400):
                #        break
            except Exception as e:
                print(f"Error processing match {i}: {e}")

        columns = ['Hash', 'Project ID', 'Version', 'License', 'Method Name', 'File Location', 
                'Function Code', 'Repository URL', 'Query Project']
        df = pd.DataFrame(data, columns=columns)
        
    except Exception as e:
        print(f"Error: {e}")

    return df, input_project_id, input_project_version


def run_searchseco_check(repo_url):
    """Run the SearchSECO check command and capture output"""
    try:
        
        # Run the check command ###check
        cmd = f"npm run execute -- checkupload {repo_url} -V 5"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Debug output
        print("\nSearchSECO Output:")
        print(result.stdout)
         
        if result.stderr:
            print("\nSearchSECO Errors:")
            print(result.stderr)
            
        return result.stdout
    except Exception as e:
        print(f"Error running SearchSECO check: {e}")
        return None

def normalize_license(license_name: str) -> str:
    return license_mapping.get(license_name, license_name)

def can_reuse_code(source_license: str, target_license: str) -> bool:
    
    return compatibility_matrix[target_license][source_license]

def check_license_compatibility(df):
    
    df["Violation"] = ""
    df["Source_project"] = ""
    df["Source_project_version"] = ""
    incompatibility_count = 0 
    # Sorting by Version (timestamp) within each hash group
    df = df.sort_values(by=["Hash", "Version"])
    grouped = df.groupby("Hash")

    for function_hash, group in grouped:
        base_license = normalize_license(group.iloc[0]["License"])  # Normalize first row's license
        source_project_id = group.iloc[0]["Project ID"]
        source_project_version = group.iloc[0]["Version"]
        group_idx = group.index[0]
        df.at[group_idx, "Query Project"] = "0"

        for idx, row in group.iloc[1:].iterrows():
            if df.at[idx, "Query Project"] == "Yes":
                license_type = normalize_license(row["License"])
                if license_type not in LICENSE_LIST or base_license not in LICENSE_LIST:
                    df.at[idx, "Violation"] = "Undetermined"
                    df.at[idx, "Source_project"] = source_project_id
                    df.at[idx, "Source_project_version"] = source_project_version
                elif not can_reuse_code(base_license, license_type):
                    df.at[idx, "Violation"] = f"{license_type} incompatible with {base_license}"
                    df.at[idx, "Source_project"] = source_project_id
                    df.at[idx, "Source_project_version"] = source_project_version
                    df.at[group_idx, "Query Project"] = "1"
                    
                    incompatibility_count += 1
                    #print(f"Incompatible licenses detected for function {function_hash}: {base_license} vs {license_type}")
            
    df = df[df['Query Project'].isin(['0', '1','Yes'])]

    print("Total number of incompatibility: ", incompatibility_count)

    return df, incompatibility_count

def get_function_code(row):
   
    if row['Query Project'] == "1" or "incompatible" in str(row['Violation']).lower():
        return get_function_code_from_github(row['Repository URL'])
    else:
        return None

def main():
    """
        Four ways of checking your repository(ies)
            - A single repo: python auto_miner.py Y https://github.com/Samsung/mTower
            - X (=20) number of repo from database: python auto_miner.py N 20
            - With a default value of X (=100): python auto_miner.py N      # default is 100
            - With the shell script: nohup ./run_python_miner.sh | tail -n 2000 > logfile.log 2>&1 &
            - Parameter N/Y determine whether a method code will be downloaded or not
        # https://github.com/google/ios-webkit-debug-proxy
        # https://github.com/Samsung/ColorPatternTracker
        # https://github.com/microsoft/Windows-universal-samples
    """
    
    fun_code = False if sys.argv[1] == "N" else True
    search_repo = sys.argv[2] if len(sys.argv) > 2 else '100'
    #print(search_repo)

    company_name = "Microsoft"
    
    repos = get_search_repos(search_repo, company_name) # provide organization name: Google, Microsoft etc.

    if len(repos)<1:
        repos = get_search_repos(search_repo, "")

    #print("Total number of searchrepos attempting: ", len(repos))

    for repo in repos:
        """
        repo_data = {
            "_id": repo[0],
            "repo_url": repo[1],
            "license": repo[2],
            "language": repo[3],
            "licenseconflicts": repo[4],
            "is_active": repo[5]
            "organization": repo[6]
        }
        """
    
        if repo[5] == True:
            repo_id = repo[0]
            repo_url = repo[1]
            
            update_process_time("processing_start_time", repo_id, repo_url)
        
            print("Running SearchSECO analysis...")
            output = run_searchseco_check(repo_url)
            
            if not output:
                print("Failed to get analysis results")
                continue
            
            print("Parsing matches...")
            matches = parse_matches(output, repo_url)
            
            if not matches:
                print("No matches found")
                # input_project_id, input_project_version, repo_id, incompatibility_count, actual_violation
                update_searchrepos("", "", repo_id, -1, 0)
                continue
            
            print("Fetching function code and creating a dataframe...")
            df, input_project_id, input_project_version = create_dataFrame(matches, repo_url)
          
            print("Checking license compatibility...")
            
            df, incompatibility_count = check_license_compatibility(df)
            
            actual_violation = 0
            
            if fun_code:
                df["Function Code"] = df.apply(get_function_code, axis=1)
                
                count_query_proj = df[~df["Function Code"].str.contains("Error fetching code", na=False) &  
                (df["Query Project"] == "Yes") & 
                df["Violation"].str.contains("incompatible", case=False, na=False)
                ].shape[0]

                count_source_proj = df[~df["Function Code"].str.contains("Error fetching code", na=False) &  
                                (df["Query Project"] == "1") 
                                ].shape[0]
                
                actual_violation = min(count_query_proj, count_source_proj)

                print("Actual violations:", actual_violation)

            print("Saving results to database...")
            
            update_process_time("processing_end_time", repo_id, repo_url)
            
            df = insert_into_rp_data(df, repo_id)

            #### Visual Inspection ####
            
            #print("Saving results to CSV...")
            save_to_csv(df, incompatibility_count, actual_violation, repo_url, input_project_id, save_dir="results")
            #time.sleep(0.01)
            
            #### End Visual Inspection ####
            
            print("Updating the query table and exiting..")
            update_searchrepos(input_project_id, input_project_version, repo_id, incompatibility_count, actual_violation)


if __name__ == "__main__":
    # Setup error logging
    log_dir = './logging'
    os.makedirs(log_dir, exist_ok=True)
    
    handler = RotatingFileHandler(
        os.path.join(log_dir, 'error_log.txt'),
        maxBytes=1_000_000,  # 1 MB
        backupCount=10       # Keep last 10 logs
    )

    logging.basicConfig(
        filename=os.path.join(log_dir, 'error_log.txt'),
        level=logging.ERROR,
        format='%(asctime)s [%(levelname)s] %(message)s',
    )
    try:
        main()
    except Exception as e:
        # Log to error_log.txt
        logging.error("Unhandled exception in main:\n%s", traceback.format_exc())

        # Also print to stdout so your shell sees something
        print(f"Error occurred. See error_log.txt for details: {e}")
        sys.exit(1)


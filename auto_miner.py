import subprocess
import os
import re
from datetime import datetime
import requests
import time
import sys
import pandas as pd
from python_script.licenses import compatibility_matrix, license_mapping
from python_script.db_operations import get_db_repos
from dotenv import load_dotenv
load_dotenv("./src/config/.env")

def get_function_code_from_github(url, retry_count=3):
    """Extract function code from GitHub URL with retries and better error handling"""
    if not url:
        return None
        
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
                        return None
                    
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
                    return None
            else:
                print(f"HTTP {response.status_code} error for {url}")
                
            if attempt < retry_count - 1:
                time.sleep(2)  
                
        except Exception as e:
            print(f"Error fetching code from {url}: {e}")
            if attempt < retry_count - 1:
                time.sleep(2) 
                
    return None

def parse_matches(output, repo_url, fun_code):
    """Parse the output to extract matched functions and their repositories"""
    print("\nParsing matches from SearchSECO output...")
    matches = []
    current_match = None
    current_hash = None
    
    lines = output.split('\n')
    total_matches = sum(1 for line in lines if line.startswith('Hash '))
    current_match_num = 0
    database=1
    
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
                    #print("match.group", match.group(1))
            
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
                    #print("method_file: ", match.group(1))
                    file_path=match.group(2).split('./')[1]
                    line_number= match.group(3)
                    #print("method_file : ")
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

    # Get function code for each match and its variants
 
    #print("\nFetching function code for matches...")
    if fun_code:
        for i, match in enumerate(matches, 1):
            #print(f"\nProcessing match {i}/{len(matches)}")
            if match['found_in']:
                #print(f"Fetching original function from {match['method_file']}")
                match['function_code'] = get_function_code_from_github(match['found_in'][0])
            
            for j, variant in enumerate(match['variants'], 1):
                if variant['url']:
                    #print(f"Fetching variant {j}/{len(match['variants'])} from {variant['method_file']}")
                    variant['function_code'] = get_function_code_from_github(variant['url'])
    
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
        
        if release_date:
            timestamp = int(datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000)
        else:
            # Fetch last commit date if no releases exist
            last_commit_url = f"{base_url}/commits?per_page=1&page=1"
            last_commit_response = requests.get(last_commit_url, headers=headers)
            last_commit_response.raise_for_status()
            last_commit_data = last_commit_response.json()
            if last_commit_data:
                last_commit_date = last_commit_data[0].get("commit", {}).get("author", {}).get("date", "No Commits Found")
                timestamp = int(datetime.strptime(last_commit_date, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000) if last_commit_date != "No Commits Found" else "No Commits Found"
            else:
                timestamp = "No Commits Found"
        
    except requests.exceptions.RequestException as e:
        return "Error fetching data", "Error fetching data", f"Error: {str(e)}"
    
    return license_info, release_info, timestamp


def save_to_csv(df, repo_url, input_project_id, save_dir):
    """Save matches to CSV file with function code and all repositories."""
    
    print("\nSaving results to CSV...")
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{repo_url.split('.com/')[1].replace('/','_')}_matches_{input_project_id}.csv"
    
    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)
    
    # Full path for the CSV file
    filepath = os.path.join(save_dir, filename)
    
    df.to_csv(filepath, index=False) 

    print(f"Results saved to {filepath}")

def create_dataFrame(matches, repo_url):

    try:
        #import pandas as pd

        # Initialize an empty list to store data
        data = []
        input_project_id = None
        # Iterate over matches and process data
        for i, match in enumerate(matches, 1):
            try:
                project_id = match['method_name'].split(',')[1].split(' ')[3]
                input_project_id = project_id
                project_version = None
                project_license = None
                project_license, release_info, project_version = get_github_repo_info(repo_url)
                input_project_version = project_version
                method_name = match['method_name'].split(',')[0]

                # Add original function to the data list
                data.append([
                    match['hash'],
                    project_id,
                    project_version,
                    project_license,
                    method_name,
                    f"{match['method_file']}:{match['method_line']}",
                    match['function_code'] or "Code not available",
                    '; '.join(match['found_in']),
                    "Yes"
                ])

                # Process and add variants
                for variant in match['variants']:
                    #print("variant details: ", variant['method_name'])
                    method_name = variant['method_name'].split(',')[0].split(':')[1].strip()
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
                        variant['function_code'] or "Code not available",
                        variant['url'],
                        "No"
                    ])
            
            except Exception as e:
                print(f"Error processing match {i}: {e}")

        # Create a DataFrame
        columns = ['Hash', 'Project ID', 'Version', 'License', 'Method Name', 'File Location', 
                'Function Code', 'Repository URL', 'Query Project']
        df = pd.DataFrame(data, columns=columns)

        # Display or save the DataFrame
        #print(df.head())  # Show first few rows
        #df.to_csv(filepath, index=False)  # Optional: Save to CSV
        
    except Exception as e:
        print(f"Error: {e}")

    return df, input_project_id, input_project_version


def run_searchseco_check(repo_url):
    """Run the SearchSECO check command and capture output"""
    try:
        # Change directory to where the SearchSECO miner is installed
        #miner_path = "."  # Adjust this path as needed
        #os.chdir(miner_path)
        
        # Run the check command ###check
        cmd = f"npm run execute -- checkupload {repo_url} -V 5"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Change back to original directory
        #os.chdir("..")
        
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
    return license_mapping.get(license_name, license_name)  # Default to original if not found

def can_reuse_code(source_license: str, target_license: str) -> bool:
    return compatibility_matrix.get(target_license, {}).get(source_license, False)

def check_license_compatibility(df):
    #df = pd.read_csv(file)
    df["Violation"] = ""
    df["Source_project"] = ""
    df["Source_project_version"] = ""
    incompatibility_count = 0 
    # Sorting by Version (timestamp) within each hash group
    df = df.sort_values(by=["Hash", "Version"])
    grouped = df.groupby("Hash")
    license_list=["MIT", "Apache-2.0", "BSD-3-Clause", "MPL-2.0", "GPLv3", "LGPL-3.0"] 
    for function_hash, group in grouped:
        base_license = normalize_license(group.iloc[0]["License"])  # Normalize first row's license
        source_project_id=group.iloc[0]["Project ID"]
        Source_project_version=group.iloc[0]["Version"]
        
        for idx, row in group.iloc[1:].iterrows(): # Compare the first row's license with rest of the others
            license_type = normalize_license(row["License"])
            if license_type not in license_list or base_license not in license_list:
                df.at[idx, "Violation"] = "Undetermined"
            elif not can_reuse_code(base_license, license_type):
                df.at[idx, "Violation"] = f"{license_type} incompatible with {base_license}"
                df.at[idx, "Source_project"] = source_project_id
                df["Source_project_version"] = Source_project_version
                incompatibility_count += 1
                #print(f"Incompatible licenses detected for function {function_hash}: {base_license} vs {license_type}")
                
    print("Total number of incompatibility: ", incompatibility_count)
    return df


def main():

    get_fun_code = lambda x: False if x == "N" else True
    fun_code = get_fun_code(sys.argv[1])
    print("fun_code: ", get_fun_code(sys.argv[1]))

    conn = get_db_repos()
    cur = conn.cursor()
    #cur.execute("SELECT _id, repository_url, license, language, licenseconflicts, is_active FROM searchrepos WHERE is_active=True;")
    # Run for a particular repository for unit testing
    cur.execute("UPDATE searchrepos SET is_active = %s WHERE repository_url = %s;", (True, 'https://github.com/shibingli/webconsole'))
    cur.execute("SELECT _id, repository_url, license, language, licenseconflicts, is_active, project_id FROM searchrepos WHERE repository_url = 'https://github.com/shibingli/webconsole';")
    
    repos = cur.fetchall()
    cur.close()
    conn.close()

    print("Total number of searchrepos attempting: ", len(repos))
    
    for repo in repos:

        repo_data = {
            "_id": repo[0],
            "repo_url": repo[1],
            "license": repo[2],
            "language": repo[3],
            "licenseconflicts": repo[4],
            "is_active": repo[5]
        }
        
        if repo_data["is_active"] == True:
            repo_id=repo[0]

            repo_url=repo[1]
        
            print("Running SearchSECO analysis...")
            output = run_searchseco_check(repo_url)
            
            if not output:
                print("Failed to get analysis results")
                continue
            
            print("Parsing matches...")
            matches = parse_matches(output, repo_url, fun_code)
            
            if not matches:
                print("No matches found")
                continue
            
            print("Fetching function code and creating a dataframe...")
            df, input_project_id, input_project_version = create_dataFrame(matches, repo_url)
            #parse_csv(filename)

            df = check_license_compatibility(df)

            print("Saving results to CSV...")
            save_to_csv(df, repo_url, input_project_id, save_dir="results")
           
            conn = get_db_repos()
            cur = conn.cursor()
            cur.execute("UPDATE searchrepos SET is_active = %s, project_id = %s,  project_version = %s WHERE _id = %s;", (False, input_project_id, input_project_version, repo_id))
            conn.commit()
            cur.close()
            conn.close()
    
if __name__ == "__main__":
    main()
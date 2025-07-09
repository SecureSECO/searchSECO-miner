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
        df = df.sort_values(by=["Hash", "Version"])
        df = (
            df.groupby("Hash", group_keys=False)
            .apply(lambda g: pd.concat([
                g.head(1), 
                g[g["Query Project"] == "Yes"]
            ]).drop_duplicates())
            .reset_index(drop=True)
        )

        #df.to_csv("./results/data/"+str(project_version)+".csv")
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
    stat_count = [0,0,0,0,0,0]
    # Sorting by Version (timestamp) within each hash group
    df = df.sort_values(by=["Hash", "Version"])
    grouped = df.groupby("Hash")

    for function_hash, group in grouped:
        base_license = normalize_license(group.iloc[0]["License"])  # Normalize first row's license
        source_project_id = group.iloc[0]["Project ID"]
        source_project_version = group.iloc[0]["Version"]
        group_idx = group.index[0]

        if df.at[group_idx, "Query Project"] == "Yes":
            df.at[group_idx, "Violation"] = f"No match foucnd with the database"
            df.at[group_idx, "Query Project"] = "5"
            stat_count[5] = stat_count[5]+1
        

        for idx, row in group.iloc[1:].iterrows():
            if df.at[idx, "Query Project"] == "Yes":
                license_type = normalize_license(row["License"])
                if license_type not in LICENSE_LIST or base_license not in LICENSE_LIST:
                    df.at[idx, "Violation"] = "Undetermined"
                    df.at[idx, "Source_project"] = source_project_id
                    df.at[idx, "Source_project_version"] = source_project_version
                    df.at[group_idx, "Query Project"] = "4"
                    stat_count[4] = stat_count[4]+1
                elif license_type=="Proprietary_Unknown" or base_license=="Proprietary_Unknown":
                    df.at[idx, "Violation"] = f"{license_type} has high risk of conflicting with {base_license}"
                    df.at[idx, "Source_project"] = source_project_id
                    df.at[idx, "Source_project_version"] = source_project_version
                    df.at[group_idx, "Query Project"] = "3"
                    stat_count[3] = stat_count[3]+1
                elif base_license==license_type:
                    df.at[idx, "Violation"] = f"{license_type} same license {base_license}"
                    df.at[idx, "Source_project"] = source_project_id
                    df.at[idx, "Source_project_version"] = source_project_version
                    df.at[group_idx, "Query Project"] = "0"
                    stat_count[0] = stat_count[0]+1
                elif can_reuse_code(base_license, license_type):
                    df.at[idx, "Violation"] = f"{license_type} compatible with {base_license}"
                    df.at[idx, "Source_project"] = source_project_id
                    df.at[idx, "Source_project_version"] = source_project_version
                    df.at[group_idx, "Query Project"] = "1"
                    stat_count[1] = stat_count[1]+1
                elif not can_reuse_code(base_license, license_type):
                    df.at[idx, "Violation"] = f"{license_type} incompatible with {base_license}"
                    df.at[idx, "Source_project"] = source_project_id
                    df.at[idx, "Source_project_version"] = source_project_version
                    df.at[group_idx, "Query Project"] = "2"
                    stat_count[2] = stat_count[2]+1

    print("Incompatibility statistics: ", stat_count)

    return df, stat_count

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

    company_name = "Microsoft"  # provide organization name: Google, Microsoft etc.
    
    repos = get_search_repos(search_repo, company_name)
    
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
            
            print("Creating a dataframe...")
            df, input_project_id, input_project_version = create_dataFrame(matches, repo_url)

            
            print("Checking license compatibility...")

            # 0, no violation & same license
            # 1, no violation & different license
            # 2, conflicting or violated license
            # 3, has high risk of conflicting
            # 4, undetermined
            # 5, no violation query project is the source project
            
            df, stat_count = check_license_compatibility(df)
            
            print("Saving results to database...")
            
            update_process_time("processing_end_time", repo_id, repo_url)
            
            df = insert_into_rp_data(df, repo_id)

            #### Visual Inspection ####
            
            #print("Saving results to CSV...")
            save_to_csv(df, stat_count[2], stat_count[2], repo_url, input_project_id, save_dir="results")
            
            #### End Visual Inspection ####
            
            print("Updating the query table and exiting..")  #same_license, dif_license_comply, actual_violation, undetermined
            update_searchrepos(input_project_id, input_project_version, repo_id, stat_count[0], stat_count[1], stat_count[2], stat_count[3])
            
            
            

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


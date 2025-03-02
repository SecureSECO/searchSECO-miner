import pandas as pd
import os
import glob
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime
from urllib.parse import urlparse

# Get all CSV files in the current directory

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Define the results folder and new timestamped folder
results_folder = "../results"
gen_report = os.path.join(results_folder, timestamp)
os.makedirs(gen_report, exist_ok=True)

csv_files = glob.glob('../results/*.csv')
dfs = []

# Read and combine CSV files
for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file, encoding='utf-8', quoting=csv.QUOTE_MINIMAL)
        df['source_file'] = csv_file
        dfs.append(df)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

if not dfs:
    print("No CSV files were successfully read")
    exit()

# Combine all dataframes
combined_df = pd.concat(dfs, ignore_index=True)

# Extract repository name from URL
def extract_repo_info(url):
    if pd.isna(url):
        return "Unknown", url
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            return f"{path_parts[0]}/{path_parts[1]}", url
        return "Unknown", url
    except:
        return "Unknown", url

# Analysis function
def analyze_projects(df):
    results = {}
    
    # Group by Project ID
    project_groups = df.groupby('Project ID')
    
    for project_id, group in project_groups:
        # Get unique hashes
        unique_hashes = group['Hash'].unique()
        
        # Get unique hashes with violations
        violation_mask = (group['Violation'].notna()) & (group['Violation'] != "Undetermined")
        violation_hashes = group[violation_mask]['Hash'].unique()
        
        # Get source files for this project
        source_files = group['source_file'].unique()
        
        # Get repository info for this project
        repo_info = group['Repository URL'].iloc[0] if not group['Repository URL'].empty else None
        repo_name, repo_url = extract_repo_info(repo_info)
        
        if len(unique_hashes) > 1:  # Only store projects with multiple hashes
            results[project_id] = {
                'unique_hashes': list(unique_hashes),
                'hash_count': len(unique_hashes),
                'violation_hashes': list(violation_hashes),
                'violation_hash_count': len(violation_hashes),
                'violations': list(group[violation_mask]['Violation'].unique()),
                'source_files': list(source_files),
                'repository_name': repo_name,
                'repository_url': repo_url
            }
    
    return results

# Perform analysis
analysis_results = analyze_projects(combined_df)

# Create report
with open(gen_report+'/multiple_hashes_report.txt', 'w') as f:
    f.write("Projects with Multiple Hashes Analysis\n")
    f.write("===================================\n\n")
    
    f.write("1. Projects with Multiple Unique Hashes\n")
    f.write("-------------------------------------\n")
    for project_id, data in sorted(analysis_results.items(), 
                                 key=lambda x: x[1]['hash_count'], 
                                 reverse=True):
        f.write(f"\nProject ID: {project_id}\n")
        f.write(f"Source Files: {', '.join(data['source_files'])}\n")
        f.write(f"Total Unique Hashes: {data['hash_count']}\n")
        f.write("Unique Hashes:\n")
        f.write(", ".join(data['unique_hashes']) + "\n")
        f.write("-" * 50 + "\n")
    
    f.write("\n\n2. Projects with Multiple Violation Hashes\n")
    f.write("----------------------------------------\n")
    # Filter and sort projects with multiple violation hashes
    violation_projects = {k: v for k, v in analysis_results.items() 
                        if v['violation_hash_count'] > 1}
    
    for project_id, data in sorted(violation_projects.items(), 
                                 key=lambda x: x[1]['violation_hash_count'], 
                                 reverse=True):
        f.write(f"\nProject ID: {project_id}\n")
        f.write(f"Source Files: {', '.join(data['source_files'])}\n")
        f.write(f"Total Unique Hashes: {data['hash_count']}\n")
        f.write(f"Hashes with Violations: {data['violation_hash_count']}\n")
        f.write("Violation Hashes:\n")
        f.write(", ".join(data['violation_hashes']) + "\n")
        f.write("Violations Found:\n")
        f.write(", ".join(str(v) for v in data['violations']) + "\n")
        f.write("-" * 50 + "\n")

# Create visualizations
plt.figure(figsize=(15, 10))

# 1. Top Projects with Multiple Hashes
plt.subplot(2, 1, 1)
top_multiple_hashes = dict(sorted(
    {k: v['hash_count'] for k, v in analysis_results.items()}.items(),
    key=lambda x: x[1],
    reverse=True
)[:20])  # Changed to top 20

plt.bar(range(len(top_multiple_hashes)), list(top_multiple_hashes.values()))
plt.title('Top 20 Projects by Number of Unique Hashes')
plt.xlabel('Project ID')
plt.ylabel('Number of Unique Hashes')
plt.xticks(range(len(top_multiple_hashes)), list(top_multiple_hashes.keys()), rotation=45)

# 2. Top Projects with Multiple Violation Hashes
plt.subplot(2, 1, 2)
violation_projects = {k: v['violation_hash_count'] for k, v in analysis_results.items() 
                     if v['violation_hash_count'] > 1}
top_violation_hashes = dict(sorted(violation_projects.items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)[:20])  # Changed to top 20

if top_violation_hashes:
    plt.bar(range(len(top_violation_hashes)), list(top_violation_hashes.values()))
    plt.title('Top 20 Projects by Number of Violation Hashes')
    plt.xlabel('Project ID')
    plt.ylabel('Number of Violation Hashes')
    plt.xticks(range(len(top_violation_hashes)), list(top_violation_hashes.keys()), rotation=45)

plt.tight_layout()
plt.savefig(gen_report+'/multiple_hashes_analysis.png')
plt.close()

# Save summary as CSV with repository information
summary_df = pd.DataFrame([
    {
        'Project ID': k,
        'Repository': v['repository_name'],
        'Repository URL': v['repository_url'],
        'Source Files': '; '.join(v['source_files']),
        'Total Unique Hashes': v['hash_count'],
        'Violation Hashes': v['violation_hash_count'],
        'Has Multiple Violations': v['violation_hash_count'] > 1
    }
    for k, v in analysis_results.items()
]).sort_values(['Has Multiple Violations', 'Violation Hashes', 'Total Unique Hashes'], 
               ascending=[False, False, False])

summary_df.to_csv(gen_report+'/multiple_hashes_summary.csv', index=False)

print("Analysis complete! Check:")
print("1. multiple_hashes_report.txt - Detailed analysis of projects with multiple hashes")
print("2. multiple_hashes_summary.csv - Summary statistics for each project")
print("3. multiple_hashes_analysis.png - Visualizations of the analysis")
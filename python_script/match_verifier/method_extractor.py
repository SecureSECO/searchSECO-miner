import pandas as pd
import requests
import re
import io
import os

def get_indentation(line):
    return len(line) - len(line.lstrip(' '))

def extract_python_method(code_lines, start_line_num):
    start_line_index = start_line_num - 1
    if start_line_index >= len(code_lines):
        return "Error: Start line number is out of the file's bounds."

    # The line number should point to the 'def' statement.
    first_line_of_method = code_lines[start_line_index]
    
    # Check if this line actually contains a method definition
    if 'def ' not in first_line_of_method and 'class ' not in first_line_of_method:
        return f"Error: Line {start_line_num} does not contain a method or class definition: {first_line_of_method.strip()}"
    
    initial_indentation = get_indentation(first_line_of_method)
    method_code = [first_line_of_method]

    # Iterate through subsequent lines to find the method's body.
    for i in range(start_line_index + 1, len(code_lines)):
        line = code_lines[i]
        
        # Preserve empty lines within the method for accurate representation.
        if not line.strip():
            method_code.append(line)
            continue

        current_indentation = get_indentation(line)
        
        # A line with more indentation is part of the method.
        if current_indentation > initial_indentation:
            method_code.append(line)
        else:
            # A line with same or less indentation marks the end of the method.
            break
            
    return "\n".join(method_code)

def extract_c_like_method(code_lines, start_line_num):
    """
    Extracts a complete C-like (C++, Java, etc.) method based on finding
    a balanced set of curly braces {}.
    """
    start_line_index = start_line_num - 1
    if start_line_index >= len(code_lines):
        return "Error: Start line number is out of the file's bounds."

    method_code = []
    brace_balance = 0
    method_started = False
    first_line = code_lines[start_line_index]

    # Check if this line looks like a method/function definition
    if not any(keyword in first_line for keyword in ['{', '(', 'void', 'int', 'char', 'bool', 'float', 'double', 'class', 'struct']):
        return f"Error: Line {start_line_num} does not appear to be a method definition: {first_line.strip()}"

    # Iterate from the starting line to the end of the file.
    for i in range(start_line_index, len(code_lines)):
        line = code_lines[i]
        method_code.append(line)
        
        # This is a simplified parser and does not account for braces
        # inside comments or string literals.
        brace_balance += line.count('{')
        brace_balance -= line.count('}')

        if brace_balance > 0:
            method_started = True
        
        # When the braces are balanced, we've found the end of the method.
        if method_started and brace_balance == 0:
            break
            
    return "\n".join(method_code)

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


def process_code_extraction(input_filepath, output_filepath):
    """
    Reads the source CSV using pandas, processes rows with 'granular_level_reached' of 4,
    extracts the corresponding methods from GitHub, and writes the results
    to a new CSV file.
    """
    print(f"Starting the processing of {input_filepath}...")
    
    EXTRACTORS = {
        'py': extract_python_method,
        'python': extract_python_method,
        'cpp': extract_c_like_method,
        'c': extract_c_like_method,
        'java': extract_c_like_method,
        'js': extract_c_like_method,
        'javascript': extract_c_like_method,
        'cs': extract_c_like_method,
        'csharp': extract_c_like_method,
    }

    try:
        df = pd.read_csv(input_filepath)
        print(f"Loaded {len(df)} rows from CSV")

        df["Language"] = df["file_location"].apply(detect_language)

        # Work only on granular_level 4
        granular_4_df = df[df['granular_level_reached'] == 4].copy()
        print(f"Found {len(granular_4_df)} entries with granular level 4")

        if granular_4_df.empty:
            print("No granular level 4 entries found. Exiting.")
            return

        # Add a new column to hold extracted code
        granular_4_df["extracted_method_code"] = None

        for idx, row in granular_4_df.iterrows():
            repo_url = row['repository_url']
            language = row['Language']
            print(f"Processing row {idx+2}: {repo_url}")

            try:
                # Repo name
                repo_name_match = re.search(r'github\.com/([^/]+/[^/]+)', repo_url)
                repo_name = repo_name_match.group(1) if repo_name_match else 'unknown_repo'

                # Extract line number
                line_num_match = re.search(r'#L(\d+)$', repo_url)
                if not line_num_match:
                    print(f"  -> Warning: Could not find line number in URL. Skipping.")
                    continue
                start_line_num = int(line_num_match.group(1))

                # Convert to raw file URL
                raw_content_url = repo_url.split('#')[0]
                raw_content_url = raw_content_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")

                # Download file content
                response = requests.get(raw_content_url, timeout=30)
                response.raise_for_status()
                code_lines = response.text.splitlines()

                # Extract method
                extractor_func = EXTRACTORS.get(language.lower())
                if extractor_func:
                    extracted_code = extractor_func(code_lines, start_line_num)
                    granular_4_df.at[idx, "extracted_method_code"] = extracted_code
                    print(f"  -> Successfully extracted method")
                else:
                    print(f"  -> Warning: No extractor for language '{language}'")

            except requests.exceptions.RequestException as e:
                print(f"  -> Error fetching URL {repo_url}: {e}")
            except Exception as e:
                print(f"  -> Unexpected error: {e}")

        # Save enriched dataframe
        granular_4_df.to_csv(output_filepath, index=False, encoding="utf-8")
        df_sorted = granular_4_df.sort_values(by=["hash", "project_id", "version"])

        granular_4_df = (
            df_sorted.groupby("hash")                    # group only by hash
            .filter(lambda g: len(g) > 1)                # keep only duplicates
            .groupby("hash")
            .apply(lambda g: g.iloc[[0, -1]])            # take first & last row
            .reset_index(drop=True)
        )
        print(f"\nSuccessfully extracted methods for {granular_4_df['extracted_method_code'].notna().sum()} rows")

    except FileNotFoundError:
        print(f"Error: The input file '{input_filepath}' was not found.")
    except Exception as e:
        print(f"A critical error occurred: {e}")

    print(f"\nProcessing finished. Output is saved to {output_filepath}")


if __name__ == '__main__':

    input_csv = 'trivial_sample_output.csv'
    output_csv = 'extracted_methods.csv'
    
    process_code_extraction(input_csv, output_csv)


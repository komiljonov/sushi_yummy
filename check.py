import os
import re
import json


# Function to find i18n calls in a given Python file
def find_i18n_calls_in_file(file_path):
    i18n_calls = []
    # Regular expression to capture i18n.<key>.<subkey> calls
    pattern = re.compile(r"i18n\.[a-zA-Z_][a-zA-Z_0-9]*(?:\.[a-zA-Z_][a-zA-Z_0-9]*)+")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        matches = pattern.findall(content)
        i18n_calls.extend(matches)
    return i18n_calls


# Function to search for i18n calls in all .py files in a project
def search_project_for_i18n_calls(project_dir):
    i18n_calls = set()  # Use a set to avoid duplicates
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                calls = find_i18n_calls_in_file(file_path)
                i18n_calls.update(calls)
    return i18n_calls


# Function to load JSON files and return nested keys
def load_json_keys(json_file):
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    return extract_nested_keys(data)


# Function to extract nested keys from JSON recursively
def extract_nested_keys(data, prefix=""):
    keys = []
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            keys.extend(extract_nested_keys(value, full_key))
        else:
            keys.append(full_key)
    return keys


# Function to check for missing i18n keys in JSON files
def check_missing_keys(i18n_calls, json_keys):
    missing_keys = []
    for call in i18n_calls:
        json_key = call.replace("i18n.", "")
        if json_key not in json_keys:
            missing_keys.append(call)
    return missing_keys


# Function to dynamically load all JSON files in the locales directory
def load_all_json_files(locales_dir):
    json_files = []
    for root, _, files in os.walk(locales_dir):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files


def main():
    # Step 1: Extract all i18n calls from the Python project
    project_dir = "tg_bot"  # Replace with your Django project directory
    i18n_calls = search_project_for_i18n_calls(project_dir)

    # Step 2: Load all JSON files dynamically from the locales folder
    locales_dir = "locales"  # Replace with your locales folder
    json_files = load_all_json_files(locales_dir)

    for json_file in json_files:
        print(f"Checking {json_file}...")
        json_keys = load_json_keys(json_file)

        # Step 3: Check for missing keys in the current JSON file
        missing_keys = check_missing_keys(i18n_calls, json_keys)

        # Step 4: Output results
        if missing_keys:
            print(f"Missing keys in {json_file}:")
            for key in missing_keys:
                print(f"  {key}")
        else:
            print(f"No missing keys in {json_file}.")


if __name__ == "__main__":
    main()

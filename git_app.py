import requests
import os

def fetch_diff(repo_name, pr_number, github_token):
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
    headers = {"Authorization": f"token {github_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [
            {
                "filename": file["filename"],
                "patch": file.get("patch", ""),
                "raw_url": file["raw_url"]
            }
            for file in response.json()
        ]
    return []

def commit_to_existing_pr(repo, pr_number, files, commit_message, github_token):
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}
    
    # Rest of the function remains the same but use parameters instead of hardcoded values
    # (Keep the same logic but remove any hardcoded credentials)
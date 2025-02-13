import os
import requests
from ai_app import ai_verify
from git_app import fetch_diff

def add_github_pr_comment(owner, repo, pr_number, commit_id, file_path, comments, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    
    for comment in comments:
        payload = {
            "body": comment["comment"],
            "commit_id": commit_id,
            "path": file_path,
            "line": comment["line_number"],
            "side": "RIGHT",
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201:
            print(f"Error commenting: {response.text}")

def get_pr_details(owner, repo, pr_number, token):
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = requests.get(pr_url, headers={"Authorization": f"token {token}"})
    pr_data = response.json()
    
    return {
        "commit_id": pr_data["head"]["sha"],
        "files": fetch_diff(f"{owner}/{repo}", pr_number, token)
    }

def main():
    owner, repo = os.getenv("GITHUB_REPOSITORY").split("/")
    pr_number = int(os.getenv("GITHUB_PR_NUMBER"))
    token = os.getenv("GITHUB_TOKEN")
    
    details = get_pr_details(owner, repo, pr_number, token)
    
    for file_info in details["files"]:
        content = requests.get(file_info["raw_url"]).text
        comments = ai_verify(content)
        
        add_github_pr_comment(
            owner=owner,
            repo=repo,
            pr_number=pr_number,
            commit_id=details["commit_id"],
            file_path=file_info["filename"],
            comments=comments,
            token=token
        )

if __name__ == "__main__":
    main()
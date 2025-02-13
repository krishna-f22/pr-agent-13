import requests
from ai_app import ai_verify


def add_github_pr_comment(owner, repo, pr_number, commit_id, file_path, comments, token):

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"

    for comment in comments:
        headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "body": comment["comment"],
            "commit_id": commit_id,
            "path": file_path,
            "line": comment["line_number"],
            "side": "RIGHT",
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            print(f"Comment on line number {comment["line_number"]} added successfully!")
        else:
            print(f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")


owner = "SaisaranF22"
repo = "test-app"
token = "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"


def get_latest_pr_info(owner, repo, token):
    headers = {"Authorization": f"token {token}"}

    # Get the latest PR
    prs_url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=open&sort=created&direction=desc"
    response = requests.get(prs_url, headers=headers)
    response.raise_for_status()
    prs = response.json()

    if not prs:
        print("No open PRs found.")
        return

    latest_pr = prs[0]  # Most recent PR
    pr_number = latest_pr["number"]

    # Get commits of the latest PR
    commits_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
    response = requests.get(commits_url, headers=headers)
    print(response)
    # response.raise_for_status()
    commits = response.json()

    commit_ids = [commit["sha"] for commit in commits]

    # Get changed files
    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    response = requests.get(files_url, headers=headers)
    response.raise_for_status()
    files = response.json()
    f_names = []
    file_data = {}
    for file in files:
        filename = file["filename"]
        f_names.append(filename)
        raw_url = file["raw_url"]
        raw_url = raw_url.replace("github.com", "raw.githubusercontent.com").replace("/raw/", "/")
        print(raw_url)
        file_response = requests.get(raw_url, headers=headers)
        print(f_names, file_response.text[:500])
        file_response.raise_for_status()
        file_data[filename] = file_response.text

    return {"pr_number": pr_number, "commit_ids": commit_ids[0], "files": file_data, "filenames": f_names}


def app(owner, repo, token):
    pr_details = get_latest_pr_info(owner, repo, token)

    for file_name in pr_details["filenames"]:

        comments = ai_verify(pr_details["files"][file_name])
        print(comments)
        # print(pr_details["files"][file_name])
        add_github_pr_comment(
            owner=owner,
            repo=repo,
            token=token,
            commit_id=pr_details["commit_ids"],
            file_path=file_name,
            comments=comments,
            pr_number=pr_details["pr_number"],
        )


print(app(owner, repo, token))

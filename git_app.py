import requests
import os

# GITHUB_TOKEN = "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"
GITHUB_TOKEN = "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"
OWNER = "SaisaranF22"
REPO = "AI"
PR_NUMBER = 7


def fetch_diff(repo_name, pr_number):
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        files = response.json()
        f_name = []
        for file in files:
            filename = file["filename"]
            patch = file.get("patch")
            f_name.append(filename)
            if patch:
                # Create a folder for saving diffs if it doesn't exist
                os.makedirs("pr_diffs", exist_ok=True)

                # Save the diff for each file into a separate file
                with open(f"pr_diffs/{filename}", "w") as diff_file:
                    diff_file.write(patch)

                return f_name
            else:
                print(f"No diff found for {filename}.")
    else:
        print(f"Failed to fetch files: {response.status_code} - {response.reason}")


def commit_to_existing_pr(repo, pr_number, files, commit_message, github_token):
    headers = {"Authorization": f"token {github_token}", "Accept": "application/vnd.github.v3+json"}

    # Step 1: Get the PR details to find the branch name
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    pr_resp = requests.get(pr_url, headers=headers)

    if pr_resp.status_code != 200:
        print(f"Error fetching PR details: {pr_resp.json()}")
        return

    pr_data = pr_resp.json()
    branch_name = pr_data["head"]["ref"]
    base_sha = pr_data["head"]["sha"]

    # Step 2: Get latest commit tree SHA
    commit_url = f"https://api.github.com/repos/{repo}/git/commits/{base_sha}"
    commit_resp = requests.get(commit_url, headers=headers)

    if commit_resp.status_code != 200:
        print(f"Error fetching commit: {commit_resp.json()}")
        return

    commit_data = commit_resp.json()
    tree_sha = commit_data["tree"]["sha"]

    # Step 3: Create blobs for new files
    blobs = []
    for filename, content in files.items():
        blob_url = f"https://api.github.com/repos/{repo}/git/blobs"
        blob_data = {"content": content, "encoding": "utf-8"}
        blob_resp = requests.post(blob_url, json=blob_data, headers=headers)

        if blob_resp.status_code != 201:
            print(f"Error creating blob for {filename}: {blob_resp.json()}")
            return

        blob_sha = blob_resp.json()["sha"]
        blobs.append({"path": filename, "mode": "100644", "type": "blob", "sha": blob_sha})

    # Step 4: Create a new tree with file changes
    tree_url = f"https://api.github.com/repos/{repo}/git/trees"
    tree_data = {"base_tree": tree_sha, "tree": blobs}
    tree_resp = requests.post(tree_url, json=tree_data, headers=headers)

    if tree_resp.status_code != 201:
        print(f"Error creating tree: {tree_resp.json()}")
        return

    new_tree_sha = tree_resp.json()["sha"]

    # Step 5: Create a commit with the new tree
    commit_data = {"message": commit_message, "tree": new_tree_sha, "parents": [base_sha]}
    commit_resp = requests.post(f"https://api.github.com/repos/{repo}/git/commits", json=commit_data, headers=headers)

    if commit_resp.status_code != 201:
        print(f"Error creating commit: {commit_resp.json()}")
        return

    new_commit_sha = commit_resp.json()["sha"]

    # Step 6: Update the PR branch reference
    ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{branch_name}"
    ref_resp = requests.patch(ref_url, json={"sha": new_commit_sha}, headers=headers)

    if ref_resp.status_code == 200:
        print("Changes committed successfully to existing PR.")
    else:
        print(f"Error updating branch ref: {ref_resp.json()}")




# Example usage
# commit_to_existing_pr(
#     repo="SaisaranF22/AI",
#     pr_number=PR_NUMBER,
#     files={"cal.py": "Updated content"},
#     commit_message="Updated cal.py in existing PR",
#     github_token=GITHUB_TOKEN,
# )


# print(fetch_diff(repo_name="SaisaranF22/AI", pr_number=7))

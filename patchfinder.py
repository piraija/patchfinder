import sys
import argparse
import requests

def get_user_repos(username, headers):
    """
    Retrieves the public repositories of a given GitHub user.

    Args:
        username (str): GitHub username.
        headers (dict): Request headers for API authentication.

    Returns:
        list or None: List of public repositories if successful, None otherwise.
    """
    url = f"https://api.github.com/users/{username}/repos"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        repositories = response.json()
        return repositories

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting the user's public repositories: {e}")
        return None

def get_repo_commits(username, repo_name, headers):
    """
    Retrieves the commits for a given repository.

    Args:
        username (str): GitHub username.
        repo_name (str): Repository name.
        headers (dict): Request headers for API authentication.

    Returns:
        list or None: List of commits for the repository if successful, None otherwise.
    """
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"

    try:
        response = requests.get(commits_url, headers=headers)
        response.raise_for_status()
        commits = response.json()
        return commits

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting a commit: {e}")
        return None

def get_commit_patch(commit_url, headers):
    """
    Retrieves the patch content for a given commit URL.

    Args:
        commit_url (str): URL of the commit.
        headers (dict): Request headers for API authentication.

    Returns:
        str or None: The patch line containing the 'From' field as a string if successful, None otherwise.
    """
    try:
        response = requests.get(commit_url + ".patch", headers=headers)
        response.raise_for_status()
        patch_lines = response.text.strip().split("\n")
        if len(patch_lines) > 1:
            return patch_lines[1] # 'From' field is on the second line of the patch

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while requesting a patch: {e}")
        return None

def search_all_patches(username, headers):
    """
    Searches through all commit patches of the given GitHub username's repositories to identify unique contributors.

    Args:
        username (str): GitHub username to search for.
        headers (dict): Request headers for API authentication.

    Returns:
        set: Set of unique commit patches containing emails.
    """
    repos = get_user_repos(username, headers)
    if repos is None:
        print("User has no public repositories.")
        sys.exit(1)

    unique_patches = set()  # Store unique contributors

    for repo in repos:
        repo_name = repo["name"]
        #repo_url = repo["html_url"]

        commits = get_repo_commits(username, repo_name, headers)
        if commits is None:
            continue

        for commit in commits:
            commit_url = commit["html_url"]
            patch = get_commit_patch(commit_url, headers)
            if patch is not None:
                if patch.startswith("From: "): # Remove leading 'From: '
                    patch = patch[6:]
                if patch not in unique_patches:  # Check for uniqueness
                    unique_patches.add(patch)  # Add contributor to set
                    print(patch)
    return unique_patches

def search_patches_for_email(username, headers, email):
    """
    Searches through commit patches of the given GitHub username's repositories to find commits leaking a specific email address.

    Args:
        username (str): GitHub username to search for.
        headers (dict): Request headers for API authentication.
        email (str): Email address to search for in commit patches.

    Returns:
        list: List of dictionaries containing repository and commit information.
    """
    repos = get_user_repos(username, headers)
    if repos is None:
        print("User has no public repositories.")
        sys.exit(1)

    results = []

    for repo in repos:
        repo_name = repo["name"]
        repo_url = repo["html_url"]
        commits = get_repo_commits(username, repo_name, headers)

        if commits is None:
            continue

        for commit in commits:
            commit_url = commit["html_url"]
            patch = get_commit_patch(commit_url, headers)
            if patch is not None and email in patch:
                result = {
                    "repository": repo_name,
                    "commit_url": commit_url
                }
                results.append(result)
                print(f"Repository: {repo_name}")
                print(f"Commit URL: {commit_url}")
                print()
    return results

def print_patchfinder_header():
    header = r'''
--------------------------------------------------------------------------------------------------
     ██▓███   ▄▄▄     ▄▄▄█████▓ ▄████▄   ██░ ██   █████▒██▓ ███▄    █ ▓█████▄ ▓█████  ██▀███  
    ▓██░  ██▒▒████▄   ▓  ██▒ ▓▒▒██▀ ▀█  ▓██░ ██▒▓██   ▒▓██▒ ██ ▀█   █ ▒██▀ ██▌▓█   ▀ ▓██ ▒ ██▒
    ▓██░ ██▓▒▒██  ▀█▄ ▒ ▓██░ ▒░▒▓█    ▄ ▒██▀▀██░▒████ ░▒██▒▓██  ▀█ ██▒░██   █▌▒███   ▓██ ░▄█ ▒
    ▒██▄█▓▒ ▒░██▄▄▄▄██░ ▓██▓ ░ ▒▓▓▄ ▄██▒░▓█ ░██ ░▓█▒  ░░██░▓██▒  ▐▌██▒░▓█▄   ▌▒▓█  ▄ ▒██▀▀█▄  
    ▒██▒ ░  ░ ▓█   ▓██▒ ▒██▒ ░ ▒ ▓███▀ ░░▓█▒░██▓░▒█░   ░██░▒██░   ▓██░░▒████▓ ░▒████▒░██▓ ▒██▒
    ▒▓▒░ ░  ░ ▒▒   ▓▒█░ ▒ ░░   ░ ░▒ ▒  ░ ▒ ░░▒░▒ ▒ ░   ░▓  ░ ▒░   ▒ ▒  ▒▒▓  ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
    ░▒ ░       ▒   ▒▒ ░   ░      ░  ▒    ▒ ░▒░ ░ ░      ▒ ░░ ░░   ░ ▒░ ░ ▒  ▒  ░ ░  ░  ░▒ ░ ▒░
    ░░         ░   ▒    ░      ░         ░  ░░ ░ ░ ░    ▒ ░   ░   ░ ░  ░ ░  ░    ░     ░░   ░ 
                   ░  ░        ░ ░       ░  ░  ░        ░           ░    ░       ░  ░   ░     
                               ░                                       ░                      
 Search a GitHub user's repositories' commit patches to identify unique names and email addresses
--------------------------------------------------------------------------------------------------
'''
    print(header)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patchfinder: Search a GitHub user's repositories' commit patches to identify unique names and email addresses.")
    parser.add_argument("username", help="GitHub username whose repositories' commit patches will be searched.")
    parser.add_argument("api_token", help="GitHub API token for REST API.")
    parser.add_argument("--search-email", metavar="EMAIL", help="Search for and return commit patches that leak a specific email address.")
    
    args = parser.parse_args()
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {args.api_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    print_patchfinder_header() # This line is probably OK to remove. Results from testing show that commenting out this line returns objetively worse results.
    if args.search_email:
        search_patches_for_email(args.username, headers, args.search_email)
    else:
        search_all_patches(args.username, headers)


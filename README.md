# Patchfinder

## Background
Git commit patches contain a wealth of information, including metadata, code changes, and commit messages. In some cases, these patches may inadvertently include information that was not intended to be made public, such as full names, private or corporate email addresses. This can occur when developers forget that they have configured git to use their full name and/or private/corporate email.

This can be leveraged to harvest corporate emails for phishing campaigns, dox developers or contributors associated with a project, or uncover email formats used within an organization. By systematically analyzing commit patches, attackers can gather intelligence and potentially target individuals or organizations for malicious purposes.

Patchfinder aims to address these concerns by providing a convenient way to search for and identify commit patches that may contain unintentionally disclosed email addresses. By being aware of these potential vulnerabilities, users can take appropriate steps to review and secure their commit history, ensuring sensitive information is not exposed.

## Description
Patchfinder is a Python script that allows you to search through commit patches of GitHub repositories to identify unique names and email addresses. It provides two main functionalities:

1. Search a GitHub user's repositories' commit patches to identify unique names and email addresses.
2. Search a GitHub user's repositories' and return commit patches that leak a specific email address.

## Usage
    ```
    python patchfinder.py <username> <api_token> [--search-email <email>]
    ```
`<username>`: GitHub username whose repositories' commit patches will be searched.

`<api_token>`: GitHub API token for REST API.

Include the `--search-email` flag followed by the email address you want to search for (for example your own private email address to figure out if you have leaked it).

## Avoiding Email Exposure in Git Commit Patches
To avoid exposing your private details in Git commit patches, consider the following:

- Configure your Git client to use a generic name and email address, or a pseudonym and email address not associated with your private details.

    - `git config user.email public-email@example.com`

    - `git config user.name pseudonym`

If you have already disclosed something private and wish to remove it, tough luck; it is on the Internet. 

## Disclaimer

Patchfinder is intended for legitimate security research and educational purposes only. By using this tool, you acknowledge that you understand the ethical implications of accessing and analyzing commit patches. It is important to use Patchfinder responsibly and ethically, respecting the privacy and security of individuals and organizations.

Patchfinder should not be used for any malicious, illegal, or unethical activities.

import os
import requests

def fetch_dependabot_prs(token, repos):
    """Fetch Dependabot PRs from specified GitHub repositories."""
    headers = {"Authorization": f"Bearer {token}"}
    dependabot_prs = []

    for repo in repos.split(","):
        url = f"https://api.github.com/repos/{repo}/pulls"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        for pr in response.json():
            # if "dependabot" in pr.get("user", {}).get("login", ""):
            dependabot_prs.append({
                "repo": repo,
                "title": pr["title"],
                "url": pr["html_url"]
            })
    return dependabot_prs

def send_to_slack(webhook_url, prs):
    """Send the Dependabot PRs to Slack."""
    if prs:
        message = "*📢 Dependabot PRs:*"
        for pr in prs:
            message += f"\n- *{pr['repo']}*: <{pr['url']}|{pr['title']}>"
    else:
        message = "No Dependabot PRs found."

    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()

if __name__ == "__main__":
    # Fetch environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    repositories = os.getenv("REPOSITORIES")

    print("Fetching Dependabot PRs...")
    print(repositories)
    # Fetch Dependabot PRs and send to Slack
    prs = fetch_dependabot_prs(github_token, repositories)
    send_to_slack(slack_webhook_url, prs)

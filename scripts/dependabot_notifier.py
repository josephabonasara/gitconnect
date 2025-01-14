import os
import requests
from flask import Flask, request, jsonify

# Flask app to listen for Slack events
app = Flask(__name__)

# A simple mapping to track Slack messages and PRs
message_to_pr_map = {}

def fetch_dependabot_prs(token, repos):
    """Fetch Dependabot PRs from specified GitHub repositories."""
    headers = {"Authorization": f"Bearer {token}"}
    dependabot_prs = []

    for repo in repos.split(","):
        url = f"https://api.github.com/repos/{repo}/pulls"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        for pr in response.json():
            # Filter Dependabot PRs by checking user login
            # if "dependabot" in pr.get("user", {}).get("login", ""):
                dependabot_prs.append({
                    "repo": repo,
                    "title": pr["title"],
                    "url": pr["html_url"],
                    "number": pr["number"]
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

    # Debug: Print response details
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    response.raise_for_status()  # Raise HTTP errors

    try:
        response_data = response.json()  # Attempt to decode JSON
    except ValueError:
        print("Slack returned a non-JSON response.")
        response_data = {}

    return response_data

def merge_pull_request(github_token, repo, pr_number):
    """Merge a pull request using the GitHub API."""
    headers = {"Authorization": f"Bearer {github_token}"}
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/merge"
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        print(f"Successfully merged PR #{pr_number} in {repo}")
    else:
        print(f"Failed to merge PR #{pr_number} in {repo}: {response.text}")

@app.route("/slack/events", methods=["POST"])
def slack_event_handler():
    """Handle Slack events and respond to verification challenges."""
    event_data = request.json

    # Respond to the challenge request
    if "challenge" in event_data:
        return jsonify({"challenge": event_data["challenge"]})

    # Handle reaction events (same as before)
    if "event" in event_data:
        event = event_data["event"]

        if event["type"] == "reaction_added":
            reaction = event["reaction"]
            ts = event["item"]["ts"]

            # Check if the reaction is ✅ and the message is tracked
            if reaction == "white_check_mark" and ts in message_to_pr_map:
                pr = message_to_pr_map[ts]
                github_token = os.getenv("GITHUB_TOKEN")
                merge_pull_request(github_token, pr["repo"], pr["number"])

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Fetch environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    repositories = os.getenv("REPOSITORIES")

    print("Fetching Dependabot PRs...")
    prs = fetch_dependabot_prs(github_token, repositories)
    send_to_slack(slack_webhook_url, prs)

    # Start the Flask app to listen for Slack events
    app.run(port=3000)

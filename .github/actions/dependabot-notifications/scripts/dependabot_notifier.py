import os
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_dependabot_prs(token, repos):
    """Fetch Dependabot PRs from specified GitHub repositories."""
    headers = {"Authorization": f"Bearer {token}"}
    dependabot_prs = []

    for repo in repos:
        url = f"https://api.github.com/repos/{repo}/pulls"
        logger.info(f"Fetching PRs from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        for pr in response.json():
            if "dependabot" in pr.get("user", {}).get("login", ""):
                dependabot_prs.append({
                    "repo": repo,
                    "title": pr["title"],
                    "url": pr["html_url"]
                })
    return dependabot_prs

def send_to_slack(token, channel, prs):
    """Send the Dependabot PRs to Slack in a thread."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Post the main message to the channel
    main_message = {
        "channel": channel,
        "text": "*📢 Dependabot PRs:*"
    }
    response = requests.post("https://slack.com/api/chat.postMessage", json=main_message, headers=headers)
    response_data = response.json()
    response.raise_for_status()

    if not response_data.get("ok"):
        logger.error(f"Failed to send message to Slack: {response_data}")
        raise Exception(f"Failed to send message to Slack: {response_data}")

    thread_ts = response_data["ts"]  # Timestamp of the main message

    # Post each PR as a threaded reply
    for pr in prs:
        thread_message = {
            "channel": channel,
            "text": (
                f"*🔹 Repository:* {pr['repo']}\n"
                f"➡️ *Title:* {pr['title']}\n\n"
                f"{pr['url']}\n\n"
                f"------------------------------"  # Visual divider for separation
            ),
            "thread_ts": thread_ts
        }
        thread_response = requests.post("https://slack.com/api/chat.postMessage", json=thread_message, headers=headers)
        thread_response_data = thread_response.json()
        thread_response.raise_for_status()

        if not thread_response_data.get("ok"):
            logger.error(f"Failed to send threaded message to Slack: {thread_response_data}")
            raise Exception(f"Failed to send threaded message to Slack: {thread_response_data}")

if __name__ == "__main__":
    # Fetch environment variables
    github_token = os.getenv("GITHUB_TOKEN")
    slack_token = os.getenv("SLACK_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL", "#dependabot-notifications")

    # Parse repositories from environment variable
    repositories = json.loads(os.getenv("REPOSITORIES", "[]"))

    logger.info("Fetching Dependabot PRs...")
    prs = fetch_dependabot_prs(github_token, repositories)

    if prs:
        send_to_slack(slack_token, slack_channel, prs)
        logger.info("Dependabot PR notifications sent successfully.")
    else:
        logger.info("No Dependabot PRs found.")

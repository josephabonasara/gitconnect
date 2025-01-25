# Notify Dependabot PRs - GitHub Action

This GitHub Action allows you to send Dependabot PR notifications to a Slack channel. It fetches Dependabot pull requests from specified repositories and posts them in a Slack channel, including threading replies for each PR.

## Features
- Fetches Dependabot PRs from one or more GitHub repositories.
- Sends a notification to a Slack channel with details of the PRs.
- Posts each PR in a thread under a main message for better organization.

---

## Requirements
1. **Slack Bot Token**: A Slack bot with permissions to post messages in the channel.
2. **GitHub Personal Access Token (PAT)**: For fetching PR details from GitHub (optional if `GITHUB_TOKEN` is sufficient).
3. **Python Environment**: The Action uses Python 3.12 for running the notification script.

---

## Setting Up a Slack Bot
To enable posting messages to Slack, you need a bot token (`xoxb-...`) with the appropriate permissions.

### Step 1: Create a Slack App
1. Go to the [Slack API Apps Page](https://api.slack.com/apps).
2. Click **"Create New App"**.
3. Choose **"From scratch"** and provide a name for your app.
4. Select your Slack workspace.

### Step 2: Add Permissions to the App
1. In your app's settings, navigate to **OAuth & Permissions**.
2. Add the following **Bot Token Scopes**:
   - `chat:write` (Send messages as the bot).
   - `channels:read` (List public channels).
   - `groups:read` (Access private channels, if needed).
3. Install the app in your workspace by clicking **Install to Workspace**.

### Step 3: Obtain the Bot Token
1. After installing the app, go to the **OAuth & Permissions** section.
2. Copy the **Bot User OAuth Token** (starts with `xoxb-`).
3. Save this token as a repository secret named `SLACK_TOKEN`.

---

## GitHub Repository Setup
1. **Add Secrets**:
   - `SLACK_TOKEN`: The Slack bot token created above.
   - `GITHUB_TOKEN`: The default GitHub Actions token (already available in most workflows).
2. **Optionally**:
   - Add a `PAT` if accessing private repositories outside of the organization.

---

## Action Inputs
| Input             | Description                                                                         | Required |
|-------------------|-------------------------------------------------------------------------------------|----------|
| `slack-token`     | Slack bot token for sending messages.                                              | Yes      |
| `github-token`    | GitHub token to fetch Dependabot PRs.                                              | Yes      |
| `slack-channel`   | Slack channel to post messages. Example: `#dependabot-notifications`.               | Yes      |
| `repositories`    | JSON array of repositories to monitor. Example: `["org/repo1", "org/repo2"]`. | Yes      |

---

## Using the Action

### Example Workflow
Create a workflow file in `.github/workflows/dependabot-notifications.yml`:

```yaml
name: Notify Dependabot PRs

on:
    workflow_dispatch:
    schedule:
      - cron: "0 12 * * *"

jobs:
    notify-dependabot-prs:
      runs-on: ubuntu-latest
      steps:
        - name: Notify Dependabot PRs
          uses: josephabonasara/gitconnect/.github/actions/dependabot-notifications@main
          with:
            slack-token: ${{ secrets.SLACK_TOKEN }}
            github-token: ${{ secrets.GITHUB_TOKEN }}
            slack-channel: "#dependabot-notifications" # your slack channel name
            repositories: | # your repositories
            [
                "dependabot/dependabot-core",
                "your-org/another-repo",
                "example/example-repo"
            ]
```

---

## How It Works
1. The Action fetches open PRs for the specified repositories.
2. It identifies PRs created by Dependabot.
3. Sends a main notification message to the specified Slack channel.
4. Posts each Dependabot PR in a threaded reply under the main message.

---

## Debugging
- Ensure your Slack bot is added to the desired channel using the `/invite` command.
---

## Contributing
Feel free to submit issues and pull requests to enhance this Action.

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.


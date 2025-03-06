# GitHub Events Fivetran Connector

This connector fetches public events from GitHub repositories and loads them into your data warehouse using Fivetran's Connector SDK.

## Features

- Monitors multiple GitHub repositories (configurable)
- Captures event details including:
  - Event ID
  - Event payload
  - Creation timestamp
  - Repository identifier
- Uses Fivetran's infrastructure for reliable data syncing

## Prerequisites

- Python 3.x
- Fivetran account
- GitHub access (token optional for public repos)

## Installation

1. Install required packages:
```bash
pip install fivetran-connector-sdk requests
```

2. Configure your repositories in `configuration.json`:
```json
{
    "repo_list": "owner1/repo1,owner2/repo2",
    "github_token": ""
}
```

## Configuration

### Required Settings

- `repo_list`: Comma-separated list of repositories in the format "owner/repo"
  - Example: `"apache/spark,microsoft/vscode"`

### Optional Settings

- `github_token`: GitHub Personal Access Token for increased rate limits
  - Leave empty for public repositories
  - Required for private repositories

## Schema

The connector creates a single table named `github_events` with the following columns:

- `event_id` (STRING, Primary Key): Unique identifier for the event
- `payload` (JSON): Full event payload from GitHub
- `created_at` (STRING): Event creation timestamp
- `repo` (STRING): Repository identifier (owner/repo format)

## Development

To run the connector locally:
```bash
python connector.py
```

## Deployment

To deploy to Fivetran:

1. Package your connector
2. Deploy using Fivetran's deployment process
3. Configure the connector in Fivetran's dashboard

## Limitations

- Only fetches public events unless a GitHub token is provided
- Subject to GitHub API rate limits
- Returns up to 30 most recent events per repository (GitHub API limitation)

## Error Handling

The connector logs:
- API rate limit information
- Number of events retrieved per repository
- Most recent event timestamp
- Any errors that occur during execution

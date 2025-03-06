import requests
import json
from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Operations as op
from fivetran_connector_sdk import Logging as log

def load_configuration():
    """Load repository configuration from configuration.json"""
    with open('configuration.json', 'r') as f:
        return json.load(f)

def get_repo_events(owner, repo, headers):
    """Fetch the latest public events for a repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}/events"
    response = requests.get(url, headers=headers)
    
    # Print rate limit information
    rate_limit = response.headers.get('X-RateLimit-Remaining', 'N/A')
    log.info(f"Remaining GitHub API calls: {rate_limit}")
    
    response.raise_for_status()
    events = response.json()
    
    # Transform the events into the desired format
    formatted_events = [
        {
            "event_id": event["id"],
            "payload": event.get("payload", {}),
            "created_at": event["created_at"],
            "repo": f"{owner}/{repo}"
        }
        for event in events
    ]
    return formatted_events

def schema(configuration):
    """Define the schema for the GitHub events table"""
    return [
        {
            "table": "github_events",
            "primary_key": ["event_id"],
            "columns": {
                "event_id": "STRING",
                "payload": "JSON",
                "created_at": "STRING",
                "repo": "STRING"
            }
        }
    ]

def update(configuration, state):
    """Fetch and yield GitHub events data"""
    try:
        # Load configuration
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if configuration.get("github_token"):
            headers["Authorization"] = f"token {configuration['github_token']}"

        # Parse repo_list from comma-separated string
        repo_list = configuration.get('repo_list', '').strip()
        if not repo_list:
            log.severe("No repositories configured")
            return

        # Convert "owner/repo" strings to structured data
        repos = []
        for repo_string in repo_list.split(','):
            if '/' in repo_string:
                owner, repo = repo_string.strip().split('/')
                repos.append({"owner": owner, "repo": repo})

        if not repos:
            log.severe("No valid repositories found in configuration")
            return

        for repo_info in repos:
            owner = repo_info['owner']
            repo = repo_info['repo']
            repo_key = f"{owner}/{repo}"
            log.info(f"Checking repository: {repo_key}")
            
            events = get_repo_events(owner, repo, headers)
            log.info(f"Retrieved {len(events)} events")
            
            if events:
                most_recent = events[0]['created_at']
                log.info(f"Most recent event: {most_recent}")
            
                # Send each event individually
                for event in events:
                    yield op.upsert("github_events", {
                        "event_id": event["event_id"],
                        "payload": event["payload"],
                        "created_at": event["created_at"],
                        "repo": event["repo"]
                    })
            
    except Exception as e:
        log.severe(f"Error occurred: {e}")

# Initialize the connector
connector = Connector(
    update=update,
    schema=schema
)

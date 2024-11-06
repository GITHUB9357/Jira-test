import os
import pandas as pd
from github import Github
from jira import JIRA
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_user_to_org(github_client, username, org_name):
    org = github_client.get_organization(org_name)
    org.invite_user(username)

def add_user_to_repo(github_client, username, repo_name):
    repo = github_client.get_repo(repo_name)
    repo.add_to_collaborators(username, permission='push')

def create_jira_ticket(jira_client, summary, description):
    new_issue = jira_client.create_issue(project='HR', summary=summary, description=description, issuetype={'name': 'Task'})
    return new_issue.key

def main():
    # Get Jira configuration from environment variables
    jira_url = os.environ.get('JIRA_SERVER')
    jira_user = os.environ.get('JIRA_USER')
    jira_api_token = os.environ.get('JIRA_TOKEN')
    github_token = os.environ.get('GITHUB_TOKEN')

    if not all([jira_url, jira_user, jira_api_token, github_token]):
        logger.error("Missing configuration. Please set JIRA_SERVER, JIRA_USER, JIRA_TOKEN, and GITHUB_TOKEN environment variables.")
        return

    try:
        jira_client = JIRA(server=jira_url, basic_auth=(jira_user, jira_api_token))
        github_client = Github(github_token)
        logger.info("Successfully connected to Jira and GitHub")

        # Read the CSV file
        df = pd.read_csv('users_to_onboard.csv')

        for index, row in df.iterrows():
            username = row['username']
            email = row['email']
            github_username = row['github_username']
            org_name = row['org_name']
            repos = row['repos'].split(';')

            try:
                # Add user to organization
                add_user_to_org(github_client, github_username, org_name)
                logger.info(f"Added {github_username} to organization {org_name}")

                # Add user to repositories
                for repo in repos:
                    add_user_to_repo(github_client, github_username, f"{org_name}/{repo}")
                    logger.info(f"Added {github_username} to repository {org_name}/{repo}")

                # Create Jira ticket
                summary = f"Onboard user: {username}"
                description = f"Onboarding process for {username} ({email}) to GitHub organization {org_name} and repositories: {', '.join(repos)}"
                jira_ticket = create_jira_ticket(jira_client, summary, description)

                logger.info(f"Successfully onboarded {username} (Jira ticket: {jira_ticket})")

            except Exception as e:
                logger.error(f"Error onboarding {username}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
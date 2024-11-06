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
    github_client = Github(os.environ['GITHUB_TOKEN'])
    jira_client = JIRA(server=os.environ['JIRA_SERVER'], basic_auth=(os.environ['JIRA_USER'], os.environ['JIRA_TOKEN']))

    try:
        df = pd.read_csv('users_to_onboard.csv')
    except FileNotFoundError:
        logger.error("users_to_onboard.csv file not found")
        return
    except pd.errors.EmptyDataError:
        logger.error("users_to_onboard.csv is empty")
        return

    for index, row in df.iterrows():
        username = row['username']
        email = row['email']
        github_username = row['github_username']
        org_name = row['org_name']
        repos = row['repos'].split(';')

        logger.info(f"Processing user: {username}")

        try:
            add_user_to_org(github_client, github_username, org_name)
            logger.info(f"Added {github_username} to organization {org_name}")

            for repo in repos:
                add_user_to_repo(github_client, github_username, f"{org_name}/{repo}")
                logger.info(f"Added {github_username} to repository {org_name}/{repo}")

            summary = f"Onboard user: {username}"
            description = f"Onboarding process for {username} ({email}) to GitHub organization {org_name} and repositories: {', '.join(repos)}"
            jira_ticket = create_jira_ticket(jira_client, summary, description)

            logger.info(f"Successfully onboarded {username} (Jira ticket: {jira_ticket})")

        except Exception as e:
            logger.error(f"Error onboarding {username}: {str(e)}")

if __name__ == "__main__":
    main()
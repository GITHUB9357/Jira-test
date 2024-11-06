import os
import pandas as pd
from github import Github, GithubException
from jira import JIRA
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_user_to_org(github_client, username, org_name):
    org = github_client.get_organization(org_name)
    try:
        user = github_client.get_user(username)
        org.invite_user(user)
        logger.info(f"Invited {username} to organization {org_name}")
    except GithubException as e:
        logger.error(f"Failed to invite {username} to organization {org_name}: {str(e)}")
        raise

def add_user_to_repo(github_client, username, repo_name):
    try:
        repo = github_client.get_repo(repo_name)
        repo.add_to_collaborators(username, permission='push')
        logger.info(f"Added {username} to repository {repo_name}")
    except GithubException as e:
        logger.error(f"Failed to add {username} to repository {repo_name}: {str(e)}")
        raise

def create_jira_ticket(jira_client, summary, description):
    try:
        new_issue = jira_client.create_issue(project='HR', summary=summary, description=description, issuetype={'name': 'Task'})
        return new_issue.key
    except Exception as e:
        logger.error(f"Failed to create Jira ticket: {str(e)}")
        raise

def main():
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

        df = pd.read_csv('users_to_onboard.csv')

        for index, row in df.iterrows():
            username = row['username']
            email = row['email']
            github_username = row['github_username']
            org_name = row['org_name']
            repos = row['repos'].split(';')

            logger.info(f"Processing user: {username}")

            try:
                add_user_to_org(github_client, github_username, org_name)

                for repo in repos:
                    full_repo_name = f"{org_name}/{repo}"
                    add_user_to_repo(github_client, github_username, full_repo_name)

                summary = f"Onboard user: {username}"
                description = f"Onboarding process for {username} ({email}) to GitHub organization {org_name} and repositories: {', '.join(repos)}"
                jira_ticket = create_jira_ticket(jira_client, summary, description)

                logger.info(f"Successfully onboarded {username} (Jira ticket: {jira_ticket})")

            except Exception as e:
                logger.error(f"Error onboarding {username}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()
import os
from github import Github
from jira import JIRA
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def remove_user_from_org(github_client, username, org_name):
    org = github_client.get_organization(org_name)
    org.remove_membership(username)

def remove_user_from_repo(github_client, username, repo_name):
    repo = github_client.get_repo(repo_name)
    repo.remove_from_collaborators(username)

def create_jira_ticket(jira_client, summary, description):
    new_issue = jira_client.create_issue(project='HR', summary=summary, description=description, issuetype={'name': 'Task'})
    return new_issue.key

def main():
    github_client = Github(os.environ['GITHUB_TOKEN'])
    jira_client = JIRA(server=os.environ['JIRA_SERVER'], basic_auth=(os.environ['JIRA_USER'], os.environ['JIRA_TOKEN']))

    # Assume the GitHub username is passed as an environment variable
    github_username = os.environ.get('GITHUB_USERNAME_TO_OFFBOARD')
    org_name = os.environ.get('GITHUB_ORG_NAME')

    if not github_username or not org_name:
        logger.error("GitHub username or organization name not provided")
        return

    logger.info(f"Processing offboarding for user: {github_username}")

    try:
        remove_user_from_org(github_client, github_username, org_name)
        logger.info(f"Removed {github_username} from organization {org_name}")

        # You might want to iterate through repos here if needed

        summary = f"Offboard user: {github_username}"
        description = f"Offboarding process for {github_username} from GitHub organization {org_name}"
        jira_ticket = create_jira_ticket(jira_client, summary, description)

        logger.info(f"Successfully offboarded {github_username} (Jira ticket: {jira_ticket})")

    except Exception as e:
        logger.error(f"Error offboarding {github_username}: {str(e)}")

if __name__ == "__main__":
    main()
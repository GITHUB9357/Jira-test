import os
from jira import JIRA
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_jira_ticket(jira_client, ticket_id, status):
    issue = jira_client.issue(ticket_id)
    issue.update(fields={'status': {'name': status}})

def main():
    jira_client = JIRA(server=os.environ['JIRA_SERVER'], basic_auth=(os.environ['JIRA_USER'], os.environ['JIRA_TOKEN']))

    # Assume the Jira ticket ID is passed as an environment variable
    ticket_id = os.environ.get('JIRA_TICKET_ID')
    new_status = os.environ.get('JIRA_NEW_STATUS', 'Done')

    if not ticket_id:
        logger.error("Jira ticket ID not provided")
        return

    try:
        update_jira_ticket(jira_client, ticket_id, new_status)
        logger.info(f"Successfully updated Jira ticket {ticket_id} to status: {new_status}")
    except Exception as e:
        logger.error(f"Error updating Jira ticket {ticket_id}: {str(e)}")

if __name__ == "__main__":
    main()
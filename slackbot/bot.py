from asyncio import Future
from concurrent.futures import ThreadPoolExecutor
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List, Any
from slackbot.config.config import blockable_emails
import time

class SlackBot:
    client: WebClient
    def __init__(self, token: str) -> None:
        self.client = WebClient(token=token)

    def send_notification(self, channel: str, messages: List[str], resource: Any) -> bool:
        notifications = self.generate_email_notifications(resource,messages)
        print(f'[COMPLETED]: Found {len(notifications)} messages... checking for new messages...')
        for message in notifications:
            try:
                response = self.client.chat_postMessage(
                    channel=channel,
                    text=message
                )
                if response.status_code == 200:
                    print(f'[SUCCESS]: Notification Sent to channel {channel} @ {9}')
                    return True
            except SlackApiError as e:
                print(f'[ERROR]: Error sending message to slack channel --> {e}')
                return False

    def generate_email_notifications(self, resource: Any, messages: List[str]) -> List[str]:
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
        futures : List[Future[str]]  = []

        def task(message: str) -> str:
            msg = resource.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            email_dict = {}
            for header in headers:
                if header['name'] in ['From', 'To', 'Subject', 'Date','Body'] and header['name'] not in blockable_emails:
                    email_dict[header['name'].lower()] = header['value']
                else:
                    email_dict[header['name'].lower()] = 'None'
                email_dict['body'] = msg['snippet']
            return f"From: {email_dict['from']}\nTo: {email_dict['to']}\nSubject: {email_dict['subject']}\nBody: {email_dict['body']}\nDate: {email_dict['date']}\n"

    
        for message in messages:
            time.sleep(2)
            futures.append(executor.submit(task,message=message))
        executor.shutdown(wait=True)
        currated_messages: List[str] = list()
        for i in range(0,len(futures)):
            currated_messages.append(futures[i].result())
        return currated_messages
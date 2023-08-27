import os
from typing import Any, Tuple,List
from datetime import datetime, timedelta
from slackbot.config.config import GoogleAPIDict
from slackbot.enums.enums import GoogleAPI,GmailFlag
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from concurrent.futures import ThreadPoolExecutor, Future


class Google:
    service: GoogleAPI
    resource: Any
    def __init__(self, name: GoogleAPI, email: str | List[str] = "") -> None:
        def create_gmail_resource():
            creds = None
            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', GoogleAPIDict[self.service.value]['scopes'])
            # If there are no (valid) credentials available, let the user log in.
            if creds:
                timestamp = datetime.strptime(creds.expiry.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),"%Y-%m-%dT%H:%M:%S.%fZ")
                current_date = datetime.utcnow()
                expiration_date = timestamp + timedelta(days=1)
                if expiration_date.date() == current_date.date():
                    creds.refresh(Request())
            elif creds is None:
                    print(GoogleAPIDict[self.service.value])
                    flow = InstalledAppFlow.from_client_secrets_file(
                    'cred.json', GoogleAPIDict[self.service.value]['scopes'])
                    creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())

            self.resource = build(
                self.service.value,
                GoogleAPIDict[self.service.value]['version'],
                credentials=creds
            )

        self.service = name
        if name.name == GoogleAPI.GMAIL.name:
            create_gmail_resource()



class Youtube(Google):
    def __init__(self, name: GoogleAPI) -> None:
        super().__init__(name)


class Gmail(Google):
    email: str | List[str]
    def __init__(self, name: GoogleAPI, email: str | List[str]) -> None:
        super().__init__(name,email=email)
        
    
    def check_email(self, maxResult: int, condition: GmailFlag, sender: str = None) -> Tuple[bool,List[str]]:
        query = f'from:{sender} is:{condition.value}'

        try:
            result = self.resource.users().messages().list(userId='me',maxResults=maxResult).execute() if condition.value != "none" or sender != None else self.resource.users().messages().list(userId='me',maxResults=maxResult, q=query).execute()
            messages = result.get('messages',[])
            return (True,messages if len(messages) > 0 else False,messages)
        except HttpError as error:
            print(f'[ERROR]: An error occurred making a request to the google API --> {error}')
            return (False,[])
    

    def generate_currated_emails(self, messages: List[str]) -> List[str]:
        executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=len(messages))
        futures : List[Future[str]]  = []

        def task(message: str) -> str:

            msg = self.resource.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
            print(f'Sender: {sender}\n Message: {msg["snippet"]}\n')

        
        for message in messages:
            futures.append(executor.submit(task(message=message)))
        executor.shutdown(wait=True)
        currated_messages: List[str] = list()
        for i in range(0,len(futures)):
            currated_messages.append(futures[i].result())
        return currated_messages

from slackbot.bot import SlackBot
from slackbot.wrapper import Gmail
from slackbot.enums.enums import GoogleAPI,GmailFlag
import time

interval = 60 / 4
slack_tokens = {
    "slack_token":"xoxb-3466765387057-5201143762164-GzebqJNhe3POhWmQRu8xRnJh",
    "channel_id":"C04PRNH69SP"
}

# Set to store the IDs of Gmail messages sent to Slack
sent_message_ids = set()

def send_slack_message(channel, message):
    slackbot = SlackBot(slack_tokens['slack_token'])
    slackbot.send_notification(channel, message, None)

print('[IN PROGRESS]: Starting Slackbot.... Checking emails...')
while True:
    gmail = Gmail(GoogleAPI.GMAIL,"antiegg.kr@gmail.com")
    slackbot = SlackBot(slack_tokens['slack_token'])
    print('[IN PROGRESS]: Sourcing emails....')
    t = gmail.check_email(maxResult=20,condition=GmailFlag.NONE,sender="juyeon.kr@gmail.com")

    if t[0]:
        # Filter out already sent messages
        new_messages = [msg for msg in t[1] if msg['id'] not in sent_message_ids]

        if new_messages:
            # Get the message snippets from the new messages
            message_snippets = [msg['snippet'] for msg in new_messages]
            send_slack_message("#test-bot", message_snippets)

            # Update the set of sent message IDs
            sent_message_ids.update(msg['id'] for msg in new_messages)
    
    print(f'[IN PROGRESS]: Beginning sleep for {interval} seconds...')
    time.sleep(interval)
print('\n[COMPLETED]: Slackbot shutting down....')
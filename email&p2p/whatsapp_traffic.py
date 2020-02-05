import random
import time
import string
from tShark import tSharkSniff
from twilio.rest import Client
# Setup: https://www.twilio.com/docs/sms/whatsapp/quickstart/python

class whatsappClient(object):
    """docstring for whatsappClient"""
    def __init__(self):
        account_sid = 'AC6ac55007b2752560426df3a870855c4f'
        auth_token = '64aaab4a59a857e96fd234f4d65ce357'
        # client credentials are read from TWILIO_ACCOUNT_SID and AUTH_TOKEN
        self.client = Client(account_sid, auth_token)
        # this is the Twilio sandbox testing number
        self.from_whatsapp_number='whatsapp:+14155238886'
        # replace this number with your own WhatsApp Messaging number
        self.to_whatsapp_number='whatsapp:+13479875493'

    def send_message(self, message):
        self.client.messages.create(body=message,
                       from_=self.from_whatsapp_number,
                       to=self.to_whatsapp_number)

if __name__ == '__main__':
    sniff = tSharkSniff(interface='WLAN')
    client = whatsappClient()

    count = 0
    while count < 3:
        print(count)
        sniff.start(output='./result/whatsapp/whatsapp_'+str(int(time.time()))+'.pcap')
        time.sleep(2)
        message = 'Randomly generated: '+''.join(random.choices(string.ascii_uppercase + string.digits, k=30))
        client.send_message(message)
        time.sleep(3)
        sniff.stop()
        count += 1
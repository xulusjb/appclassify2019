import smtplib
import imaplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tShark import tSharkSniff
import time
import random
import string
import subprocess

class emailClient(object):
    """docstring for emailClient"""
    def __init__(self):
        self.ADDRESS = 'ddouup@gmail.com'
        self.PASSWORD = 'zerose1996'
        self.host = 'smtp.gmail.com'
        self.port = 587

    def get_contacts(self, filename):
        """
        Return two lists names, emails containing names and email addresses
        read from a file specified by filename.
        """
        names = []
        emails = []
        with open(filename, mode='r', encoding='utf-8') as contacts_file:
            for a_contact in contacts_file:
                names.append(a_contact.split()[0])
                emails.append(a_contact.split()[1])
        return names, emails

    def read_template(self, filename):
        """
        Returns a Template object comprising the contents of the 
        file specified by filename.
        """
        with open(filename, 'r', encoding='utf-8') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    def send_mail(self, name, email, message_template):
        # set up the SMTP server
        s = smtplib.SMTP(host=self.host, port=self.port)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.ADDRESS, self.PASSWORD)

        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())
        message += '\n Randomly generated: '+''.join(random.choices(string.ascii_uppercase + string.digits, k=1000))

        # Prints out the message body for our sake
        # print(message)

        # setup the parameters of the message
        msg['From']=self.ADDRESS
        msg['To']=email
        msg['Subject']="This is TEST"
        
        # add in the message body
        msg.attach(MIMEText(message, 'plain'))
        
        # send the message via the server set up earlier.
        s.send_message(msg)
        del msg
            
        # Terminate the SMTP session and close the connection
        s.quit()

    def receive(self):
        s = imaplib.IMAP4('imap.gmail.com')
        s.starttls()
        s.login(self.ADDRESS, self.PASSWORD)
        s.list()
        # Out: list of "folders" aka labels in gmail.
        s.select("inbox") # connect to inbox.

        result, data = mail.search(None, "ALL")

        ids = data[0] # data is a list.
        id_list = ids.split() # ids is a space separated string
        latest_email_id = id_list[-1] # get the latest

        result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID

        raw_email = data[0][1] # here's the body, which is raw text of the whole email
        # including headers and alternate payloads
        return raw_email
        
if __name__ == '__main__':
    sniff = tSharkSniff(interface='WLAN')
    client = emailClient()
    message_template = client.read_template('message.txt')
    names, emails = client.get_contacts('mycontacts.txt')
    count = 0
    while count < 50:
        for name, email in zip(names, emails):
            subprocess.call('ipconfig /flushdns')
            sniff.start(output='./result/vpn_email/vpn_email_'+str(int(time.time()))+'.pcap')
            time.sleep(3)
            client.send_mail(name, email, message_template)
            time.sleep(5)
            sniff.stop()
            count += 1
            print(count)
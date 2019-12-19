from twilio.rest import Client
# Setup: https://www.twilio.com/docs/sms/whatsapp/quickstart/python

class whatsappClient(object):
	"""docstring for whatsappClient"""
	def __init__(self, to_number)
		account_sid = 'AC6ac55007b2752560426df3a870855c4f'
		auth_token = 'your_auth_token'
		# client credentials are read from TWILIO_ACCOUNT_SID and AUTH_TOKEN
		self.client = Client(account_sid, auth_token)
		# this is the Twilio sandbox testing number
		self.from_whatsapp_number='whatsapp:+14155238886'
		# replace this number with your own WhatsApp Messaging number
		self.to_whatsapp_number='whatsapp:+'

	def send_message(self, message):
		client.messages.create(body=message,
                       from_=self.from_whatsapp_number,
                       to=self.to_whatsapp_number)

if __name__ == '__main__':
	sniff = tSharkSniff()
    client = bittorrentClient()
    messages = []   # magnet links of torrents
    # torrent_list = client.get_torrents()
    for message in messages:
        sniff.start(output=output)
        client.download_from_url(message)
        sniff.stop()
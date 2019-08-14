import smtplib
import json
import requests


# Function for send email using an existing gmail account
def send_email(recipient, msg):
	with open("config.json") as config_file:
		data = json.load(config_file)
	notifications = data['notifications']

	smtp_server = notifications['smtp_server']
	smtp_user = notifications['username']
	smtp_pass = notifications['password']

	recipients = recipient
	sender = smtp_user
	subject = "New event WhiteBlocker"
	text = msg
	message = "Subject: {0}\n\n{1}".format(subject, text)

	server = smtplib.SMTP(smtp_server, 587)
	server.ehlo()
	server.starttls()
	server.ehlo()
	server.login(smtp_user, smtp_pass)
	server.sendmail(sender, recipients, message)
	server.quit()


# Send message
def send_msg_bot(msg):
	with open("config.json") as config_file:
		data = json.load(config_file)
	notifications_bot = data['notifications_bot']

	api_key = notifications_bot['api_key']
	chat_id = notifications_bot['chat_id']
	url = "https://api.telegram.org/bot" + api_key + "/sendMessage"
	querystring = {
		"chat_id": chat_id,
		"text": msg
	}

	response = requests.get(url, params=querystring)
	print(response.text)


# Send message
def send_gif_bot(gif_url):
	with open("config.json") as config_file:
		data = json.load(config_file)
	notifications_bot = data['notifications_bot']

	api_key = notifications_bot['api_key']
	chat_id = notifications_bot['chat_id']
	url = "https://api.telegram.org/bot" + api_key + "/sendAnimation"
	querystring = {
		"chat_id": chat_id,
		"animation": gif_url
	}

	response = requests.get(url, params=querystring)
	print(response.text)

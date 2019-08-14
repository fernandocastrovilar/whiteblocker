import smtplib
import json


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

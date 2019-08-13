import smtplib


# Function for send email using an existing gmail account
def send_email(recipient, msg):
	smtp_server = "smtp.gmail.com"

	with open("credentials.txt") as f:
		credentials = [x.strip().split(':', 1) for x in f]
	for username, password in credentials:
		smtp_user = username
		smtp_pass = password

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

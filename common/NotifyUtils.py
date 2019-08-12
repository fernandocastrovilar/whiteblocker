import smtplib

smtp_server = "smtp.gmail.com"
smtp_user = "" # Gmail user account
smtp_pass = "" # Gmail password account

RECIPIENTS = "" # Email to:
SENDER = smtp_user
mssg = ""
s = mssg

server = smtplib.SMTP(smtp_server, 587)
server.ehlo()
server.starttls()
server.ehlo()
server.login(smtp_user, smtp_pass)
server.set_debuglevel(1)
server.sendmail(SENDER, [RECIPIENTS], s)
server.quit()

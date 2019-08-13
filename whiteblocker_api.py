import logging
import datetime
import ipaddress
from common.SocketUtils import open_listen_socket
from common.SecurityUtils import block_ip, LocateIp
from common.DatabaseUtils import insert_db, select_all, select_full_custom, update_row, init_db
from common.NotifyUtils import send_email


recipient = ""


# Case 1: IP not blocked and not in DB
def case_1(ip):
	block = block_ip(ip=ip)
	if block == "ko":
		print("Failed to block the IP {0}, manual action is required".format(ip))
		logging.error("Failed to block the IP {0}, manual action is required".format(ip))

	# Next steps consist on retrieve info about the IP, store it on the DB and send a notification with the data.
	# Get IP info
	ip_data = LocateIp(ip)
	location = str(ip_data.country_name()) + ", " + str(ip_data.state())
	print("The blocked IP is from {0}".format(location))
	logging.info("The blocked IP is from {0}".format(location))

	# Write IP, date and info to DB
	print("Writing info on DB...")
	logging.info("Writing info on DB...")
	date = "{0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
	try:
		result = insert_db(ip=ip, tries="1", location=location, current_status="Blocked", first_view=date, last_view=date)
		if result == "ko":
			print("Failed to insert info on DB")
			logging.error("Failed to insert info on DB")
			return "ko"
		row_inserted = select_full_custom(field="*", condition="IP", match=ip)
		print(row_inserted)
		logging.info(row_inserted)
		print("Successful inserted data on DB")
		logging.info("Successful inserted data on DB")
		print("Sending notification...")
		logging.info("Sending notification...")
		send_email(recipient=recipient,
					msg="Blocking IP due to a scan try.\n\nIP: {0}\nTries: 1\nDate: {1}".format(ip, date))
		return "ok"
	except Exception as e:
		print(e)
		return "ko"


# Case 2:IP is not blocked but it's already listed on DB
def case_2(ip):
	block = block_ip(ip=ip)
	if block == "ko":
		print("Failed to block the IP {0}, manual action is required".format(ip))
		logging.error("Failed to block the IP {0}, manual action is required".format(ip))
	# Retrieve IP historic tries
	tries = str(select_full_custom(field="TRIES", condition="IP", match=ip))
	tries = int(''.join(list(filter(str.isdigit, tries))))
	print("IP {0} made {1} tries".format(ip, tries))
	logging.info("IP {0} made {1} tries".format(ip, tries))
	tries = int(tries) + 1
	# Update DB
	date = "{0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
	print("Updating tries...")
	logging.info("Updating tries...")
	update_tries = update_row(ip=ip, field="TRIES", value=tries)
	if update_tries == "ko":
		print("Failed to update tries")
		logging.error("Failed to update tries")
	elif update_tries == "ok":
		print("Successful updated tries")
		logging.info("Successful updated tries")
	print("Updating date...")
	logging.info("Updating date...")
	update_date = update_row(ip=ip, field="LAST_VIEW", value=date)
	if update_date == "ko":
		print("Failed to update date")
		logging.error("Failed to update date")
	elif update_date == "ok":
		print("Successful updated date")
		logging.info("Successful updated date")
	print("Updating status...")
	logging.info("Updating status...")
	update_status = update_row(ip=ip, field="CURRENT_STATUS ", value="Blocked")
	if update_status == "ko":
		print("Failed to update status")
		logging.error("Failed to update status")
	elif update_status == "ok":
		print("Successful updated status")
		logging.info("Successful updated status")
	print("Sending notification...")
	logging.info("Sending notification...")
	send_email(recipient=recipient,
				msg="Blocking IP due to a scan try.\n\nIP: {0}\nTries:{1}\nDate: {2}".format(ip, tries, date))
	return "ok"


# Main function
def main():
	init_db()
	while True:
		print("opening socket")
		socket = open_listen_socket()
		if socket != "timeout":
			ip = socket
			if ipaddress.ip_address(ip).is_private is True:
				print("Skipping, connection from private network")
				logging.info("Skipping, connection from private network")
				continue
			print("Launching function to block the IP {0}".format(ip))
			logging.info("Launching function to block the IP {0}".format(ip))
			lst = select_all()
			if any(ip in s for s in lst):
				# Case 2: IP is not blocked but it's already on DB
				case_2(ip=ip)
			else:
				# Case 1: IP not blocked not in BD
				case_1(ip=ip)
		else:
			print("Changing socket port due to timeout waiting for connection")
			logging.warning("Changing socket port due to timeout waiting for connection")


if __name__ == "__main__":
	main()

import logging
import datetime
import ipaddress
import json
import re
import subprocess
import platform
import time as tm
from dateutil.parser import parse
from common.SocketUtils import open_listen_socket
from common.SecurityUtils import block_ip, LocateIp, unblock_ip
from common.DatabaseUtils import insert_db, select_all, select_full_custom, multiple_update_row, init_db
from common.NotifyUtils import send_email, send_msg_bot

with open("config.json") as config_file:
	data = json.load(config_file)
notifications = data['notifications']
recipient = notifications['recipient']


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
	date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
	try:
		result = insert_db(ip=ip, tries="1", location=location, current_status="Blocked", blocked_date=date, unblocked_date="None", first_view=date, last_view=date)
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
		message = "Blocking IP due to a scan try.\n\nIP: {0}\nTries: 1\nDate: {1}".format(ip, date)
		send_email(recipient=recipient, msg=message)
		send_msg_bot(msg=message)
		return "ok"
	except Exception as e:
		print(e)
		return "ko"


# Case 2: IP is not blocked but it's already listed on DB
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
	date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	print("Updating DB info...")
	logging.info("Updating DB info...")
	update_db = multiple_update_row(ip=ip, conditions="'TRIES' = '{0}', 'LAST_VIEW' = '{1}', 'BLOCKED_DATE' = '{1}', 'CURRENT_STATUS' = 'Blocked'".format(tries, date))
	if update_db == "ko":
		print("Failed to update data")
		logging.error("Failed to update data")
	elif update_db == "ok":
		print("Successful updated data")
		logging.info("Successful updated data")
	print("Sending notification...")
	logging.info("Sending notification...")
	message = "Blocking IP due to a scan try.\n\nIP:{0}\nTries:{1}\nDate: {2}".format(ip, tries, date)
	send_email(recipient=recipient, msg=message)
	send_msg_bot(msg=message)
	return "ok"


# Case 3: Manual block
def case_3(ip, tier):
	block = block_ip(ip=ip)
	if block == "ko":
		print("Failed to block the IP {0}, manual action is required".format(ip))
		logging.error("Failed to block the IP {0}, manual action is required".format(ip))

	# Get IP info
	ip_data = LocateIp(ip)
	location = str(ip_data.country_name()) + ", " + str(ip_data.state())
	print("The blocked IP is from {0}".format(location))
	logging.info("The blocked IP is from {0}".format(location))

	# Write IP, date and info to DB
	print("Writing info on DB...")
	logging.info("Writing info on DB...")
	date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
	try:
		result = insert_db(ip=ip, tries=tier, location=location, current_status="Blocked", blocked_date=date, unblocked_date="None", first_view=date, last_view=date)
		if result == "ko":
			print("Failed to insert info on DB")
			logging.error("Failed to insert info on DB")
			return "ko"
		row_inserted = select_full_custom(field="*", condition="IP", match=ip)
		print(row_inserted)
		logging.info(row_inserted)
		print("Successful inserted data on DB")
		logging.info("Successful inserted data on DB")
		return "ok"
	except Exception as e:
		print(e)
		return "ko"


# Unblock IP after time pass
def unblock(ip):
	date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	ip_tables = unblock_ip(ip=ip)
	if ip_tables == "ko":
		print("Error unblocking IP {0}".format(ip))
		logging.error("Error unblocking IP {0}".format(ip))
		return "ko"
	else:
		update_db = multiple_update_row(conditions="CURRENT_STATUS = 'Unblocked', UNBLOCKED_DATE = '" + date + "'", ip=ip)
	if update_db == "ko":
		print("Error updating DB")
		logging.error("Error updating DB")
		return "ko"


# Main function for whiteblocker
def whiteblocker_process():
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


# Function for unblock old IPs
def whiteblocker_unblock():
	while True:
		""" Tiers:
		Tier 1: 1 week blocked = 1 Try
		Tier 2: 15 days blocked = 2 Tries
		Tier 3: 1 month blocked = 3 Tries
		Tier 4: 3 months blocked = 4 Tries
		Tier 5: 6 months blocked = 5 Tries
		Tier 6: Permanent blocked = 6 Tries
		"""
		current_date = parse(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
		blocked_ips = select_full_custom(field="IP", condition="CURRENT_STATUS", match="Blocked")
		if blocked_ips == "ko":
			print("Error getting IPs blocked")
			logging.error("Error getting IPs blocked")
			return "ko"
		for ip in blocked_ips:
			ip = str(re.findall(r'[0-9]+(?:\.[0-9]+){3}', str(ip))).replace('[', '').replace(']', '').replace('\'', '')
			blocked_date = str(select_full_custom(field="BLOCKED_DATE", condition="IP", match=ip))
			if blocked_date == "ko":
				print("Error getting IPs blocked date")
				logging.error("Error getting IPs blocked date")
				return "ko"
			for elem in ["[", "]", "(", ")", "'", ","]:
				if elem in blocked_date:
					blocked_date = blocked_date.replace(elem, '')
			print("The IP {0} was blocked on {1}".format(ip, blocked_date))
			last_date = parse(blocked_date)
			time = int(str((current_date - last_date)).split(' ', 1)[0])
			tries = str(select_full_custom(field="TRIES", condition="IP", match=ip))
			tries = int(''.join(list(filter(str.isdigit, tries))))
			if time >= 7 and tries == 1:
				ip_unblock = unblock(ip=ip)
				if ip_unblock == "ko":
					print("Failed to unblock IP {0}, contact sysadmin".format(ip))
					logging.error("Failed to unblock IP {0}, contact sysadmin".format(ip))
					raise Exception
				else:
					print("Successful unblocked IP {0}".format(ip))
					logging.info("Successful unblocked IP {0}".format(ip))
					message = "Unblocked IP due to time pass.\n\nIP: {0}\nDate: {1}".format(ip, current_date)
					send_email(recipient=recipient, msg=message)
					send_msg_bot(msg=message)
			elif time >= 15 and tries == 2:
				ip_unblock = unblock(ip=ip)
				if ip_unblock == "ko":
					print("Failed to unblock IP {0}, contact sysadmin".format(ip))
					logging.error("Failed to unblock IP {0}, contact sysadmin".format(ip))
					raise Exception
				else:
					print("Successful unblocked IP {0}".format(ip))
					logging.info("Successful unblocked IP {0}".format(ip))
					message = "Unblocked IP due to time pass.\n\nIP: {0}\nDate: {1}".format(ip, current_date)
					send_email(recipient=recipient, msg=message)
					send_msg_bot(msg=message)
			elif time >= 30 and tries == 3:
				ip_unblock = unblock(ip=ip)
				if ip_unblock == "ko":
					print("Failed to unblock IP {0}, contact sysadmin".format(ip))
					logging.error("Failed to unblock IP {0}, contact sysadmin".format(ip))
					raise Exception
				else:
					print("Successful unblocked IP {0}".format(ip))
					logging.info("Successful unblocked IP {0}".format(ip))
					message = "Unblocked IP due to time pass.\n\nIP: {0}\nDate: {1}".format(ip, current_date)
					send_email(recipient=recipient, msg=message)
					send_msg_bot(msg=message)
			elif time >= 90 and tries == 4:
				ip_unblock = unblock(ip=ip)
				if ip_unblock == "ko":
					print("Failed to unblock IP {0}, contact sysadmin".format(ip))
					logging.error("Failed to unblock IP {0}, contact sysadmin".format(ip))
					raise Exception
				else:
					print("Successful unblocked IP {0}".format(ip))
					logging.info("Successful unblocked IP {0}".format(ip))
					message = "Unblocked IP due to time pass.\n\nIP: {0}\nDate: {1}".format(ip, current_date)
					send_email(recipient=recipient, msg=message)
					send_msg_bot(msg=message)
			elif time >= 180 and tries == 5:
				ip_unblock = unblock(ip=ip)
				if ip_unblock == "ko":
					print("Failed to unblock IP {0}, contact sysadmin".format(ip))
					logging.error("Failed to unblock IP {0}, contact sysadmin".format(ip))
					raise Exception
				else:
					print("Successful unblocked IP {0}".format(ip))
					logging.info("Successful unblocked IP {0}".format(ip))
					message = "Unblocked IP due to time pass.\n\nIP: {0}\nDate: {1}".format(ip, current_date)
					send_email(recipient=recipient, msg=message)
					send_msg_bot(msg=message)
			elif time >= 365 and tries == 6:
				print("This is permanent blocked!")
			else:
				break
		tm.sleep(1800)


# Function for check if the system software requirements is compliment
def check_system():
	so = check_so()
	software = check_software()
	if so == "ok" and software == "ok":
		return "ok"
	else:
		return "ko"


# Function for check the compatibility with the SO
def check_so():
	so = platform.system()
	if "Linux" in so:
		return "ok"
	else:
		return "ko"


# Function for check if the necessary software are running/installed/stopped... And fix it.
def check_software():
	script = "dpkg -s nftables | grep Status"
	result = subprocess.call(script, shell=True)
	if result == 0:
		print("Nftables is correctly installed")
		logging.info("Nftables is correctly installed")
		return "ok"
	else:
		print("Nftables it's not installed.")
		logging.error("Nftables it's not installed.")
		try:
			result = configure_nftables()
			if result == "ko":
				print("Failed to configure nftables")
				logging.error("Failed to configure nftables")
				return "ko"
			else:
				return "ok"
		except Exception as e:
			print(e)
			logging.error(e)
			return "ko"


# Function for configure nftables services
def configure_nftables():
	try:
		print("Trying to installing nftables...")
		logging.info("Trying to installing nftables...")
		script = "apt-get install -y nftables"
		result = subprocess.call(script, shell=True)
		if result == 0:
			print("Corrected installed nftables")
			logging.info("Corrected installed nftables")
		else:
			print("Failed to install nftables, manual intervention is needed")
			logging.error("Failed to install nftables, manual intervention is needed")
			return "ko"
	except Exception as e:
		print(e)
		logging.error(e)
		return "ko"
	print("Creating service and enabling")
	logging.info("Creating service and enabling")
	script = "cp linux_files/firewall.service /etc/systemd/system/firewall.service && systemctl enable firewall.service"
	result = subprocess.call(script, shell=True)
	if result != 0:
		print("Failed to setup Nftables")
		logging.error("Failed to setup Nftables")
		return "ko"
	print("Coping nftables initial config")
	logging.info("Coping nftables initial config")
	script = "mkdir /etc/firewall && cp linux_files/nftables.cfg /etc/firewall/"
	result = subprocess.call(script, shell=True)
	if result != 0:
		print("Failed to setup Nftables")
		logging.error("Failed to setup Nftables")
		return "ko"
	script = "systemctl start firewall.service"
	result = subprocess.call(script, shell=True)
	if result == 0:
		print("Nftables is successfully started")
		logging.info("Nftables is successfully started")
	else:
		print("Nftables isn't correctly started")
		logging.error("Nftables isn't correctly started")
		return "ko"

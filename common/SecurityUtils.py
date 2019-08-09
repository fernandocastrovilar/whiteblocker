import logging
import subprocess
import requests


# Function for block an IP
def block_ip(ip):
	script = "/sbin/iptables -A INPUT -s " + ip + " -j DROP"
	# Check if ip is already blocked
	ip_status = check_if_ip_is_blocked(ip=ip)
	if ip_status == "blocked":
		print("Ip {0} is already blocked".format(ip))
		logging.error("Ip {0} is already blocked".format(ip))
		return "Ip {0} is already blocked".format(ip)
	elif ip_status == "unblocked":
		try:
			print("Blocking IP: {0}".format(ip))
			logging.info("Blocking IP: {0}".format(ip))
			result = subprocess.call(script, shell=True)
			# If result = 0 command success, if different command failed
			if result == 0:
				print("IP {0} successfully blocked".format(ip))
				logging.info("IP {0} successfully blocked".format(ip))
				return "ok"
			else:
				print("IP {0} unsuccessfully blocked".format(ip))
				logging.error("IP {0} unsuccessfully blocked".format(ip))
				return "ko"
		except Exception as e:
			print(e)
			return "ko"


# Function for unblock an IP
def unblock_ip(ip):
	script = "/sbin/iptables -D INPUT -s " + ip + " -j DROP"
	# Check if ip is blocked
	ip_status = check_if_ip_is_blocked(ip=ip)
	if ip_status == "blocked":
		try:
			print("Unblocking IP: {0}".format(ip))
			logging.info("Unblocking IP: {0}".format(ip))
			result = subprocess.call(script, shell=True)
			# If result = 0 command success, if different command failed
			if result == 0:
				print("IP {0} successfully unblocked".format(ip))
				logging.info("IP {0} successfully unblocked".format(ip))
				return "ok"
			else:
				print("IP {0} unsuccessfully unblocked".format(ip))
				logging.error("IP {0} unsuccessfully unblocked".format(ip))
				return "ko"
		except Exception as e:
			print(e)
			return "ko"
	elif ip_status == "unblocked":
		print("Ip {0} is not blocked".format(ip))
		logging.error("Ip {0} is not blocked".format(ip))
		return "Ip {0} is not blocked".format(ip)


# Function for check if an IP is already or not blocked
def check_if_ip_is_blocked(ip):
	script = "/sbin/iptables -L | grep " + ip
	try:
		result = subprocess.call(script, shell=True)
	# If result = 0 the ip is already blocked, if different the IP is not blocked yet
		if result == 0:
			return "blocked"
		else:
			return "unblocked"
	except Exception as e:
		print(e)
		return "ko"


# Function for retrieve the complete list of blocked IPs
def get_blocked_ip():
	script = "/sbin/iptables -L INPUT -v -n"
	p = subprocess.Popen(script, stdin=subprocess.PIPE, shell=True)
	blocked_ip = p.communicate()[0]
	print(blocked_ip)
	return blocked_ip


# Get the location of the IP. This can be useful to filter incoming connections by country
def locate_ip(ip):
	# We use a free and open API to get the IP location on json format
	url = "https://geoip-db.com/json/" + ip
	response = requests.get(url=url)
	data = response.json()
	return data


# Function to get report from IP
def reverse_nmap(ip):
	# If wanted, we can perform a nmap to incoming IP connection to retrieve some (useful) info about it
	return "report nmap"



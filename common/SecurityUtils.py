import logging
import subprocess
import requests
import re


# Function for block an IP
def block_ip(ip):
	# Check if ip is already blocked
	ip_status = check_if_ip_is_blocked(ip=ip)
	if ip_status == "blocked":
		print("Ip {0} is already blocked".format(ip))
		logging.error("Ip {0} is already blocked".format(ip))
		return "Ip {0} is already blocked".format(ip)
	elif ip_status == "unblocked":
		try:
			add_ip_nftables(ip=ip)
			script = "cp linux_files/nftables.cfg /etc/firewall/"
			result = subprocess.call(script, shell=True)
			if result != 0:
				print("Failed to setup block IP {0}".format(ip))
				logging.error("Failed to block IP {0}".format(ip))
				return "ko"
			script = "systemctl restart firewall.service"
			result = subprocess.call(script, shell=True)
			if result == 0:
				print("Nftables is successfully started")
				logging.info("Nftables is successfully started")
				result = check_if_ip_is_blocked(ip=ip)
				if result == "blocked":
					print("IP {0} correctly blocked".format(ip))
					logging.info("IP {0} correctly blocked".format(ip))
					return "ok"
				elif result == "unblocked":
					print("IP {0} not blocked correctly".format(ip))
					logging.error("IP {0} not blocked correctly".format(ip))
					return "ko"
			else:
				print("Nftables isn't correctly started")
				logging.error("Nftables isn't correctly started")
				return "ko"
		except Exception as e:
			print(e)
			return "ko"


# Function for search variable and replace it
def add_ip_nftables(ip):
	filename = "linux_files/nftables.cfg"
	key = "IP_RANGE"
	f = open(filename, "r")
	lines = f.readlines()
	f.close()
	for i, line in enumerate(lines):
		if line.split('=')[0] == key:
			ips = line.split('=')[1].replace("\"", "").replace("\n", "")
			if "." not in ips:
				lines[i] = key + '=' + "\"{ " + ip + " }\"" + "\n"
			else:
				lines[i] = key + '=' + "\"{ " + ips + ", " + ip + " }\"" + "\n"
	f = open(filename, "w")
	f.write("".join(lines))
	f.close()


# Delete IP from nftables config
def delete_ip_nftables(ip):
	filename = "linux_files/nftables.cfg"
	key = "IP_RANGE"
	f = open(filename, "r")
	lines = f.readlines()
	f.close()
	for i, line in enumerate(lines):
		if line.split('=')[0] == key:
			ips = line.split('=')[1].replace("\"", "").replace("}", "").replace("{", "").replace(",", " ").replace(ip, "")\
				.replace("\n", "")
			ips = re.sub(" +", ",", ips).rstrip(",")
			if ips.startswith(","):
				ips.replace(",", "", 1)
			if "." in ips:
				lines[i] = key + '=' + "\"{ " + ips + " }\"" + "\n"
			elif "." not in ips:
				lines[i] = key + '=' + "\"{ " + " }\"" + "\n"

	f = open(filename, "w")
	f.write("".join(lines))
	f.close()


# Function for unblock an IP
def unblock_ip(ip):
	# Check if ip is blocked
	ip_status = check_if_ip_is_blocked(ip=ip)
	if ip_status == "blocked":
		try:
			print("Unblocking IP: {0}".format(ip))
			logging.info("Unblocking IP: {0}".format(ip))
			delete_ip_nftables(ip=ip)
			script = "cp linux_files/nftables.cfg /etc/firewall/"
			result = subprocess.call(script, shell=True)
			if result != 0:
				print("Failed to setup block IP {0}".format(ip))
				logging.error("Failed to block IP {0}".format(ip))
				return "ko"
			script = "systemctl restart firewall.service"
			result = subprocess.call(script, shell=True)
			if result == 0:
				print("Nftables is successfully started")
				logging.info("Nftables is successfully started")
				result = check_if_ip_is_blocked(ip=ip)
				if result == "blocked":
					print("IP {0} correctly blocked".format(ip))
					logging.info("IP {0} correctly blocked".format(ip))
					return "ok"
				elif result == "unblocked":
					print("IP {0} not blocked correctly".format(ip))
					logging.error("IP {0} not blocked correctly".format(ip))
					return "ko"
			else:
				print("Nftables isn't correctly started")
				logging.error("Nftables isn't correctly started")
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
	try:
		with open("linux_files/nftables.cfg") as f:
			if ip in f.read():
				return "blocked"
			else:
				return "unblocked"
	except Exception as e:
		print(e)
		return "ko"


# Function for retrieve the complete list of blocked IPs
def get_blocked_ip():
	blocked_ip = ""
	filename = "linux_files/nftables.cfg"
	key = "IP_RANGE"
	f = open(filename, "r")
	lines = f.readlines()
	f.close()
	for i, line in enumerate(lines):
		if line.split('=')[0] == key:
			blocked_ip = line.split('=')[1].replace("\"", "").replace("\n", "")
	return blocked_ip


# Get the location of the IP. This can be useful to filter incoming connections by country
class LocateIp:
	# We use a free and open API to get the IP location on json format
	def __init__(self, ip):
		self.ip = ip
		url = "https://geoip-db.com/json/" + self.ip
		response = requests.get(url=url)
		self.data = response.json()

	def country_code(self):
		country_code = self.data['country_code']
		return country_code

	def country_name(self):
		country_name = self.data['country_name']
		return country_name

	def state(self):
		state = self.data['state']
		return state

	def postal(self):
		postal = self.data['postal']
		return postal


# Function to get report from IP
def reverse_nmap(ip):
	# If wanted, we can perform a nmap to incoming IP connection to retrieve some (useful) info about it
	return "report nmap"

import logging
from common.ApiUtils import whiteblocker_process, whiteblocker_unblock#, check_system
from concurrent.futures import ThreadPoolExecutor


def main():
	#check = check_system()
	#if check == "ko":
	#	raise Exception("Iptables is not installed")
	pool = ThreadPoolExecutor(max_workers=2)
	pool.submit(whiteblocker_process)
	pool.submit(whiteblocker_unblock)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("^C received, shutting down service")
		logging.error("^C received, shutting down service")
		exit("Exit")
	except Exception as e:
		print(e)
		logging.error(e)

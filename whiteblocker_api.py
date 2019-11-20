import logging
from common.ApiUtils import whiteblocker_process, whiteblocker_unblock, check_system
from concurrent.futures import ThreadPoolExecutor
from threading import Thread


logging.basicConfig(filename="api.log", filemode="w", format="%(asctime)s %(name)s - %(levelname)s - %(message)s",
					level=logging.INFO)


def main():
	check = check_system()
	if check == "ko":
		raise Exception("Nftables is not installed")
	Thread(target=whiteblocker_process).start()
	Thread(target=whiteblocker_unblock).start()
#	pool = ThreadPoolExecutor(max_workers=1)
#	pool.submit(whiteblocker_process)
#	pool.submit(whiteblocker_unblock)


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

import logging
from common.ApiUtils import whiteblocker_process, whiteblocker_unblock
from concurrent.futures import ThreadPoolExecutor


def main():
	pool = ThreadPoolExecutor(max_workers=2)
	pool.submit(whiteblocker_process)
	pool.submit(whiteblocker_unblock)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("^C received, shutting down the web server")
		logging.error("^C received, shutting down the web server")
		exit("Exit")
	except Exception as e:
		print(e)
		logging.error(e)

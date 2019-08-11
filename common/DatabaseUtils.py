import sqlite3
import logging


# Function for create the DB and table if it's a new installation
def init_db():
	print("Creating DB and tables...")
	logging.info("Creating DB and tables...")
	try:
		conn = sqlite3.connect("whiteblocker.db")
		print("Opened database successfully")
		logging.info("Opened database successfully")
		conn.execute('''CREATE TABLE IF NOT EXISTS RECORD
				(IP               TEXT    NOT NULL,
				TRIES             INT     NOT NULL,
				LOCATION          TEXT,
				CURRENT_STATUS    TEXT,
				BLOCKED_DATE      TEXT,
				UNBLOCKED_DATE    TEXT,
				FIRST_VIEW        TEXT,
				LAST_VIEW         TEXT);''')
		print("Created table successfully")
		logging.info("Created table successfully")
	except Exception as e:
		print(e)
		logging.error(e)


# Function for insert data on DB
def insert_db(ip, tries, location, current_status, first_view, last_view):
	conn = sqlite3.connect("whiteblocker.db")
	try:
		conn.execute("INSERT INTO RECORD \
	(IP,TRIES,LOCATION,CURRENT_STATUS,BLOCKED_DATE,UNBLOCKED_DATE,FIRST_VIEW,LAST_VIEW)	\
	VALUES \
	('{0}', {1}, '{2}', '{3}', 'None', 'None', '{4}', '{5})".format(ip, tries, location, current_status,
															first_view, last_view))
		conn.commit()
		return "ok"
	except Exception as e:
		print(e)
		return "ko"


# Function for delete a row based on IP
def delete_row(ip):
	conn = sqlite3.connect("whiteblocker.db")
	try:
		conn.execute("DELETE from RECORD where IP = '{0}'".format(ip))
		conn.commit()
		return "ok"
	except Exception as e:
		print(e)
		return "ko"


# Function for select all data store in RECORD table from DB
def select_all():
	conn = sqlite3.connect("whiteblocker.db")
	try:
		cursor = conn.execute("SELECT * FROM RECORD")
		lst = cursor.fetchall()
		return lst
	except Exception as e:
		print(e)
		return "ko"


# Function for select data from DB based on custom field
def select_full_custom(field, condition, match):
	conn = sqlite3.connect("whiteblocker.db")
	try:
		cursor = conn.execute("SELECT {0} FROM RECORD where {1} = '{2}'".format(field, condition, match))
		lst = cursor.fetchall()
		return lst
	except Exception as e:
		print(e)
		return "ko"


# Function for update exist row
def update_row(ip, field, value):
	conn = sqlite3.connect("whiteblocker.db")
	try:
		conn.execute("UPDATE RECORD SET '{0}' = '{1}' WHERE IP = '{2}'".format(field, value, ip))
		conn.commit()
		return "ok"
	except Exception as e:
		print(e)
		return "ko"


# Function for drop table
def drop_table():
	conn = sqlite3.connect("whiteblocker.db")
	conn.execute('''DROP TABLE RECORD''')


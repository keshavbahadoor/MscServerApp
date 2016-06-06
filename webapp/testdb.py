import psycopg2
import config
import dataservice
from flask import jsonify

# CONN = psycopg2.connect(None, config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_PORT)
# cursor = CONN.cursor()
#
# cursor.execute('Select * from "SpeetTest" limit 100;')
# records = cursor.fetchall()

# print records

data_service = dataservice.DataService()
data_service.connect()

# Do stuff here with data service



data = data_service.get_user_badges('111006565137014624471')

print data
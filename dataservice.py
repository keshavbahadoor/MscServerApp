import psycopg2
import config

class DataService(object):

    def __init__(self):
        self.CONN = None
        self.cursor = None

    # Establishes connection with database and returns cursor object
    def connect(self):
        try:
            self.CONN = psycopg2.connect(None, config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_PORT)
            self.cursor = self.CONN.cursor()
            return True
        except:
            return False

    # Closes connection to the database
    def close(self):
        try:
            self.cursor.close()
            return True
        except:
            return False

    # Returns All API KEYs
    def get_api_keys(self):
        try:
            self.cursor.execute('Select * from "ApiKey";')
            records = self.cursor.fetchall()
            return records
        except:
            return False

    # Checks to see if passed API KEY exists
    def api_key_exists(self, key):
        try:
            self.cursor.execute('Select * from "ApiKey" where "ApiKey" = \'' + key + '\';')
            if self.cursor.rowcount > 0:
                return True
            return False
        except:
            return False

    # Adds a user's location, speed data
    def add_location_data(self):
        try:

            return True
        except:
            return False





import psycopg2
import config


class DataService(object):

    def __init__(self):
        self.CONN = None
        self.cursor = None

    # Establishes connection with database and returns cursor object
    def connect(self):
        try:
            self.CONN = psycopg2.connect(None, config.DB_NAME, config.DB_USER, config.DB_PASSWORD, config.DB_HOST,
                                         config.DB_PORT)
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
    def add_location_data(self, latitude, longitude, speed):
        try:
            self.cursor.execute('INSERT INTO "SpeetTest"("Latitude", "Longitude", "Speed") '
                                '   VALUES (\'{}\', \'{}\', {});'.format(latitude, longitude, speed))
            self.CONN.commit()
            return True
        except:
            return False

    # Adds GPS data
    def add_gps_data(self, latitude, longitude, speed, userid, timestamp):
        if timestamp is not None:
            sql = 'INSERT INTO "GPSData"("UserID", "Latitude", "Longitude", "Speed", ' \
                  '"TimeStamp") VALUES ({}, \'{}\', \'{}\', {}, \'{}\');'.format(userid, latitude, longitude, speed, timestamp)
        else:
            sql = 'INSERT INTO "GPSData"("UserID", "Latitude", "Longitude", "Speed") VALUES ({}, \'{}\', \'{}\', ' \
                  '{});'.format(userid, latitude, longitude, speed)
        try:
            self.cursor.execute(sql)
            self.CONN.commit()
            return True
        except Exception, e:
            print e
            return False

    # Adds GPS data with weather
    def add_gps_weather_data(self, latitude, longitude, speed, userid, weatherid, rain, windspeed, temperature, pressure, humidity, timestamp):
        if timestamp is not None:
            sql = 'INSERT INTO "GPSData"("UserID", "Latitude", "Longitude", "Speed", ' \
                  '"WeatherID", "Rain", "WindSpeed", "Temperature", "Pressure", "Humidity", ' \
                  '"TimeStamp") VALUES (\'{}\', \'{}\', \'{}\', {}, ' \
                  '{}, {}, {}, {}, {}, {}, \'{}\');'.format(userid, latitude, longitude, speed, weatherid, rain,
                                                            windspeed, temperature, pressure, humidity, timestamp)
        else:
            sql = 'INSERT INTO "GPSData"("UserID", "Latitude", "Longitude", "Speed", ' \
                  '"WeatherID", "Rain", "WindSpeed", "Temperature", "Pressure", "Humidity" ' \
                  ') VALUES (\'{}\', \'{}\', \'{}\', {}, ' \
                  '{}, {}, {}, {}, {}, {});'.format(userid, latitude, longitude, speed, weatherid, rain, windspeed,
                                                    temperature, pressure, humidity)
        try:
            self.cursor.execute(sql)
            self.CONN.commit()
            return True
        except Exception, e:
            print e
            return False

    # Adds sensor data
    def add_acc_sensor_data(self, userid, accx, accy, accz, timestamp):
        if timestamp is not None:
            sql = 'INSERT INTO "AccSensorData"("UserID", "AccX", "AccY", "AccZ", "TimeStamp") ' \
                  'VALUES ({}, {}, {}, {}, \'{}\');'.format(userid, accx, accy, accz, timestamp)
        else:
            sql = 'INSERT INTO "AccSensorData"("UserID", "AccX", "AccY", "AccZ") VALUES ({}, {}, {}, {});'.format(userid, accx, accy, accz)
        try:
            self.cursor.execute(sql)
            self.CONN.commit()
            return True
        except Exception, e:
            print e
            return False

    # Returns all data
    # - For testing purposes- should not use otherwise.
    def get_all_data(self):
        for k in psycopg2.extensions.string_types.keys():
            del psycopg2.extensions.string_types[k]
        try:
            self.cursor.execute('SELECT "Latitude", "Longitude", "Speed", "TimeStamp" '
                                'from "SpeetTest" where "Speed" > 0;')
            data = self.cursor.fetchall()
            return data
        except:
            return False

    # Returns True if user exists, False if otherwise
    def user_exists(self, userid):
        try:
            self.cursor.execute('SELECT COUNT(*) from "User" where "GooglePlusID" = \'{}\';'.format(userid))
            result = self.cursor.fetchone()
            if result[0] == 0:
                return False
            return True
        except Exception, e:
            print e
            return False

    # Adds a google plus user to the User table.
    # Does not check if the user already exists.
    # TODO : add first name and last name
    def add_google_user(self, googleid, email, displayname,  photourl):
         try:
            self.cursor.execute('INSERT INTO "User"("DisplayName", "GooglePlusID", "PhotoURL", "Email") '
                                'VALUES (\'{}\', \'{}\', \'{}\', \'{}\');'.format(displayname, googleid, photourl, email))
            self.CONN.commit()
            return True
         except Exception, e:
            print e
            return False

    # Gets all driving Ids per supplied user
    def get_driving_events(self, googleid):
        try:
            self.cursor.execute('Select * from "DrivingEvent" where "GoogleID" = \'{}\';'.format(googleid))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Adds driving event score
    def insert_driving_event_score(self, googleid, score):
        try:
            self.cursor.execute('INSERT INTO "DrivingEvent"( "Score",  "GoogleID") VALUES ({}, \'{}\' );'.format(score, googleid))
            self.CONN.commit()
            return True
        except Exception, e:
            print e
            return False

    # Returns all users except the current user that is accessing data
    def get_all_users(self, googleid):
        try:
            self.cursor.execute('Select * from "User" where "GooglePlusID" != \'{}\';'.format(googleid))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Returns all badges assigned to user
    def get_user_badges(self, googleid):
        try:
            self.cursor.execute('Select * from "Badge" where "UserID" = \'{}\';'.format(googleid))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Returns all badges
    def get_feed(self):
        try:
            self.cursor.execute('Select "BadgeName", "BadgeID", "TimeStamp", "DisplayName", "PhotoURL" '
                                'from "Badge" '
                                'join "User" on "User"."GooglePlusID" = "Badge"."UserID" '
                                'order by "TimeStamp" desc ;')
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Adds user badge
    def insert_badge(self, googleid, badgeid, badgename, timestamp):
        try:
            self.cursor.execute('INSERT INTO "Badge"( "BadgeName",  "BadgeID", "TimeStamp", "UserID") '
                                'VALUES (\'{}\', {}, \'{}\', \'{}\' );'.format(badgename, badgeid, timestamp, googleid))
            self.CONN.commit()
            return True
        except Exception, e:
            print e
            return False

    # Returns all user activity for a specific user
    # TODO : add limits
    def get_user_activity(self, googleid):
        try:
            self.cursor.execute('Select * from "UserActivity" where "UserID" = \'{}\';'.format(googleid))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Returns all user activity for all users except current user
    # TODO : add limits
    def get_user_activity_all(self, googleid):
        try:
            self.cursor.execute('Select * from "UserActivity" where "UserID" != \'{}\';'.format(googleid))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Adds user activity
    def insert_user_activity(self, googleid, activitydetail, icon):
        try:
            self.cursor.execute('INSERT INTO "UserActivity"( "ActivityDetail",  "UserID", "IconID") '
                                'VALUES (\'{}\', \'{}\', {} );'.format(activitydetail, googleid, icon))
            self.CONN.commit()
            return True
        except Exception, e:
            print e
            return False

    # Gets gps data
    def get_gpsdata(self, googleid, limit):
        try:
            self.cursor.execute('Select * from "GPSData" where "UserID" = \'{}\''
                                'order by "GPSDataID" desc '
                                'limit {};'.format(googleid, limit))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Gets gps data
    def get_gpsdata_limit(self, limit):
        try:
            self.cursor.execute('Select * from "GPSData"  '
                                'order by "GPSDataID" desc '
                                'limit {};'.format(limit))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Gets all gps data by date
    def get_gpsdata_date(self, date):
        try:
            self.cursor.execute('Select * from "GPSData" where "TimeStamp"::date = \'{}\''
                                'order by "GPSDataID" desc ;'.format(date))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Gets all gps data by date
    def get_accdata_date(self, date):
        try:
            self.cursor.execute('Select * from "AccSensorData" where "TimeStamp"::date = \'{}\''
                                'order by "AccSensorID" desc ;'.format(date))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Gets user score
    def get_score(self, googleid):
        try:
            self.cursor.execute('Select "Score" from "User" where "GooglePlusID" = \'{}\';'.format(googleid))
            records = self.cursor.fetchall()
            return records
        except Exception, e:
            print e
            return False

    # Updtes user score
    def update_score(self, googleid, score):
        try:
            self.cursor.execute('UPDATE "User" '
                                'SET "Score" = {} '
                                'where "GooglePlusID" = \'{}\';'.format(score, googleid))
            self.CONN.commit()
            return True
        except Exception, e:
            print e
            return False


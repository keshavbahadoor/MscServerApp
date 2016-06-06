import dataservice
from numpy import array
from collections import namedtuple
import numpy
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans2, whiten
from sklearn.cluster import KMeans
import warnings
import datetime
from itertools import groupby

# Suppress warnings
warnings.filterwarnings('ignore')

# Define arrays and variables
Data = namedtuple('Data', 'lat lon speed timestamp userid weatherid rain wind temp pressure humidity kmeans_region')
AccData = namedtuple('AccData', 'x y z userid')
user_dict = {}
geodata = []
tuple_data = []
tuple_acc = []
region0 = []
region1 = []
region2 = []
region3 = []
region4 = []
region5 = []
region6 = []
CLUSTER_SIZE = 6

data_service = dataservice.DataService()
data_service.connect()


# ----------------------------------------------------------------------------------------|
# Loads all users into a dictionary
# ----------------------------------------------------------------------------------------|
def load_users():
    db_users = data_service.get_all_users('')
    for user in db_users:
        user_dict[user[4]] = {'positive': 0, 'negative': 0, 'acc_pos': 0, 'acc_neg': 0, 'max_speed': 0.0}


# ----------------------------------------------------------------------------------------|
# Loads acceleration data
# ----------------------------------------------------------------------------------------|
def load_acc_data(date):
    db_acc = data_service.get_accdata_date(date)
    for row in db_acc:
        tuple_acc.append(AccData(float(row[1]),
                                 float(row[2]),
                                 float(row[3]),
                                 row[5]))


# ----------------------------------------------------------------------------------------|
# loads all gps data for a given day
# ----------------------------------------------------------------------------------------|
def load_gpsdata(date):
    data = data_service.get_gpsdata_date(date)
    for cols in data:
        geodata.append([float(cols[1]), float(cols[2])])
        speed = float(cols[3])*3.6
        tuple_data.append(Data(float(cols[1]),
                               float(cols[2]),
                               speed,
                               cols[4],         # date
                               cols[5],         # userid
                               int(cols[6]),    # weather
                               int(cols[7]),    # rain
                               float(cols[8]),  # wind
                               float(cols[9]),  # temp
                               float(cols[10]),  # pressure
                               float(cols[11]),  # humidity
                               None))

        if speed > user_dict[cols[5]]['max_speed']:
            user_dict[cols[5]]['max_speed'] = speed


# ----------------------------------------------------------------------------------------|
# For the given model, a k-means graph is plotted
# ----------------------------------------------------------------------------------------|
def plot_kmeans_model(model, arr):
    plt.figure(figsize=(8, 6))
    plt.scatter(arr[:, 0], arr[:, 1], c=model.labels_.astype(float), marker='+')
    plt.show()


# ----------------------------------------------------------------------------------------|
# Usign the k-means cluster model the data is now filtered by region
# ----------------------------------------------------------------------------------------|
def filter_data_by_region(model):
    for row in tuple_data:
        reg = model.predict([row.lat, row.lon])
        if reg[0] == 1:
            region1.append(row)
        elif reg[0] == 2:
            region2.append(row)
        elif reg[0] == 3:
            region3.append(row)
        elif reg[0] == 4:
            region4.append(row)
        elif reg[0] == 5:
            region5.append(row)
        elif reg[0] == 6:
            region6.append(row)
        elif reg[0] == 0:
            region0.append(row)


# ----------------------------------------------------------------------------------------|
# For each given region, the data is separated by time.
# a predefined incremental time is used, typically 4 hours
# ----------------------------------------------------------------------------------------|
def filter_data_by_time(array):
    print 'filtering by time. Array size: {}'.format(array.__len__())
    subarr = []
    hour = 0
    hour_increment = 4
    while hour <= 24:
        for row in array:
            if row.timestamp.hour >= hour and row.timestamp.hour < (hour + hour_increment):
                subarr.append(row)
        hour += hour_increment
        if subarr.__len__() > 0:
            process_region_time_data(subarr)
        del subarr[:]


# ----------------------------------------------------------------------------------------|
# This function takes data that is broken down into a region and time
#   This data is then processed for any outliers
# ----------------------------------------------------------------------------------------|
def process_region_time_data(arr):
    data = []
    for row in arr:
        data.append(row.speed)

    data = array(data)
    q75, q25 = numpy.percentile(data, [75, 25])
    IQR = q75 - q25

    print '\n\nQ75 = {} '.format(q75)
    print 'Q25 = {} '.format(q25)

    for row in arr:
        score_user(row, q75, q25, IQR)


# ---------------------------------------------------------------------------------
#  return values based on weather
# ---------------------------------------------------------------------------------
def evaluate_weather_score(weatherid, rain):
    score = 0
    if weatherid > 960 or (902 >= weatherid >= 900):
        score += 100
    if weatherid == 202 or weatherid == 232:
        score += 40
    if 312 <= weatherid <= 321:
        score += 45
    # Rain
    if weatherid == 501:
        score += 20
    if weatherid == 502 and weatherid == 531:
        score += 40
    if weatherid == 503 and weatherid == 520:
        score += 80
    if weatherid == 504 and weatherid == 522:
        score += 200
    return score

# ---------------------------------------------------------------------------------
#  Score the user
# ---------------------------------------------------------------------------------
def score_user(row, q75, q25, IQR):

    if (row.speed - q75) > 1.5*IQR:
        print '{} is a mid outlier'.format(row.speed)
        user_dict[row.userid]['negative'] += (5 + evaluate_weather_score(row.weatherid, row.rain))

    elif (row.speed-q75) > 3.0*IQR:
        print '{} is an extereme outlier'.format(row.speed)
        user_dict[row.userid]['negative'] += (15 + evaluate_weather_score(row.weatherid, row.rain))

    else:
        user_dict[row.userid]['positive'] += 1

# ---------------------------------------------------------------------------------
#  process acc
# ---------------------------------------------------------------------------------
def process_acc_data():
    data = []
    for row in tuple_acc:
        data.append([row.x, row.y, row.z])

    data = array(data)
    q75, q25 = numpy.percentile(data, [75, 25])
    IQR = q75 - q25

    print '\n\nQ75 = {} '.format(q75)
    print 'Q25 = {} '.format(q25)

    for row in tuple_acc:
        if ((abs(row.x-q75) > 1.5*IQR) or
           (abs(row.y-q75) > 1.5*IQR) or
           (abs(row.z-q75) > 1.5*IQR)):
            # print 'Mid Outlier: {} {} {}'.format(row.x, row.y, row.z)
            user_dict[row.userid]['acc_neg'] += 1

        elif ((abs(row.x-q75) > 3.0*IQR) or
              (abs(row.y-q75) > 3.0*IQR) or
              (abs(row.z-q75) > 3.0*IQR)):
            # print 'Extreme Outlier: {} {} {}'.format(row.x, row.y, row.z)
            user_dict[row.userid]['acc_neg'] += 2

        else:
            user_dict[row.userid]['acc_pos'] += 1

# ---------------------------------------------------------------------------------
#       MAIN
# ---------------------------------------------------------------------------------
print 'Starting processing of data'


date = '2016-03-13'
load_users()
load_gpsdata(date)
load_acc_data(date)
print 'Amount of gps data: {}'.format(geodata.__len__())
print 'Amount of Acc data: {}'.format(tuple_acc.__len__())

# PROCESS ACCELEROMETER DATA
if tuple_acc.__len__() > 1:
    process_acc_data()
else:
    print 'No Acceleration data'

# PROCESS GPS DATA
if geodata.__len__() >= CLUSTER_SIZE:

    # create kmeans model
    npgeo = array(geodata)
    model = KMeans(n_clusters=CLUSTER_SIZE)
    model = model.fit(npgeo)

    # plot_kmeans_model(model, npgeo)

    filter_data_by_region(model)
    filter_data_by_time(region0)
    filter_data_by_time(region1)
    filter_data_by_time(region2)
    filter_data_by_time(region3)
    filter_data_by_time(region4)
    filter_data_by_time(region5)


else:
    print 'data less than 6 rows'

for key in user_dict:
    print key, 'corresponds to', user_dict[key]
    if user_dict[key]['positive'] > 0 and user_dict[key]['negative'] == 0:
        print 'shining star'
        data_service.insert_badge(key, 1, 'Shining Star', date)

    if user_dict[key]['acc_pos'] > 0 and user_dict[key]['acc_neg'] == 0:
        print 'smooth rider'
        data_service.insert_badge(key, 4, 'Smooth Rider', date)

    if user_dict[key]['max_speed'] > 0 and user_dict[key]['max_speed'] < 80.0:
        print 'super 80 badge'
        data_service.insert_badge(key, 2, 'Super 80', date)

    score = data_service.get_score(key)
    r_score = [x[0] for x in score]
    print 'score: {} '.format(r_score[0])
    r_score[0] += user_dict[key]['positive']
    r_score[0] += user_dict[key]['acc_pos']
    data_service.update_score(key, r_score[0])























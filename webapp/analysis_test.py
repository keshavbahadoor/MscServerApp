import os
import io
import dataservice
from numpy import array
from collections import namedtuple
import numpy
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans2, whiten
from sklearn.cluster import KMeans
import datetime
from itertools import groupby

# Define arrays and variables
Data = namedtuple('Data', 'lat lon speed timestamp userid weatherid rain wind temp pressure humidity kmeans_region')
geodata = []
tuple_data = []
region0 = []
region1 = []
region2 = []
region3 = []
region4 = []
region5 = []
region6 = []

data_service = dataservice.DataService()
data_service.connect()


# Load data from csv file. This populates both the tuple data array and the geodata
# Geo data array is used for building the model
# TODO can use one array
def read_file(path):
    arr = []
    f = io.open(path, 'r')
    count = 0
    for line in f:
        if count > 0:
            cols = line.split(',')
            # geo data
            geodata.append([float(cols[1]), float(cols[2])])

            # speed data
            speed = float(cols[3])*3.6
            if speed > 0:
                arr.append(speed)
                tuple_data.append(Data(float(cols[1]),
                                       float(cols[2]),
                                       speed,
                                       datetime.datetime.strptime(cols[4], '%Y-%m-%d %H:%M:%S.%f'),
                                       cols[5],         # userid
                                       int(cols[6]),    # weather
                                       int(cols[7]),    # rain
                                       float(cols[8]),  # wind
                                       float(cols[9]),  # temp
                                       float(cols[10]),  # pressure
                                       float(cols[11]),  # humidity
                                       None))
        count += 1
    f.close()
    return array(arr)


# Usign the kmeans cluster model the data is now filtered by region
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
            calc_percentile(subarr)
        del subarr[:]



# Plot the kmeans model
def plot_kmeans_model(model, npgeo):
    plt.figure(figsize=(8, 6))
    plt.scatter(npgeo[:, 0], npgeo[:, 1], c=model.labels_.astype(float), marker='+')
    plt.show()


def calc_percentile(arr):
    data = []
    for row in arr:
        data.append(row.speed)

    data = array(data)
    q75, q25 = numpy.percentile(data, [75, 25])
    IQR = q75 - q25

    print '\n\nQ75 = {} '.format(q75)
    print 'Q25 = {} '.format(q25)

    for row in arr:
        if (row.speed-q75) > 1.5*IQR:
            print '{} is a mid outlier'.format(row.speed)
            score = (q25 / row.speed) * 12.5
            print 'mid score = {}'.format(score)
            data_service.insert_driving_event_score(row.userid, score)
        if (row.speed-q75) > 3.0*IQR:
            print '{} is an extereme outlier'.format(row.speed)
            score = (q75 / row.speed) * 10
            print 'score = {}'.format(score)
            data_service.insert_driving_event_score(row.userid, score)

print 'Testing Data analyis stuff'

data = read_file('C:\Users\Keshav\Desktop\msc\data and statics\gpsdatadump3.csv')

# q75, q25 = numpy.percentile(data, [75, 25])
# IQR = q75 - q25
# print q75
# print q25

# x = 160.24
#
# if abs(x-q75) > 1.5*IQR:
#     print '{} is a mid outlier'.format(x)
#
# if abs(x-q75) > 3.0*IQR:
#     print '{} is an extereme outlier'.format(x)



# create kmeans model
npgeo = array(geodata)
model = KMeans(n_clusters=6)
model = model.fit(npgeo)
print model.labels_

arr = [[11.52587433729828, -61.4113577915120]]
a = model.predict(arr)
print a[0]


filter_data_by_region(model)

filter_data_by_time(region0)
filter_data_by_time(region1)
filter_data_by_time(region2)
filter_data_by_time(region3)
filter_data_by_time(region4)
filter_data_by_time(region5)










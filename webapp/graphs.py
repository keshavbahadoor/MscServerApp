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
# loads all gps data for a given day
# ----------------------------------------------------------------------------------------|
def load_gpsdata(limit):
    data = data_service.get_gpsdata_limit(limit)
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



# ----------------------------------------------------------------------------------------|
# For the given model, a k-means graph is plotted
# ----------------------------------------------------------------------------------------|
def plot_kmeans_model(model, arr):
    plt.figure(figsize=(8, 6))
    plt.scatter(arr[:, 0], arr[:, 1], c=model.labels_.astype(float), marker='+')
    plt.xlabel('Latitude', fontsize=18)
    plt.ylabel('Longitude', fontsize=18)
    plt.show()


# ---------------------------------------------------------------------------------
#       MAIN
# ---------------------------------------------------------------------------------
print 'Starting processing of data'


load_gpsdata('4000')

# PROCESS GPS DATA
if geodata.__len__() >= CLUSTER_SIZE:

    # create kmeans model
    npgeo = array(geodata)
    model = KMeans(n_clusters=CLUSTER_SIZE)
    model = model.fit(npgeo)

    plot_kmeans_model(model, npgeo)



else:
    print 'data less than 6 rows'
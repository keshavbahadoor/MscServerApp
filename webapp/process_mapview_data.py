import dataservice
from collections import namedtuple
import warnings

data_service = dataservice.DataService()
data_service.connect()

# Suppress warnings
warnings.filterwarnings('ignore')

# Define arrays and variables
LatLonData = namedtuple('Data', 'lat lon')
userlatlon = {}

def load_gpsdata(date):
    data = data_service.get_gpsdata_date(date)
    for cols in data:
        if cols[5] not in userlatlon:
            userlatlon[cols[5]] = []
        userlatlon[cols[5]].append(LatLonData(float(cols[1]),
                                              float(cols[2])))

def load_badges():
    data = data_service.get_badges_all()
    for cols in data:
        print cols


print 'starting processing for mapview'
date = '2016-03-13'
load_gpsdata(date)

print userlatlon

print 'process finished'
# author Luis Castillo 2017

from flask import Flask
from flask import request
from flask import render_template

from datetime import date
from math import cos
from math import radians
from urllib import urlencode
import urllib2
import json

DOMAIN = 'http://api.geonames.org/'
USERNAME = 'lach'
RADIUS = 20 # 10km of radius
oneDegree = 111.12 # kms : 60 nautical miles

app = Flask(__name__)

def fetchJson(method, params):
    uri = DOMAIN + '{}?{}&username={}'.format(method, urlencode(params), 
                                              USERNAME)
    resource = urllib2.urlopen(uri).readlines()
    js = json.loads(resource[0])
    return js

def getLocation(location):
    # import pdb; pdb.set_trace()
    method = 'searchJSON'
    params = {'q': location, 'maxRows': 1}
    js = fetchJson(method, params)
    # import pdb; pdb.set_trace()
    if js['totalResultsCount'] == 0:
        return None, None
    lat = js['geonames'][0]['lat']
    lng = js['geonames'][0]['lng']
    return lat, lng # return dictionary

def getEarthquakes(north, south, east, west):
    # import pdb; pdb.set_trace()
    method = 'earthquakesJSON'
    params = {'north': north, 'south': south, 'east': east, 'west': west}
    js = fetchJson(method, params)
    earthquakes = js['earthquakes']
    count = 0
    for i in earthquakes:
        count += 1
        i['index'] = count
    return earthquakes # return dictionary

def getLocationName(lat, lng):
    method = 'findNearbyPlaceNameJSON'
    params = {'lat': lat, 'lng': lng}
    js = fetchJson(method, params)
    #import pdb; pdb.set_trace()
    return js['geonames'][0]['name']

# http://api.geonames.org/findNearbyPlaceNameJSON?lat=47.3&lng=9&username=demo 

def getLargestEarthquakes():
    # the world goes from -180 to 180 degrees west to east,
    # and -90 to 90 south to north
    north = 90
    east = 180
    west = -180
    south = -90
    today = date.today().isoformat()
    method = 'earthquakesJSON'
    params = {'north': north, 'south': south, 'east': east, 'west': west,
             'minMagnitude':7, 'date': today}
    js = fetchJson(method, params)
    earthquakes = js['earthquakes']
    for eq in earthquakes:
        try:
            eq['name'] = getLocationName(eq['lat'], eq['lng'])
        except IndexError:
            eq['name'] = 'NA'
    return earthquakes

topEarthquakes = getLargestEarthquakes()

def latLngToCoordinates(lat, lng):
    # North-South -> latitude
    # one degree of latitude is invariably a distance of 60 nautical miles
    # or 111.12 km
    north = lat + (RADIUS/oneDegree)
    south = lat - (RADIUS/oneDegree)
    # East-West -> longitude
    east = lng + (RADIUS/oneDegree)/cos(radians(lat))
    west = lng - (RADIUS/oneDegree)/cos(radians(lat))
    return north, south, east, west



@app.route('/')
def my_form():
    return render_template('map.html', earthquakes={},
                            topEarthquakes=topEarthquakes, 
                            lat=19.53124, lng=-96.91589, location='Welcome!')

@app.route('/', methods=['POST'])
def my_form_post():
    # import pdb; pdb.set_trace()
    text = request.form['text']
    lat, lng = getLocation(text.replace(' ',''))
    if lat is None and lng is None:
        return render_template('map.html', earthquakes={},
                            topEarthquakes=topEarthquakes, 
                            lat=19.53124, lng=-96.91589, 
                            location='No place found!')
    else:
        coord = latLngToCoordinates(float(lat), float(lng))
        earthquakes = getEarthquakes(coord[0], coord[1], coord[2], coord[3])
        # return str(earthquakes)
        # import pdb; pdb.set_trace()
        return render_template('map.html', earthquakes=earthquakes,
                                topEarthquakes=topEarthquakes, 
                                lat=lat, lng=lng, location=text)


if __name__ == '__main__':
    app.run(debug=True)

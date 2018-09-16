# coding: utf-8

from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
import json
import requests
import urllib.request
from urllib.request import Request, urlopen

app = Flask(__name__, template_folder="templates")

app.config['GOOGLEMAPS_KEY'] = "AIzaSyAYnlWxEoOaBVFkv6VijmIEZ1pumZfhFoA"
GoogleMaps(app, key="AIzaSyAYnlWxEoOaBVFkv6VijmIEZ1pumZfhFoA")
API_KEY = "AIzaSyAYnlWxEoOaBVFkv6VijmIEZ1pumZfhFoA"

REGION_LAT_LNG = dict(east=dict(lat=1.3413, lng=103.9638),
                west=dict(lat=1.3483, lng=103.6831),
                south=dict(lat=1.2957, lng=103.8065),
                north=dict(lat=1.4382, lng=103.7890),
                central=dict(lat=1.36, lng=103.8))

COLOR_CODE = dict(green='#228B22', blue='#4169e1', yellow='#ffcc00', orange='#FF4500', red='#B22222')

@app.route("/")
def psimapview():
    def _get_psi_info(region, psi_json_dict_list):
        return dict(lat=REGION_LAT_LNG[region], lng=REGION_LAT_LNG[region], psi=psi_json_dict_list[0]['items'][0]['readings']['pm25_twenty_four_hourly'][region])
    #end def

    def _check_status(info_dict):
        if info_dict['psi'] <= 50: return ('Healthy', 'green')
        elif info_dict['psi'] <= 100: return ('Moderate', 'blue')
        elif info_dict['psi'] <= 200: return ('Unhealthy', 'yellow')
        elif info_dict['psi'] <= 300: return ('Very Unhealthy', 'orange')
        else: return ('Hazardous', 'red')
    #end def

    psi_response = urllib.request.urlopen('https://api.data.gov.sg/v1/environment/psi', timeout=5)
    psi = [line.decode('utf-8') for line in psi_response]
    psi_json_dict_list = [json.loads(js) for js in psi]

    east_info = _get_psi_info('east', psi_json_dict_list)
    west_info = _get_psi_info('west', psi_json_dict_list)
    south_info = _get_psi_info('south', psi_json_dict_list)
    north_info = _get_psi_info('north', psi_json_dict_list)
    central_info = _get_psi_info('central', psi_json_dict_list)

    east_info['status'], east_info['color'] = _check_status(east_info)
    west_info['status'], west_info['color'] = _check_status(west_info)
    south_info['status'], south_info['color'] = _check_status(south_info)
    north_info['status'], north_info['color'] = _check_status(north_info)
    central_info['status'], central_info['color'] = _check_status(central_info)

    psimap = Map(
        identifier="psimap",
        lat=1.3521,
        lng=103.8198,
        zoom=12,
        region='SG',
        style="height:800px;width:1200px;margin:0;",
        markers=[
            {
                'icon': icons.alpha.E,
                'lat':  east_info['lat'],
                'lng':  east_info['lng'],
                'infobox': "<b style='color:{};'>East PSI: \n {}\n{}</b>".format(COLOR_CODE[east_info['color']], east_info['status'], east_info['psi'])
            },
            {
                'icon': icons.alpha.W,
                'lat':  west_info['lat'],
                'lng':  west_info['lng'],
                'infobox': "<b style='color:{};'>West PSI: \n {}\n{}</b>".format(COLOR_CODE[west_info['color']], west_info['status'], west_info['psi'])
            },
            {
                'icon': icons.alpha.S,
                'lat':  south_info['lat'],
                'lng':  south_info['lng'],
                'infobox': "<b style='color:{};'>South PSI: \n {}\n{}</b>".format(COLOR_CODE[south_info['color']], south_info['status'], south_info['psi'])
            },
            {
                'icon': icons.alpha.N,
                'lat':  north_info['lat'],
                'lng':  north_info['lng'],
                'infobox': "<b style='color:{};'>North PSI: \n {}\n{}</b>".format(COLOR_CODE[north_info['color']], north_info['status'], north_info['psi'])
            },
            {
                'icon': icons.alpha.C,
                'lat':  central_info['lat'],
                'lng':  central_info['lng'],
                'infobox': "<b style='color:{};'>Central PSI: \n {}\n{}</b>".format(COLOR_CODE[central_info['color']], central_info['status'], central_info['psi'])
            }
        ]
    )
    return render_template('psimap.html', psimap=psimap)
#end def


@app.route("/weather")
def weathermapview():
    weather_response = urllib.request.urlopen('https://api.data.gov.sg/v1/environment/2-hour-weather-forecast', timeout=5)
    weather = [line.decode('utf-8') for line in weather_response]
    weather_json_dict_list = [json.loads(js) for js in weather]
    # print(weather_json_dict_list[0]['items'][0]['forecasts'])

    weather_dict = dict()
    for item in weather_json_dict_list[0]['area_metadata']:
        weather_dict[item['name']] = dict(lat=item['label_location']['latitude'], lng=item['label_location']['longitude'])

    for item in weather_json_dict_list[0]['items'][0]['forecasts']:
        weather_dict[item['area']]['forecast'] = item['forecast']

    #create markers
    markers_list = list()
    for area, info_dict in weather_dict.items():
        tmp_dict = dict(icon='http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                        lat=info_dict['lat'],
                        lng=info_dict['lng'],
                        infobox="{} Forecast: \n {}</b>".format(area, info_dict['forecast']))
        markers_list.append(tmp_dict)

    weathermap = Map(
        identifier="weathermap",
        lat=1.3521,
        lng=103.8198,
        zoom=12,
        region='SG',
        style="height:800px;width:1200px;margin:0;",
        markers=markers_list
    )

    return render_template('weathermap.html', weathermap=weathermap)
#end def

@app.route("/shelters")
def sheltermapview():
    shelters_response = Request('https://data.gov.sg/api/action/datastore_search?resource_id=4ee17930-4780-403b-b6d4-b963c7bb1c09', headers={'User-Agent': 'Mozilla/5.0'})
    shelters_response = urlopen(shelters_response).read().decode('utf-8')
    shelters_dict_list = json.loads(shelters_response)['result']['records']

    shelters_dict = dict()
    for item in shelters_dict_list:
        geo_api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(item['address'].replace(" ", "+"), API_KEY))
        geo_api_response_dict = geo_api_response.json()
        if geo_api_response_dict['status'] == 'OK':
            lat = geo_api_response_dict['results'][0]['geometry']['location']['lat']
            lng = geo_api_response_dict['results'][0]['geometry']['location']['lng']
            tmp_dict = dict(address=item['address'],
                postal_code=item['postal_code'],
                description=item['description'],
                lat=lat,
                lng=lng)
        else:
            lat = 0
            lng = 0
            tmp_dict = dict(address=item['address'],
                postal_code=item['postal_code'],
                description=item['description'],
                lat=lat,
                lng=lng)
        #end else

        shelters_dict[item['name']] = tmp_dict
    #end for

    #create markers
    markers_list = list()
    for area, info_dict in shelters_dict.items():
        tmp_dict = dict(icon='http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                        lat=info_dict['lat'],
                        lng=info_dict['lng'],
                        infobox="{}\n Address: {}\n Postal Code: {}\n Description: {}</b>".format(area, info_dict['address'], info_dict['postal_code'], info_dict['description']))
        markers_list.append(tmp_dict)
    #end for

    sheltersmap = Map(
        identifier="sheltersmap",
        lat=1.3521,
        lng=103.8198,
        zoom=12,
        region='SG',
        style="height:800px;width:1200px;margin:0;",
        markers=markers_list
    )

    return render_template('sheltersmap.html', sheltersmap=sheltersmap)
#end def


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
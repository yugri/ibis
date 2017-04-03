import time
from geopy.exc import GeocoderTimedOut

from alchemyapi.alchemyapi import AlchemyAPI
from geopy.geocoders import Nominatim
import json
geolocator = Nominatim()
api = AlchemyAPI()


def del_non_characters(x, del_str='–-—`~!@#$^&*()_+\\|\'":;<>,.?/{}[]=+%0123456789’'):
    """
    Function deletes all non-characters symbols or all characters that you don`t want to have in text
    """
    for i in x:
        if i in del_str:
            x = x[:x.find(i)]+x[x.find(i)+1:]   # Here we delete symbols
    return x


def extract_geo_entities(text):
    text = text.encode(errors='replace').decode('utf-8')
    time.sleep(1) #well... should get rid of it
    all_entities = api.entities('text', text)

    result = []
    try:
        for entity in all_entities['entities']:
            if entity['type'] not in { 'Country', 'City', 'Region' }:
                pass
            result.append({
                'name': del_non_characters(entity['text'].title()),
                'type': entity['type']
            })
    except KeyError:
        pass
    return result


def extract_locations(text):
    coords = []
    for entity in extract_geo_entities(text):
        time.sleep(1)
        try:
            location = geolocator.geocode(entity['name'], timeout=10)
            coords.append({
                'name': location.address,
                'type': entity['type'],
                'latitude': location.latitude,
                'longitude': location.longitude,
                'altitude': location.altitude
            })
        except GeocoderTimedOut as e:
            print('Error: geocode failed on input {} with message {}'.format(entity['name'], e.msg))

    return coords


def extract_keywords(text):
    text = text.encode(errors='replace').decode('utf-8')
    time.sleep(1)
    keyword_list = api.keywords('text', text)
    try:
        return [keyword['text'] for keyword in keyword_list['keywords']]
    except KeyError:
        return None


def convert_to_json(text):
    text = text.encode(errors='replace').decode('utf-8')
    return {
        'keywords': extract_keywords(text),
        'locations': extract_locations(text)
    }



def parse_coordinates(coordinates, return_json=True):
    """
    This function helps us to get locations info from data received from the AlchemyAPI

    Example received data from AlchemyAPI:
    {
     "keywords": ["intermingled careers", "Dnipropetrovsk Oblast"],
     "location": [[45.04, 35.67, 0.0]],
     "geo_entities": ["Dnipropetrovsk", "Lutsk"]
    }
    We operates here with location and geo_entities only as arrays

    :param coordinates: list()
    :param return_json: BOOLEAN
    :return: JSON or dict()
    """

    locations = { 'coordinates': [] }
    for coord in coordinates:
        locations['coordinates'].append({
            'type': coord['type'],
            'address': cord['name'],
            'lat': coord['latitude'],
            'lng': coor['longitude'],
            'primary': True if len(coordinates) == 1 else False
        })

    if return_json:
        return json.dumps(locations)
    else:
        return locations



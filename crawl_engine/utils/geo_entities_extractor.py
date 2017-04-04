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

    result, entity_types = [], set()
    try:
        for entity in all_entities['entities']:
            entity_type = entity['type'].lower()
            if entity_type not in { 'country', 'city', 'region' }:
                pass
            result.append({
                'name': del_non_characters(entity['text'].title()),
                'type': entity_type
            })
            entity_types.add()
    except KeyError:
        pass

    #if city exists, remove country and region
    if 'city' in entity_types:
        for geo_entity in result:
            if geo_entity['type'] != 'city':
                result.remove(geo_entity)


    return result


def extract_locations(text):
    coords = []
    for entity in extract_geo_entities(text):
        try:
            time.sleep(1) #not good, not good
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



def parse_coordinates(coordinates, return_str=True):
    """
    This function helps us to get locations info from data received from the AlchemyAPI

    Example received data from AlchemyAPI:
    [ { 'type': 'Country', 'name': 'Ukraine', 'latitude': 62.0, 'longitude': 56.3 }, ... ]

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

    if return_str:
        return json.dumps(locations)
    else:
        return locations



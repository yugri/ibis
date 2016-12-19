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
    time.sleep(1)
    all_entities = api.entities('text', text)
    try:
        return [del_non_characters(entity['text'].capitalize()) for entity in all_entities['entities'] if entity['type'] == 'Country'
            or entity['type'] == 'City']
    except KeyError:
        return None


def locate_entities(geo_entities):
    coords = list()
    for entity in geo_entities:
        time.sleep(1)
        try:
            location = geolocator.geocode(entity, timeout=10)
        except GeocoderTimedOut as e:
            print("Error: geocode failed on input %s with message %s" % (entity, e.msg))
            location = None
        if location:
            # print(location.latitude, location.longitude)
            coords.append(location)
    return coords


def extract_theme_keywords(text):
    text = text.encode(errors='replace').decode('utf-8')
    time.sleep(1)
    keyword_list = api.keywords('text', text)
    try:
        return [keyword['text'] for keyword in keyword_list['keywords']]
    except KeyError:
        return None


def convert_to_json(text):
    text = text.encode(errors='replace').decode('utf-8')
    try:
        geo_entities = set(sorted(extract_geo_entities(text)))
        return json.dumps({'keywords': extract_theme_keywords(text),
                           'location': [(location.latitude, location.longitude, location.altitude)
                                        for location in locate_entities(geo_entities)
                                        if location is not None],
                           'geo_entities': [entity for entity in geo_entities
                                            if geolocator.geocode(entity) is not None]})
    except TypeError:
        return None


def parse_coordinates(array_coords, array_geo_entities, return_json=True):
    """
    This function helps us to get locations info from data received from the AlchemyAPI

    Example received data from AlchemyAPI:
    {
     "keywords": ["intermingled careers", "Dnipropetrovsk Oblast"],
     "location": [[45.04, 35.67, 0.0]],
     "geo_entities": ["Dnipropetrovsk", "Lutsk"]
    }
    We operates here with location and geo_entities only as arrays

    :param array_coords: list()
    :param array_geo_entities: list()
    :param return_json: BOOLEAN
    :return: JSON or dict()
    """
    locations = {
        'coordinates': [],
        'geo_entity': None
    }
    index = 0
    for item in array_coords:
        lat = item[0]
        lng = item[1]
        point = dict()
        point['lat'] = lat
        point['lng'] = lng
        locations['coordinates'].append(point)
        locations['geo_entity'] = array_geo_entities[index]
        index += 1
    if return_json:
        return json.dumps(locations)
    else:
        return locations


# # Here we have a check of a module
# if __name__ == '__main__':
#     print(convert_to_json('Dnipropetrovsk (Ukrainian: Дніпропетро́вськ , officially Dnipro, Дніпро) or \
# Dnepropetrovsk (Russian: Днепропетро́вск ), is Ukraine\'s fourth largest city, with about one \
# million inhabitants. [3][4][5][6] It is 391 kilometres (243 mi)[7] southeast of the capital Kiev on the Dnieper \
# River, in the south-central part of Ukraine. Dnipropetrovsk is the administrative centre of the Dnipropetrovsk \
# Oblast. Administratively, it is incorporated as a city of oblast significance, the centre of Dnipropetrovsk \
# municipality and extraterritorial administrative centre of Dnipropetrovsk Raion. Population: 997,754 (2013 est.)[8]. \
# Known as Ekaterinoslav (Russian: Екатериносла́в , Ukrainian: Катериносла́в, translit. \
# Katerynoslav) until 1925, the city was formally inaugurated by the Russian Empress Catherine the Great in \
# 1787 as the administrative centre of the newly acquired vast territories of imperial New Russia, including \
# those ceded to Russia by the Ottoman Empire under the Treaty of Istanbul (1774). The city was originally \
# envisioned as the Russian Empire\'s third capital city,[9] after Moscow and Saint Petersburg. A vital industrial \
# centre of Soviet Ukraine, Dnipropetrovsk was one of the key centres of the nuclear, arms, and space industries of \
# the Soviet Union. In particular, it is home to the Yuzhmash, a major space and ballistic missile design bureau and \
# manufacturer. Because of its military industry, Dnipropetrovsk was a closed city[nb 1] until the 1990s. On 19 May \
# 2016 the official name of the city was changed to Dnipro.[10] \
# Dnipropetrovsk is a powerhouse of Ukraine\'s business and politics as the native city for many of the country\'s most \
# important figures. Ukraine\'s politics are still defined by the legacies of Leonid Kuchma, Pavlo Lazarenko and Yuliya \
# Tymoshenko whose intermingled careers started in Dnipropetrovsk.'))

#     print(convert_to_json('To protect your subscription investment, we\'ve instituted a security system to protec \
# against the electronic redistribution of copyrighted IntraFish content. Read more Fishery is first industrial fishery \
#     to earn the stamp in the country.'))

    # j = '{"keywords": ["industrial fishery", "electronic redistribution", "subscription investment", "IntraFish content", "stamp", "security", "country"], "location": [], "geo_entities": []}'
    # d = json.loads(j)
    # print(json.loads(j))

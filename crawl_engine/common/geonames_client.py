import json
import pprint

import requests


class GeonamesClient(object):
    """
    Client for manipulating with Geonames API
    ref: http://www.geonames.org/export/web-services.html
    """
    def __init__(self, query='', max_rows=10):
        self.username = 'ibis'
        self.api_base_url = 'http://api.geonames.org/'
        self.q = query
        self.max_rows = max_rows

    def search(self):
        url = self.api_base_url + 'searchJSON'
        parameters = {
            'username': self.username,
            'q': self.q,
            'maxRows': self.max_rows,
        }
        r = requests.post(
            url,
            data=parameters
        )
        return r

    def result_to_dict(self, result):
        if result and result.status_code == 200:
            geonames = result.json()['geonames']
            return geonames

    def reverse_geoname(self, lat, lng):
        url = self.api_base_url + 'findNearbyPlaceNameJSON'
        parameters = {
            'username': self.username,
            'lat': lat,
            'lng': lng,
        }
        r = requests.post(
            url,
            data=parameters
        )
        return r

    def generate_location_name(self, name, admin_name=None, country_name=None):
        if name and admin_name and country_name:
            return ", ".join([name, admin_name, country_name])
        elif name and country_name and not admin_name:
            return ", ".join([name, country_name])
        else:
            return name

    def generate_integer_id(self, locations):
        id_list = []
        try:
            coords = locations['coordinates']
        except KeyError:
            coords = []
        if len(coords):
            for coordinate in coords:
                try:
                    if coordinate['id']:
                        id_list.append(coordinate['id'])
                except KeyError:
                    pass
            if len(id_list) > 0:
                id_list.sort()
                return id_list[-1] + 1
            else:
                return 1
        else:
            return 1

if __name__ == '__main__':
    cli = GeonamesClient('Lutsk')
    r = cli.reverse_geoname(41, 52)
    print(r)
    if r:
        d = cli.result_to_dict(r)
        pprint.pprint(d, indent=4)


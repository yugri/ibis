import time, json

from alchemyapi.alchemyapi import AlchemyAPI


api = AlchemyAPI()

def del_non_characters(x, del_str='–-—`~!@#$^&*()_+\\|\'":;<>,.?/{}[]=+%0123456789’'):
    """
    Function deletes all non-characters symbols or all characters that you don`t want to have in text
    """
    for i in x:
        if i in del_str:
            x = x[:x.find(i)]+x[x.find(i)+1:]   # Here we delete symbols
    return x


def extract_locations(text):
    text = text.encode(errors='replace').decode('utf-8')
    time.sleep(1) #well... should get rid of it
    all_entities = api.entities('text', text)

    result, entity_types = [], set()
    try:
        for entity in all_entities['entities']:
            entity_type = entity['type'].lower()
            if entity_type not in { 'country', 'city', 'region' }:
                continue
            result.append({
                'name': del_non_characters(entity['text'].title()),
                'type': entity_type
            })
            entity_types.add(entity_type)
    except KeyError:
        pass

    #if city exists, remove country and region
    if 'city' in entity_types:
        for geo_entity in result:
            if geo_entity['type'] != 'city':
                result.remove(geo_entity)


    return result


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





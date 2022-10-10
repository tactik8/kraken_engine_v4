
import requests
import json

schema = {}
schema_ref = {}
schemas = {}


record_type_db = {}
normalized_record_type_db = {}

keys_db = {}    
normalized_keys_db = {}





def retrieve_attributes():
    """Retrieves attributes from schema_org
    """
    url = 'https://schema.org/version/latest/schemaorg-current-https.jsonld'
    r = requests.get(url)

    data = r.json()

    for i in data.get('@graph', []):
        schema_id = i.get('@id', None)
        schema[schema_id] = i 

    return schema




def get_properties():
    """Download schema_org vocabulary definition file data
    """

    global schema
    global schema_ref

    if schema and schema is not None:        
        return


    url = 'https://schema.org/version/latest/schemaorg-current-https.jsonld'
    r = requests.get(url)

    data = r.json()

    for i in data.get('@graph', []):
        schema_id = i.get('@id', None)
        schema[schema_id] = i 


    return schema



    # Initialize db records
    for i in schema.keys():

        if schema[i].get('@type', None) == 'rdf:Property':
            keys_db[i] = schema[i]
            normalized_i = i.lower().replace('schema:', '')
            normalized_keys_db[normalized_i] = i


        elif schema[i].get('@type', None) == 'rdfs:Class':
            record_type_db[i] = schema[i]
            normalized_i = i.lower().replace('schema:', '')
            normalized_record_type_db[normalized_i] = i


    return 



def get_schema( record_type):
    """Download schema.org schema for a specific entity (product, person, etc)
    """

    if not record_type:
        return False

    short_record_type = record_type.replace('schema:', '')

    if schemas.get(record_type, None):
        return True

    try:
        url = url = 'https://schema.org/' + short_record_type

        r = requests.get(url, timeout=5)

        text = r.text


        # Separate jsonld
        text = text.split('<script type="application/ld+json">')[1]
        text = text.split('</script>')[0]


        # Laod as json object
        new_s = json.loads(text)

        # store in dict
        schemas[record_type] = {}
        for i in new_s['@graph']:
            record_id = i.get('@id', None)
            schemas[record_type][record_id] = i

        return schemas[record_type]

    except:
        return False




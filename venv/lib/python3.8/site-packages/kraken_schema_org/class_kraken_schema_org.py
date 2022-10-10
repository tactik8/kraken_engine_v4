import requests
import json
from kraken_schema_org import schema_org_data  
from kraken_schema_org import schema_org_transform 


"""
Method to clean data following schema.org format
"""


global schema       # Dict with schema.org vocabulary definition files
global schema_ref   # Dict with keys in lowercase and missing schema:
global schemas      # Dict with full record for each schema


global class_db   # Contains record types (product, etc)
class_db = {}

global normalized_class_db
normalized_class_db = {}

global properties_db          # Contains attreibutes (url, givenname, etc)
properties_db = {}

global normalized_properties_db          
normalized_properties_db = {}

schema = {}
schema_ref = {}
schemas = {}


class Schema_org:

    """
    methods:
        get_clean_record_type: returns standardized record_type
        get_clean_key: returns standardized key
        get_keys: returns all keys for a record_type
        get_data_type: returns datatype for a given key (text, number, etc)

    """

    def __init__(self):

        attributes = schema_org_data.get_properties()

        self.class_db = schema_org_transform.transform_class(attributes)
        self.normalized_class_db = normalized_class_db

        self.attributes = schema_org_data.get_properties()
        
        self.schema = schema
        self.schema_ref = schema_ref


        if not normalized_class_db:
            self._download_data2()



    """
    API
    """

    def normalize_record_type(self, record_type):

        return self._get_clean_record_type(record_type)



    def normalize_key(self, key):
        """Given a record_type and key, returns clean key
        """
        return self._get_clean_key(key)


    def get_keys(self, record_type):
        """Returns all keys for a given record_type
        """
        return self._get_keys(record_type)
    
    def get_datatype(self, record_type, key):
        """Given a key, returns the datatype (text, number, entity, etc)
        """
        return self._get_data_type(record_type, key)


    """
    Methods - Main
    """

    def _get_clean_record_type(self, record_type):
        """Returns the clean type of the schema
        """

        if not record_type or not isinstance(record_type, str):
            return None
        
        record_type = record_type.strip()
        record_type = record_type.replace('schema:', '')
        record_type = record_type.replace('_', '')
        record_type = record_type.lower()

        clean_record_type = normalized_class_db.get(record_type, None)

        return clean_record_type



    def _get_keys(self, record_type):

        return self._get_keys_for_record_type(record_type)



    def _get_clean_key(self, key):


        normalized_key = key.lower().replace('schema:', '')

        # Find equivalent key
        key = normalized_properties_db.get(normalized_key, None)
        
        return key


    def _get_data_type(self, record_type, key):
        """Given a key, returns the datatype (text, number, entity, etc)
        """

        key = self._get_clean_key(key)

        datatype = self.schema.get(key, {}).get('schema:rangeIncludes', None)

        if not datatype:
            return None

        if type(datatype) is not list:
            datatype = [datatype]

        datatypes = []
        for i in datatype:
            d = i.get('@id', None)
            if d:
                datatypes.append(d)

        return datatypes




    """
    Methods
    """



    def _get_keys_for_record_type(self, record_type):
        """Return all the ksys for a given record_type
        """
        record_type = self._get_clean_record_type(record_type)

        if not self._get_schema_from_schema_org(record_type):
            return None

        keys = list(schemas.get(record_type, {}).keys())        
        return keys


    """
    Methods to retrieve data from schema.org
    """

    def _download_data2(self):
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
    

        # Initialize db records
        for i in schema.keys():

            if schema[i].get('@type', None) == 'rdf:Property':
                properties_db[i] = schema[i]
                normalized_i = i.lower().replace('schema:', '')
                normalized_properties_db[normalized_i] = i


            elif schema[i].get('@type', None) == 'rdfs:Class':
                class_db[i] = schema[i]
                normalized_i = i.lower().replace('schema:', '')
                normalized_class_db[normalized_i] = i




    def _get_schema_from_schema_org(self, record_type):
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

            return True

        except:
            return False





#import kraken_db_api
from kraken_engine.class_observation import Observation
from kraken_engine.decorators import error_log
import datetime
import uuid
import json
import kraken_schema_org as norm 

METADATA_TERMS = ['credibility','datasource','agent','instrument','object', 'result', 'start_time', 'end_time', 'valid']


cache_types = {}


class Entity:


    def __init__(self, record_type = None, record_id = None):


        self.record_type = record_type
        self.record_id = record_id

        if not self.record_id:
            self.record_id = str(uuid.uuid4())



        # Store observations from / to database
        self._observations = []

        # Store related entities (nested entities)
        self._related = []

    def __lt__(self, other):

        if self.created_date < other.created_date:
            return True

        return False


    def __add__(self, other):
        """Add observations of other, change record_type and id if necessary
        """
        if not isinstance(other, Entity):
            return self

        for i in other._observations:
            if i not in self._observations:
                i.record_type = self.record_type
                i.record_id = self.record_id
                self._observations.append(i)

        return self


    """
    Attributes
    """

    
    
    
    @property
    def sameas(self):
        """
        Returns list of values for sameas
        """
        sameas= []
        for i in self.get('schema:sameAs'):
            if i.value not in sameas:
                sameas.append(i.value)
        return sameas

    @property
    def created_date(self):

        earliest_date = None
        for i in self._observations:
            if not earliest_date or i.created_date < earliest_date:
                earliest_date = i.created_date

        return earliest_date

    @property
    def modified_date(self):

        modified_date = None
        for i in self._observations:
            if not modified_date or i.created_date > modified_date:
                modified_date = i.created_date

        return modified_date


    @property
    def ref_id(self):
        return {'@type': self.record_type, '@id': self.record_id}

    @property
    def json(self):
        return self.dump_to_record()


    @property
    def observations(self):
        """Return observations 
        """
        return self.get_observations()


    @property
    def new_observations(self):
        """Return observations not committed to db
        """
        return self.get_new_observations() 


    """
    API
    """

    def get(self, key):

        obs = []
        for i in self.observations:
            if i.key == key:
                obs.append(i)

        return obs



    def post(self, record = {}):

        return


    """
    Methods - Entity
    """

    def dump_to_record(self):
        """ Convers obs to record
        """
        record = self.ref_id

        for o in self.observations:
            if not record.get(o.key, None):
                record[o.key] = []
            
            if o.value not in record[o.key]:
                record[o.key].append(o.value)
        
        # Simplify json record
        for k in record:
            if isinstance(record[k], list):
                if len(record[k]) == 1:
                    record[k] = record[k][0]
                elif len(record[k]) == 0:
                    record[k] = None
        
        
        
        return record


    def load_from_record(self, record, metadata = None):
        """Load record. Turns them into o. Return nested entities
        metadata is dict with observation data (credibility, etc)
        """

        record = self.test_valid_record(record)
        
        if not record:
            return []

        self.record_type = record.get('@type', self.record_type)
        self.record_id = record.get('@id', self.record_id)

        cache_type = cache_types.get(self.record_type, None)
        if not cache_type:
            cache_type= norm.normalize_type(self.record_type)
            cache_types[self.record_type] = cache_type
        self.record_type = cache_type
        
        record['@type'] = self.record_type

        # 

        # Replace og:url by schema:url
        og_url = record.get('og:url', None)
        if og_url and not record.get('schema:url', None):
            record['schema:url'] = og_url


        self.normalize_id(record)
        
        if not metadata:
            metadata = self._get_metadata(record)


        for key, values in record.items():

            if key not in ['@type', '@id'] and key not in METADATA_TERMS:
                self._load_value(key, values, metadata)

        
        
        return self._related


    def test_valid_record(self, record):
        # Return cleaned up recor dif true, False if not

        valid = True

        if not isinstance(record, dict):
            valid = False

        record_type = record.get('@type', self.record_type)

        if type(record_type) is list and len(record_type) == 1:
            record['@type'] = record_type[0]
        

        if valid == True:
            return record

        else:

            content = '-' * 40 + '\n'
            content += datetime.datetime.now() + '\n'
            content += json.dumps(record, default = str, indent = 4)
            
            
            f = open("rejected_records.txt", "a")
            f.write(content)
            f.close()

            return False



    def _get_metadata(self, record):

        metadata = {}
        for t in METADATA_TERMS:
            metadata[t] = record.get(t, None)

        return metadata
        

    def _load_value(self, key, values, metadata):

        if type(values) is not list:
                values = [values]

        for value in values:

            if not value:
                continue
            
            # Transform value into entity if one (nested)
            if type(value) is dict and value.get('@type', None):
                entity = Entity()
                entity.load_from_record(value, metadata)
                value = entity.ref_id
                self._related.append(entity)
                for i in entity._related:
                    self._related.append(i)

            # Populate observation data
            o = Observation(self.record_type, self.record_id)
            if metadata:
                o._load_from_record(metadata)
            o.key = key
            o.value = value
            self.post_observation(o)



    """
    Methods - observations
    """

    def get_observations(self):
        return self._observations


    def get_new_observations(self):
        new_observations = []
        for o in self._observations:
            if not o.db_id:
                new_observations.append(o)

        return new_observations


    def post_observation(self, observation):
        """Add observation to list
        """

        # Change obs type if exist, else takes it from obs
        if self.record_type:
            observation.record_type = self.record_type
        else:
            self.record_type = observation.record_type
        
        # Change obs id if exist, else takes it from obs
        if self.record_id:
            observation.record_id = self.record_id
        else:
            self.record_id = observation.record_id

        # Add to list if not exist
        if observation not in self._observations:
            self._observations.append(observation)

        return


    """
    Methods- mass change
    """

    def update_record_type(self, new_record_type):
        """Update record type of self and obs
        """
        self.record_type = new_record_type
        for o in self._observations:
            o.record_type = new_record_type
        return


    def update_record_id(self, new_record_id):
        """Update record id of self and obs
        """
        self.record_id = new_record_id
        for o in self._observations:
            o.record_id = new_record_id
        return


    def update_ref_id(self, old_record_type, old_record_id, new_record_type, new_record_id):
        """Changes all references to ref id in value of observations. Returns number of obs changed
        """
        old_ref_id = {'@type': old_record_type, '@id': old_record_id}
        new_ref_id = {'@type': new_record_type, '@id': new_record_id}

        count = 0
        for o in self._observations:
            if o.value == old_ref_id:
                o.value = new_ref_id
                count += 1

        return count

        
    @error_log
    def normalize_id(self, record):

        if not self.record_type:
            return

        new_record = {}

        for k in record:
            new_k = k.lower().replace('schema:', '')
            new_record[new_k] = record[k]
        record = new_record

        norm_record_type = self.record_type.lower().replace('schema:', '')

        if norm_record_type in ['webpage', 'website', 'datafeed', 'webapi']:
            url = record.get('url', None)
            if url:
                hash_url = str(uuid.uuid3(uuid.NAMESPACE_URL, url))
                self.record_id = hash_url


        elif norm_record_type in ['imageobject', 'videoobject']:
            url = record.get('contenturl', None)
            if url:
                hash_url = str(uuid.uuid3(uuid.NAMESPACE_URL, url))
                self.record_id = hash_url

        


        else:
            a=1

        return

    
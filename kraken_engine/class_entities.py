
#import kraken_db_api


from kraken_engine.class_entity import Entity
from kraken_engine.class_observation import Observation



class Entities:


    def __init__(self, record_type = None, record_id = None):

        self.record_type = record_type
        self.record_id = record_id

        # Store observations from / to database
        #self.observations = []
        self._entities = {}


    """
    Atrtributes
    """

    @property
    def json(self):

        return self.dump_to_records()
    

    @property
    def entities(self):
        return self._get_entities()


    @property
    def new_observations(self):
        # Gather all observation from individual entity
        observations = []

        for entity in self.entities:
            for o in entity.new_observations:
                if o not in observations:
                    observations.append(o)

        return observations



    @property
    def observations_json(self):
        # Gather all observation from individual entity
        observations = []

        for entity in self.entities:
            for o in entity.observations:
                if o.json not in observations:
                    observations.append(o.json)

        return observations


    @property
    def observations(self):
        # Gather all observation from individual entity
        observations = []

        for entity in self.entities:
            for o in entity.observations:
                if o not in observations:
                    observations.append(o)

        return observations


    @property
    def new_observations_json(self):
        # Gather all observation from individual entity
        observations = []

        for entity in self.entities:
            for o in entity.new_observations:
                if o.json not in observations:
                    observations.append(o.json)

        return observations


    """
    API
    """

    def get(self):

        return



    def post(self, record = {}):

        return self._post_entity(record)

    def post_observations(self, observations):
        return self._post_observations(observations)
        



    """
    Methods - Entities
    """

    def dump_to_records(self):
        records = []
        for i in self.entities:
            if i:
                records.append(i.dump_to_record())
        return records


    def load_from_records(self, records):
        """Load from list of json-ld records
        """
        if type(records) is list:
            for record in records:
                self.load_from_records(record)

            return

        entity = Entity()
        nested = entity.load_from_record(records)
        self._post_entity(entity)
        self._post_entity(nested)
        

        return

    """
    Methods - Entity
    """


    def _get_entity(self, record_type, record_id):

        if not self._entities:
            return None

        try:
            return self._entities.get(record_type, {}).get(record_id, None)
        except Exception as e:
            return e


    def _get_entities(self):
        """Returns list of all entities
        """
        entities = []
        for t in self._entities.keys():
            for i in self._entities[t].keys():
                entities.append(self._get_entity(t, i))
        
        return entities


    def _post_entity(self, new_entity):
        """Add an entity to list of entities
        """

        if type(new_entity) is list:
            for i in new_entity:
                self._post_entity(i)
            return


        old_entity = self._get_entity(new_entity.record_type, new_entity.record_id)

        if old_entity:
            old_entity = old_entity + new_entity

        else:
            self._create_type_and_id_in_dict(self._entities, new_entity.record_type, new_entity.record_id)
            self._entities[new_entity.record_type][new_entity.record_id] = new_entity

        return


    def _new_entity(self, record_type, record_id):
        """Create new entity and return entity
        """

        self._create_type_and_id_in_dict(self._entities, record_type, record_id)
        
        entity = Entity(record_type, record_id)
        self._post_entity(entity)
        return entity


    """
    Methods - Observations
    """


    def update_ref_id(self, old_record_type, old_record_id, new_record_type, new_record_id):
        """Changes all references to ref id in value of observations
        """

        count = 0
        for entity in self.entities:
            count += entity.update_ref_id(old_record_type, new_record_type, old_record_id, new_record_id)

        return count

    def _post_observations(self, observations):

        if type(observations) is not list:
            observations = [observations]

        for observation in observations:

            if type(observation) is not Observation:
                o = Observation()
                o.json = observation
                observation = o


            entity = self._get_entity(observation.record_type, observation.record_id)

            # Check if entity exist, create if not:
            if not entity:
                entity = self._new_entity(observation.record_type, observation.record_id)

            # Add observation
            entity.post_observation(observation)

        return



    """
    Helpers
    """

    def _create_type_and_id_in_dict(self, dict_record, record_type, record_id):
        """Creates dict_record[type][id] if doesn't exist
        """

        if not dict_record.get(record_type, None):
            dict_record[record_type] = {}

        if not dict_record[record_type].get(record_id, None):
            dict_record[record_type][record_id] = None

        return 
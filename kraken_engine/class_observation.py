import uuid
import kraken_schema_org as norm 
import kraken_datatype as dt
import json
import datetime
class Observation:

    def __init__(self, record_type = None, record_id = None):

        # attributes related to datapoint
        self.observation_id = str(uuid.uuid4())
        self.db_id = None
        self.created_date = datetime.datetime.now()
        self._record_type = record_type
        self._record_id = record_id
        self._key = None
        self._value = None

        #Attributes related to source of datapoint
        self.credibility = None
        self.datasource = None
        self.agent = None
        self.instrument = None
        self.object = None
        self.result = None
        self.start_time = None
        self.end_time = None
        self.valid = None

        self.observation_date = None

        #Attributes related to db
        self.in_db = False

    def __eq__(self, other):

        if self.observation_id == other.observation_id:
            return True

        return False

    def __repr__(self):
        return json.dumps(self._dump_to_record(), default = str, indent = 4)


    """
    Attributes
    """

    
    @property
    def is_valid(self):

        if not isinstance(self.record_type, str):
            return False
        if not isinstance(self.record_id, str):
            return False
        if not isinstance(self.key, str):
            return False

        return True

    @property
    def ref_id(self):
        record = {
            '@type': self.record_type,
            '@id': self.record_id
        }
        return record

    @property
    def record_type(self):
        return self._record_type

    @record_type.setter
    def record_type(self, value):
        self._record_type = norm.normalize_type(value)
        if not self._record_type or type(self._record_type) is list:
            self._record_type = value

    @property
    def record_id(self):
        return self._record_id

    @record_id.setter
    def record_id(self, value):
        self._record_id = value


    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        
        self._key = value
        try:
            self._key = norm.normalize_key(value)
        except:
            a=1
        if not self._key:
            self._key = value
        self._normalize_value()


    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._normalize_value()



    @property
    def json(self):
        return self._dump_to_record()

    @json.setter
    def json(self, record):
        self._load_from_record(record)
        return

    @property
    def record(self):
        record = self._dump_to_record()
        return record

    @record.setter
    def record(self, record):
        self._load_from_record(record)
        return



    """
    Methods 
    """
    def _load_from_record(self, record):
        """Load a record in 
        """
        self.observation_id = record.get('observation_id', self.observation_id)
        self.record_type = record.get('record_type', self.record_type)
        self.record_id = record.get('record_id', self.record_id)
        self.key = record.get('key', self.key)

        self.value = record.get('value', self.value)
        

        self.db_id = record.get('id', self.db_id)

        self.credibility = record.get('credibility', self.credibility)
        self.datasource = record.get('datasource', self.datasource)
        self.agent = record.get('agent', self.agent)
        self.instrument = record.get('instrument', self.instrument)
        self.object = record.get('object', self.object)
        self.result = record.get('result', self.result)
        self.start_time = record.get('start_time', self.start_time)
        self.end_time = record.get('end_time', self.end_time)
        self.valid = record.get('valid', self.valid)
        self.observation_date = record.get('observation_date', self.observation_date)
        self.created_date = record.get('created_date', self.created_date)

        
    def _dump_to_record(self):
        """Dump content to record
        """



        record = {
            'id': self.db_id,
            'observation_id': self.observation_id,
            'record_type': self.record_type,
            'record_id': self.record_id,
            'key': self.key,
            'value': self.value,
            'db_id': self.db_id,
            'credibility': self.credibility,
            'datasource': self.datasource,
            'agent': self.agent,
            'instrument': self.instrument,
            'object': self.object,
            'result': self.result,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'valid': self.valid,
            'observation_date': self.observation_date,
            'created_date': self.created_date,

        }

        if type(record.get('created_date', None)) is not datetime.datetime:
            record['created_date'] = datetime.datetime.now()

        return record



    def _normalize_value(self):

        if not self.key or not self.value:
            return

        datatypes = norm.get_datatype(self.record_type, self.key)

        if not datatypes:
            return

        for i in datatypes:
            try:
                k = i.lower().replace('schema:', '')
                n_value = dt.normalize(k, self._value)
                if n_value:
                    self._value = n_value
                    return
            except Exception as e:
                a=1
                #print('error', i, e)
from kraken_engine.class_entity import Entity
from kraken_engine.class_observation import Observation



def test_init():

    record_type = 'test_type'
    record_id = 'test_id'

    entity = Entity(record_type, record_id)

    assert entity.record_type == record_type

    assert entity.record_id == record_id


def test_observation():

    record_type = 'test_type'
    record_id = 'test_id'

    obs = Observation(record_type, record_id)

    entity = Entity(record_type, record_id)

    entity.post_observation(obs)

    assert entity.observations == [obs]
    

def test_add_entity():

    record_type = 'test_type'
    record_id = 'test_id'

    obs = Observation(record_type, record_id)

    entity1 = Entity(record_type, record_id)
    entity1.post_observation(obs)

    entity2 = Entity(record_type, record_id)
    entity2.post_observation(obs)

    entity1 = entity1 + entity2

    assert entity1.observations == [obs]
    
    
def test_change_ref_id():

    record_type = 'test_type'
    record_id = 'test_id'

    obs = Observation(record_type, record_id)
    obs.value = {'@type': record_type, '@id': record_id}


    entity1 = Entity(record_type, record_id)
    entity1.post_observation(obs)

    record_id2 = 'test_id2'

    entity1.update_ref_id(record_type, record_id, record_type, record_id2)

    assert entity1.observations[0].value == {'@type': record_type, '@id': record_id2}
    

def test_load_record():

    record = {
        '@type': 'test_type',
        '@id': 'test_id',
        'schema:name': 'test_name'
    }

    entity = Entity()
    entity.load_from_record(record)

    assert entity.observations[0].value == 'test_name'

def test_load_nested():

    record = {
        '@type': 'test_type',
        '@id': 'test_id',
        'schema:name': 'test_name',
        'parent': {
            '@type': 'test_type',
            '@id': 'test_id_nested',
            'schema:name': 'test_name_nested'
        }
    }

    entity = Entity()
    related = entity.load_from_record(record)

    assert related[0].observations[0].value == 'test_name_nested'





def test_dump_record():

    record_type = 'test_type'
    record_id = 'test_id'

    obs = Observation(record_type, record_id)
    obs.key = 'schema:name'
    obs.value = 'test_name'

    entity = Entity()
    entity.post_observation(obs)

    record = {
        '@type': 'test_type',
        '@id': 'test_id',
        'schema:name': ['test_name']
    }

    assert entity.dump_to_record() == record
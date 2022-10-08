
DBURL = 'https://dbapi.tactik8.repl.co'
import json
import uuid
import queue
from threading import Thread
from kraken_engine.decorators import error_log
import tldextract
import operator
import kraken_schema_org as norm 

import copy
from kraken_engine.class_log import Kraken_log as Log

from kraken_db.class_kraken_db import Kraken_db as Db
from kraken_engine.class_entity import Entity

from kraken_engine.class_entities import Entities
from kraken_engine import flask_routes 
import copy
global post_queue
post_queue = None

global entity_cache
entity_cache = {}
id_cache = {}


db = Db('data/test30')



def init_daemon():

    # Init queue
    global post_queue
    post_queue = queue.Queue()

    # Init daemon
    thread = Thread(target=post_daemon)
    thread.setDaemon(True)
    thread.start()


def get_daemon_queue_size():
    
    global post_queue
    
    return post_queue.qsize()


def post_daemon():
    global post_queue
    while True:
        record = post_queue.get()
        
        if record:
            post(record)

def post_to_queue(record):
    post_queue.put(record)
    print('Queue size', post_queue.qsize())
    return


def get(record_type = None, record_id = None, key = None, value = None):

    # Retrieve obs from db
    observations = db.get(record_type, record_id, key, value)

    
    # Generate entities
    e = Entities()
    e.post_observations(observations) 

    # Output json result
    records = e.json

    return records


def get_observations(record_type = None, record_id = None, key = None, value = None):

    # Retrieve obs from db
    observations = db.get(record_type, record_id)


    # Generate entities
    e = Entities()
    e.post_observations(observations)

    # Output json result
    records = e.observations_json

    
    return records


def get_entities():

    records = db.list_record_types()
    return records


def search(params, order_by = None, order_direction = None, limit = 100, offset = 0):

    log = Log('engine_search')
    
    limit = int(limit)
    offset = int(offset)

    # Normalize params
    norm_params = []
    
    for key, operator, value in params:
        if key == '@type':
            value = norm.normalize_type(value)

        norm_params.append((key, operator, value))
    
    # Retrieve obs from db
    observations = db.search(norm_params, order_by, order_direction, limit, offset)

    # Generate entities
    e = Entities()
    e.post_observations(observations)

    
    log.stop()
    return e.json


def post(record):

    log = Log('engine_post')


    # Generate entities
    entities = Entities()
    entities.load_from_records(record)


    # Search db for equivalent or duplicate record
    for e in entities.entities:
        new_record_id = find_id(e)
        if new_record_id and new_record_id != e.record_id:
            old_record_id = copy.deepcopy(e.record_id)
            e.update_record_id(new_record_id)
            entities.update_ref_id(e.record_type, old_record_id, e.record_type, new_record_id)


    obs = entities.observations


    for o in obs:
        if o.value and isinstance(o.value, str) and len(o.value) > 6000:
            o.value = o.value[:200]


    records = []
    for i in obs: 
        if i.is_valid:
            records.append(i.record)

    # Save to db
    for i in records:
        try:
            db.post(i)
        except Exception as e:
            print(e)
            db.rollback()
            db.post(i)
         
        db.commit()

    # Output json result
    records = entities.json


    # perform basic extract
    basic_extract(obs)

    log.stop()

    
    return records


def search_observations(params, order_by = None, order_direction = None, limit = 100, offset = 0):

    log = Log('engine_search_observations')
    
    limit = int(limit)
    offset = int(offset)

    # Normalize params
    norm_params = []
    
    for key, operator, value in params:
        if key == '@type':
            value = norm.normalize_type(value)

        norm_params.append((key, operator, value))
    
    # Retrieve obs from db
    observations = db.get_observations(norm_params, order_by, order_direction, limit, offset)

   
    return observations


def basic_extract(obs):
    # Extract domain from url

    if not isinstance(obs, list):
        obs = [obs]

    for o in obs:

        if o.key =='schema:url' and o.value: 
            url = o.value
            ext = tldextract.extract(url)
            domain = ext.registered_domain
            website_url = 'https://' + domain
    
            website = {
                '@type': 'schema:WebSite',
                'schema:url': website_url,
                'schema:SameAs': website_url
                }
            action = {
                '@type': 'schema:Action',
                'schema:object': { '@type': o.record_type, '@id': o.record_id},
                'schema:result': website,
                'schema:instrument': 'basic_extract'
            }
            
            entity = Entity()
            entity.load_from_record(website)
            if not record_exists(entity.record_type, entity.record_id):
                if not entity_cache.get(entity.record_type, None):
                    entity_cache[entity.record_type] = {}
                entity_cache[entity.record_type][entity.record_id] = True
                
                post(website)
                post(action)

        if o.key =='schema:email' and o.value: 
            email = o.value
            domain = email.split('@')[1]
            website_url = 'https://' + domain
    
            website = {
                '@type': 'schema:WebSite',
                'schema:url': website_url,
                'schema:SameAs': website_url
                }

            action = {
                '@type': 'schema:Action',
                'schema:object': { '@type': o.record_type, '@id': o.record_id},
                'schema:result': website,
                'schema:instrument': 'basic_extract'
            }
            
            entity = Entity()
            entity.load_from_record(website)
            if not record_exists(entity.record_type, entity.record_id):
                post(action)




def record_exists(record_type, record_id):
    """
    Return true if entity exists in db
    """

    # Check if in entity_cache
    entity = entity_cache.get(record_type, {}).get(record_id, None)
    if entity:
        return True


    # Retrieve obs from db
    observations = db.get(record_type, record_id, None, None)

    if observations and len(observations) > 0:
        # Add to cache
        if not entity_cache.get(record_type, None):
            entity_cache[record_type] = {}
        entity_cache[record_type][record_id] = True

        return True

    return False



def find_id(entity):
    """
    Look for record in db, return id if exist
    """

    # Look in cache


    # ContactPoint:
    if entity.record_type in ['schema:Person', 'schema:ContactPoint']:
        record_id = find_id_by_email(entity)
        if record_id:
            return record_id

    # if webpage
    elif entity.record_type in ['schema:Organization', 'schema:WebPage', 'schema:WebSite', 'schema:SearchAction', 'schema:WebAPI']:
        record_id = find_id_by_url(entity)
        if record_id:
            return record_id

    # if image

    elif entity.record_type in ['schema:ImageObject', 'schema:VideoObject']:


        record_id = find_id_by_hash(entity)
        if record_id:
            return record_id
            
        record_id = find_id_by_contenturl(entity)
        if record_id:
            return record_id

    elif entity.record_type in ['schema:Brand', 'schema:Organization']:


        record_id = find_id_by_name(entity)
        if record_id:
            return record_id

    
    else:
        record_id = find_id_by_url(entity)
        if record_id:
            return record_id


    

            
                
    # Search in sameas
    record_id = find_id_by_sameas(entity)
    if record_id:
        return record_id

    return None


def find_id_by_hash(entity):
    for o in entity.observations:
        if o.key == 'schema:sha256':

            # Look in cache
            cache_id = id_cache.get(entity.record_type, {}).get(o.value, None)
            if cache_id:
                return cache_id


            # Look in db
            params = []
            params.append(('record_type', 'eq', entity.record_type))
            params.append(('schema:sha256', 'eq', o.value))

            records = db.search(params, None, None, 1, 0)

            if records:
                record_id = records[0].get('record_id', records[0].get('@id', None))

                # Add to cache
                if not id_cache.get(entity.record_type, None):
                    id_cache[entity.record_type] = {}
                id_cache[entity.record_type][o.value] = record_id

                # Return
                return record_id

    return None


def find_id_by_name(entity):

    for o in entity.observations:
        if o.key == 'schema:name':

            # Look in cache
            cache_id = id_cache.get(entity.record_type, {}).get(o.value, None)
            if cache_id:
                return cache_id


            # Look in db
            params = []
            params.append(('record_type', 'eq', entity.record_type))
            params.append(('schema:name', 'eq', o.value))

            records = db.search(params, None, None, 1, 0)

            if records:
                record_id = records[0].get('record_id', records[0].get('@id', None))

                # Add to cache
                if not id_cache.get(entity.record_type, None):
                    id_cache[entity.record_type] = {}
                id_cache[entity.record_type][o.value] = record_id

                # Return
                return record_id

    return None


def find_id_by_url(entity):

    for o in entity.observations:
        if o.key == 'schema:url':

            # Look in cache
            cache_id = id_cache.get(entity.record_type, {}).get(o.value, None)
            if cache_id:
                return cache_id


            # Look in db
            params = []
            params.append(('record_type', 'eq', entity.record_type))
            params.append(('schema:url', 'eq', o.value))

            records = db.search(params, None, None, 1, 0)

            if records:
                record_id = records[0].get('record_id', records[0].get('@id', None))

                # Add to cache
                if not id_cache.get(entity.record_type, None):
                    id_cache[entity.record_type] = {}
                id_cache[entity.record_type][o.value] = record_id

                # Return
                return record_id

    return None


    
def find_id_by_contenturl(entity):

    for o in entity.observations:
        if o.key == 'schema:contentUrl':

            # Look in cache
            cache_id = id_cache.get(entity.record_type, {}).get(o.value, None)
            if cache_id:
                return cache_id


            # Look in db
            params = []
            params.append(('record_type', 'eq', entity.record_type))
            params.append(('schema:contentUrl', 'eq', o.value))

            records = db.search(params, None, None, 1, 0)

            if records:
                record_id = records[0].get('record_id', records[0].get('@id', None))

                # Add to cache
                if not id_cache.get(entity.record_type, None):
                    id_cache[entity.record_type] = {}
                id_cache[entity.record_type][o.value] = record_id

                # Return
                return record_id

    return None


def find_id_by_email(entity):

    for o in entity.observations:
        if o.key == 'schema:email':
            # Look in cache
            cache_id = id_cache.get(entity.record_type, {}).get(o.value, None)
            if cache_id:
                return cache_id

            # Look in db
            params = []
            params.append(('record_type', 'eq', entity.record_type))
            params.append(('schema:email', 'eq', o.value))

            records = db.search(params, None, None, 1, 0)

            if records:
                record_id = records[0].get('record_id', records[0].get('@id', None))

                # Add to cache
                if not id_cache.get(entity.record_type, None):
                    id_cache[entity.record_type] = {}
                id_cache[entity.record_type][o.value] = record_id

                # Return
                return record_id

    return None



def find_id_by_sameas(entity):
    for o in entity.observations:
        if o.key == 'schema:sameAs':
            # Look in cache
            cache_id = id_cache.get(entity.record_type, {}).get(o.value, None)
            if cache_id:
                return cache_id

            # look in db
            params = []
            params.append(('record_type', 'eq', entity.record_type))
            #todo: added "" to comply with json format of db. Fix db
            params.append(('schema:sameAs', 'eq', '"{value}"'.format(value = o.value)))

            records = db.search(params)
            if records:
                record_id = records[0].get('record_id', records[0].get('@id', None))

                # Add to cache
                if not id_cache.get(entity.record_type, None):
                    id_cache[entity.record_type] = {}
                id_cache[entity.record_type][o.value] = record_id

                # Return
                return record_id

    return None

def run_api(url = None):
    
    #db.set_db_url(DBURL)

    flask_routes.run_api()



init_daemon()
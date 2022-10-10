
from kraken_db import db_connect
from kraken_db import db_config
from kraken_db import data_manipulation as data
from kraken_db import sql_commands as sql
import datetime
import os

DB_PATH = 'db/db_test.sqlite'


def init(db_path = DB_PATH):
    """
    Initializes db, returns connection"""

    # Create directory
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    

    conn = db_connect.create_connection(db_path)
    db_config.db_config_records(conn)
    db_config.db_config_observations(conn)

    #sql.sql_fix_records(conn)
    #sql.sql_fix_observations(conn)
    #sql.sql_remove_duplicates(conn)
    
    return conn

def list_record_types(conn):
    """
    Returns list of record_types
    """

    return sql.sql_get_record_types(conn)


def search(conn, params, order_by = None, order_direction = None, limit = 100, offset = 0):
    """
    Search
    Returns observations
    """

    start = datetime.datetime.now()
    
    # Convert params
    
    where_clauses = []

    for i in params:
        
        where_clauses.append(data.convert_params(i))


    
    # Retrieve records
    records = sql.sql_get_records_observations(conn, where_clauses, order_by, order_direction, limit, offset)



    # Transform data from db to regular format
    records = data.sql_db_record_to_data(records)



    #print('Search Duration:', (datetime.datetime.now()-start).total_seconds())
    #print(params, len(records))
    return records


    
def post(conn, records):
    """
    """
    start = datetime.datetime.now()
    
    # Convert data to db friendly mapping
    records = data.sql_data_to_db_record(records)

    # Add records
    sql.sql_add_record(conn, records)
    
    # Add observations
    sql.sql_add_observations(conn, records)
    
    # Commit add
    conn.commit()

    #print('Post Duration:', (datetime.datetime.now()-start).total_seconds())
    
    
    return


def get(conn, record_type=None, record_id=None, key=None, value=None):
    """
    """

    # Retrieve records
    records = sql.sql_get_record(conn, record_type, record_id)


    # Transform data from db to regular format
    records = data.sql_db_record_to_data(records)
    #print(record_type, record_id, len(records))

    return records




def get_observations(conn, params, order_by = None, order_direction = None, limit = 100, offset = 0):
    """
    Search
    Returns observations
    """

    start = datetime.datetime.now()
    
    # Convert params
    
    where_clauses = []

    for i in params:
        
        where_clauses.append(data.convert_params(i))


    
    # Retrieve records
    records = sql.sql_get_observations(conn, where_clauses, order_by, order_direction, limit, offset)


    # Transform data from db to regular format
    records = data.sql_db_record_to_data(records)

    return records


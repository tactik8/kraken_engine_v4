from kraken_db import db_connect


def db_config_records(conn):
    
    db_connect.create_table_records(conn)

    db_connect.sql_add_column(conn, 'records', '_record_ref', 'TEXT')

    
    
    #db_connect.create_index(conn, 'records', 'record_type')
    #db_connect.create_index(conn, 'records', 'record_id')
    db_connect.create_index(conn, 'records', '_record_ref')
    db_connect.create_index(conn, 'records', 'date_created')
    db_connect.create_index(conn, 'records', 'date_updated')

    db_connect.create_index(conn, 'records', 'created_date')
    db_connect.create_index(conn, 'records', '_record_ref, created_date')

    
    #db_connect.create_index(conn, 'records', 'date_created, _record_ref')
    #db_connect.create_index(conn, 'records', '_record_ref, date_created')

    #db_connect.create_index(conn, 'records', 'date_created, record_type')


def db_config_observations(conn):
    
    db_connect.create_table_observations(conn)

    db_connect.sql_add_column(conn, 'observations', '_record_ref', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', '_value_text', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', '_value_int', 'INTEGER')
    db_connect.sql_add_column(conn, 'observations', '_value_real', 'REAL')
    db_connect.sql_add_column(conn, 'observations', '_value_datetime', 'datetime')
    db_connect.sql_add_column(conn, 'observations', '_value_type', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', '_value_id', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', '_value_ref', 'TEXT')

    db_connect.sql_add_column(conn, 'observations', '_value_json', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', 'credibility', 'REAL')
    db_connect.sql_add_column(conn, 'observations', 'created_date', 'datetime')
    db_connect.sql_add_column(conn, 'observations', 'datasource', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', 'agent', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', 'instrument', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', 'object', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', 'result', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', 'start_time', 'datetime')
    db_connect.sql_add_column(conn, 'observations', 'end_time', 'datetime')
    db_connect.sql_add_column(conn, 'observations', 'valid', 'BOOL')
    db_connect.sql_add_column(conn, 'observations', 'hash', 'TEXT')
    db_connect.sql_add_column(conn, 'observations', '_value_str', 'TEXT')
    

    # indexes
    db_connect.create_index(conn, 'observations', 'record_id')
    db_connect.create_index(conn, 'observations', 'record_type')
    db_connect.create_index(conn, 'observations', '_record_ref')
    
    db_connect.create_index(conn, 'observations', 'key')
    db_connect.create_index(conn, 'observations', 'created_date')

    
    db_connect.create_index(conn, 'observations', '_value_id')
    db_connect.create_index(conn, 'observations', '_value_type')
    db_connect.create_index(conn, 'observations', '_value_ref')

    
    db_connect.create_index(conn, 'observations', '_value_int')
    db_connect.create_index(conn, 'observations', '_value_real')
    db_connect.create_index(conn, 'observations', '_value_datetime')
    db_connect.create_index(conn, 'observations', '_value_text')
    db_connect.create_index(conn, 'observations', '_value_str') 



    # Compound
    db_connect.create_index(conn, 'observations', 'date_created, record_type')
    db_connect.create_index(conn, 'observations', 'created_date, record_type')

    
    db_connect.create_index(conn, 'observations', 'record_id, record_type')

    # Search
    db_connect.create_index(conn, 'observations', '_value_text, key, record_type')
    
    db_connect.create_index(conn, 'observations', '_value_text, key')
    db_connect.create_index(conn, 'observations', 'key, _value_text')

    db_connect.create_index(conn, 'observations', '_value_ref, key')


    
    db_connect.create_index(conn, 'observations', '_value_real, key, record_type')
    db_connect.create_index(conn, 'observations', '_value_real, created_date, key, record_type')
    
    db_connect.create_index(conn, 'observations', '_value_id, key, _value_type')

    db_connect.create_index(conn, 'observations', '_record_ref, created_date')

    db_connect.create_index(conn, 'observations', 'record_type, record_id, key, _value_str, datasource, credibility, observation_date', True)

    
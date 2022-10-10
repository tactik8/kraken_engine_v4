
import sqlite3
import datetime
import os


filepath = 'log_query/log_file.txt'
os.makedirs(os.path.dirname(filepath), exist_ok=True)


def sql_data_to_list_of_dicts(conn, select_query):
      """Returns data from an SQL query as a list of dicts."""
      try:
          conn.row_factory = sqlite3.Row
          things = conn.execute(select_query).fetchall()
          unpacked = [{k: item[k] for k in item.keys()} for item in things]
          return unpacked
      except Exception as e:
          print(f"Failed to execute. Query: {select_query}\n with error:\n{e}")
          return []



def sql_fix_records(conn):

    sql_query = '''
        UPDATE records
        SET created_date={date}
        WHERE created_date IS NULL;

    '''.format(date=datetime.datetime.now())
    try:
        c = conn.cursor()
        c.execute(sql_query)
        #conn.commit()
    except Exception as e:
        print('Error fixing record', e)

def sql_fix_observations(conn):

    sql_query = '''
    
        UPDATE observations
        SET created_date={date}
        WHERE created_date IS NULL;

    '''.format(date=datetime.datetime.now())
    try:
        c = conn.cursor()
        c.execute(sql_query)
        #conn.commit()
    except Exception as e:
        print('Error fixing obs', e)








def sql_add_record(conn, obs):

    if not isinstance(obs, list):
        obs=[obs]


    # Deduplicate
    record_refs = []
    records = []
    for i in obs:
        record_ref = i.get('_record_ref', None)
        if record_ref not in record_refs:
            records.append(i)
            record_refs.append(record_ref)

    obs = records
    #print('Adding records ',i.get('record_type', None), i.get('record_id', None))

    # Query
    sql_query = '''
        INSERT INTO records ('record_type', 'record_id', '_record_ref')
        VALUES
           (:record_type, :record_id, :_record_ref)
            ;
        '''

    start_time = datetime.datetime.now()

    try:
        c = conn.cursor()
        c.executemany(sql_query, obs)
        #conn.commit()
    except Exception as e:
        if 'UNIQUE constraint' not in str(e):
            print('Error creating record', e)

    duration = (datetime.datetime.now() - start_time).total_seconds()
    
    if duration > 1:
        save_long_query(sql_query, duration)


def sql_add_observations(conn, obs):
    """
    Add observation record to db
    """

    # Convert to list
    if not isinstance(obs, list):
        obs=[obs]
    
    sql_query = '''    
        INSERT OR IGNORE INTO observations ('observation_id', '_record_ref', 'record_type', 'record_id', 'key', '_value_text', '_value_int', '_value_real', '_value_id', '_value_type', '_value_ref', '_value_datetime', '_value_json', 'credibility', 'created_date', 'date_created')
        VALUES (:observation_id, :_record_ref, :record_type, :record_id, :key, :_value_text, :_value_int, :_value_real, :_value_id, :_value_type, :_value_ref, :_value_datetime, :_value_json, :credibility, datetime('now'), datetime('now'));
        '''
    
    start_time = datetime.datetime.now()

    try:
        c = conn.cursor()
        c.executemany(sql_query, obs)
        #conn.commit()
    except Exception as e:
        print('Error creating obs', e)

    

    duration = (datetime.datetime.now() - start_time).total_seconds()
    
    if duration > 1:
        save_long_query(sql_query, duration)

    
    return
    




def sql_get_record(conn, record_type, record_id):
    
    sql_query = '''
        SELECT *
        FROM observations
        WHERE record_type="{record_type}" and record_id="{record_id}"
        
        '''.format(record_type=record_type, record_id=record_id)


    
    start_time = datetime.datetime.now()
    
    records = sql_data_to_list_of_dicts(conn, sql_query)

    duration = (datetime.datetime.now() - start_time).total_seconds()
    
    if duration > 1:
        save_long_query(sql_query, duration)


    
    return records

def sql_get_observations(conn, wheres=None, orderby='created_date', order_direction='DESC', limit=1000, offset=0):

    wheres = ' AND '.join(wheres)

    if wheres:
        wheres = 'WHERE ' + wheres

    order_statement = 'ORDER BY ' + orderby + ' ' + order_direction if orderby else ''

    limit_statement = ''        
    if limit:
        limit_statement = 'LIMIT {limit} OFFSET {offset}'.format(limit=limit, offset=offset)

    
    sql_query = '''
        SELECT *
        FROM observations
        {wheres}
        {order_statement}
        {limit_statement}
            
        '''.format(wheres=wheres, order_statement=order_statement, limit_statement=limit_statement)


    #print(sql_query)
    start_time = datetime.datetime.now()
    
    records = sql_data_to_list_of_dicts(conn, sql_query)

    duration = (datetime.datetime.now() - start_time).total_seconds()
    
    if duration > 1:
        save_long_query(sql_query, duration)


    
    return records




def sql_get_records_observations(conn, wheres=None, orderby='created_date', order_direction='DESC', limit=1000, offset=0):

    orderby = 'created_date' if orderby == 'created_date' else orderby

    if order_direction:
        order_direction = order_direction.upper()


    # Build statement
    #where_statement = 'WHERE ' + where if where else ''
    
    order_statement = 'ORDER BY ' + orderby + ' ' + order_direction if orderby else ''

    limit_statement = ''
    if limit:
        limit_statement = 'LIMIT {limit} OFFSET {offset}'.format(limit=limit, offset=offset)

    
    # Assemble query

    """
    sql_query = '''
        SELECT observations.*
        FROM observations
        INNER JOIN (
            SELECT *
            FROM records
            WHERE _record_ref in (
                SELECT DISTINCT _record_ref
                FROM observations
                {where} 
                
                )
            {order_statement}
            {limit_statement}
            ) AS records
        ON observations._record_ref=records._record_ref
        {order_statement}

            
    '''.format(where=where_statement, order_statement=order_statement, limit_statement=limit_statement)
    """
    
    # Build subqueries to retrieve observations
    sql_query_record_refs = []

    if not wheres:
        wheres = ['record_id is not null']
    
    if not isinstance(wheres, list):
        wheres=[wheres]
    
    for where in wheres:
        where = 'WHERE ' + where
        sql_query_record_ref = '''
            SELECT DISTINCT _record_ref
            FROM observations
            {where} 
        '''.format(where=where)
        sql_query_record_refs.append(sql_query_record_ref)

    # Combine subqueries to keep only values that intersect all of them
    sql_query_where = ' INTERSECT '.join(sql_query_record_refs)

    # Retrieve observations
    sql_query = '''
        SELECT observations.*
        FROM observations
        INNER JOIN (
            SELECT *
            FROM records
            WHERE _record_ref in (
                {sql_query_where} 
                )
            {order_statement}
            {limit_statement}
            ) AS records
        ON observations._record_ref=records._record_ref
        {order_statement}

            
    '''.format(sql_query_where=sql_query_where, order_statement=order_statement, limit_statement=limit_statement)

    
    #print(sql_query)


    start_time = datetime.datetime.now()
    
    records = sql_data_to_list_of_dicts(conn, sql_query)

    duration = (datetime.datetime.now() - start_time).total_seconds()
    
    if duration > 1:
        save_long_query(sql_query, duration)

    #print(records)
    
    
    return records

def sql_remove_duplicates(conn):
    
    
    sql_query = '''
        DELETE FROM observations
        WHERE EXISTS (
          SELECT 1 FROM observations p2 
          WHERE observations.record_type = p2.record_type
          AND observations.record_id = p2.record_id
          AND observations.key = p2.key
          AND observations._value_text IS NOT NULL
          AND observations._value_text = p2._value_text
          AND observations.credibility < p2.credibility
          
        );
    '''
    
    try:
        c = conn.cursor()
        c.execute(sql_query)
        print('Duplicates removed')
        c.execute('VACUUM')
        #conn.commit()
    except Exception as e:
        print('Error duplicates', e)

    return

def sql_get_record_types(conn):
    """Returns list of dict with number for each record_types
    """
    sql_query = '''
            SELECT record_type, COUNT(record_type) AS n
            FROM records
            GROUP BY record_type
            '''
    records = sql_data_to_list_of_dicts(conn, sql_query)
    
    
    return records



def save_long_query(query, duration):

    duration = round(duration, 0)
    
    filename = 'log_query/log_query_' + str(datetime.datetime.now()) + '_' + str(duration)
    with open(filename, 'w') as filehandle:
        filehandle.write(query)

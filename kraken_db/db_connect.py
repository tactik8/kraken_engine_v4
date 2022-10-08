import sqlite3
from sqlite3 import Error
import datetime
import uuid
import json

DB_PATH = 'db/db1.sqlite'

def create_connection(db_path):
    """ create a database connection to a database that resides
        in the memory
    """

    db_path = DB_PATH if not db_path else db_path

    conn = None;
    
    try:
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, check_same_thread=False)

        c = conn.cursor()
        c.execute('PRAGMA temp_store=MEMORY;')
        c.execute('pragma journal_mode = WAL;')
        c.execute('pragma synchronous = normal;')

    
    except Error as e:
        print(e)

    return conn



def create_table_records(conn):

    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS records (
        	_record_ref TEXT PRIMARY KEY,
            record_id text NOT NULL,
        	record_type text NOT NULL,
            name text,
            date_created timestamp DEFAULT CURRENT_TIMESTAMP,
            date_updated timestamp DEFAULT CURRENT_TIMESTAMP,
            created_date timestamp DEFAULT CURRENT_TIMESTAMP

        );
        '''

    c = conn.cursor()
    c.execute(create_table_sql)

def create_table_observations(conn):
    
    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS observations (
            observation_id TEXT PRIMARY KEY,
            _record_ref TEXT, 
            record_type TEXT,
            record_id TEXT,
            date_created timestamp DEFAULT CURRENT_TIMESTAMP,
            date_updated timestamp DEFAULT CURRENT_TIMESTAMP,
            key TEXT,
            FOREIGN KEY (_record_ref)
                REFERENCES records(_record_ref)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        );
    '''
    c = conn.cursor()
    c.execute(create_table_sql)



def drop_index(conn, index):


    sql_statement = 'DROP INDEX IF EXISTS {name};'.format(name=index)
    
    sqliteCursor = conn.cursor()

    sqliteCursor.execute(sql_statement)


def create_index(conn, table, column, unique = False):

    
    
    title = 'index_' + str(table) + '_' + column.replace(',', '_')
    title = title.replace(' ', '_')


    unique_statement = ' UNIQUE ' if unique else ''
    
    try:
        sqliteCursor = conn.cursor()
        
        createSecondaryIndex = "CREATE {unique_statement} INDEX {title} ON {table}({column})".format(title=title, table=table, column=column, unique_statement=unique_statement)

    
        sqliteCursor.execute(createSecondaryIndex)

    except Exception as e:
        if 'already exists' not in str(e):
            print(e)


def sql_add_column(conn, table, column_name, column_type):

    
    alter_sql = '''
    ALTER TABLE {table} ADD COLUMN {name} {type}
    '''.format(table=table, name=column_name, type=column_type.upper())
    
    try:
        c = conn.cursor()
        c.execute(alter_sql)
    except:
        #print('Column {name} already exists'.format(name=column_name))
        a=1

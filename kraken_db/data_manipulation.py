
import json
import datetime



def db_to_data_remove_empty_values(record):

    # Remove empty values
    new_record = {}
    for key, value in record.items():
        if value:
            new_record[key] = value

    return new_record


def db_to_data_get_value(record):
    
    value = None
    
    if record.get('_value_text', None):
        value = record.get('_value_text', None)

    elif record.get('_value_int', None):
        value = record.get('_value_int', None)

    elif record.get('_value_real', None):
        value = record.get('_value_real', None)

    elif record.get('_value_datetime', None):
        value = record.get('_value_datetime', None)

    elif record.get('_value_json', None):
        value = json.loads(record.get('_value_json', None))

    elif record.get('_value_id', None):
        value = {
            '@type': record.get('_value_type', None),
            '@id': record.get('_value_id', None)
        }

    return value


def db_to_data_remove_custom_fields(record):
    """
    """
    new_record = {}

    # Retrieve value
    new_record['value'] = db_to_data_get_value(record)

    # Copy data
    for key, value in record.items():
        if not key.startswith('_'):
            new_record[key] = value

    return new_record

def db_to_data_dates(record):

    cdate = record.get('created_date', None)

    if not isinstance(cdate, datetime.datetime):
        try:
            record['created_date'] = datetime.datetime.fromisoformat(cdate)
        except Exception as e:
            print(e)
    # record['created_date'] = record.get('date_created', None)

    return record
    
def sql_db_record_to_data(record):
    """
    Convert data coming from db
    """
    
    # Deal with list
    if isinstance(record, list):
        records = []
        for i in record:
            records.append(sql_db_record_to_data(i))
        return records

    # Remove custom field
    record = db_to_data_remove_custom_fields(record)

    # Deal with dates
    record = db_to_data_dates(record)
    
    # Remove empty values
    record = db_to_data_remove_empty_values(record)

    return record

def sql_data_to_db_record(record):
    '''
    Converts datatypes going into db
    '''

    # Deal with list
    if isinstance(record, list):
        records = []
        for i in record:
            records.append(sql_data_to_db_record(i))
        return records

    # Assign dates
    #created_date = record.get('created_date', None)
    #date_created = record.get('date_created', None)
    #record['date_created'] = date_created if date_created else created_date

    if not record.get('date_created', None):
        record['date_created'] = datetime.datetime.now()
    if not record.get('created_date', None):
        record['created_date'] = datetime.datetime.now()

    if not isinstance(record.get('created_date', None), datetime.datetime):
        try:
            record['created_date'] = datetime.datetime.fromisoformat(record.get('created_date', None))
        except Exception as e:
            print(e)
        
    # Add record_ref
    record['_record_ref'] = record.get('record_type', '') + '_' + record.get('record_id', '')
        
    # Add custom fields as blank
    for i in ['_value_text', '_value_int', '_value_real', '_value_datetime', '_value_json', '_value_id', '_value_ref', '_value_type', 'credibility', 'created_date', 'datasource', 'agent', 'instrument', 'object', 'result', 'start_time', 'end_time', 'valid', 'hash', 'observation_date', 'date_created']:
        if i not in record.keys():
            record[i] = None

    # Add value t proper datatype custom field
    value = record.get('value', None)

    record['_value_str'] = str(value)
    
    if not value:
        record['_value_text'] = None
    
    elif isinstance(value, str):
        record['_value_text'] = value

    elif isinstance(value, int) or isinstance(value, float):
        record['_value_real'] = value

    elif isinstance(value, datetime.datetime):
        record['_value_datetime'] = value
    
    elif isinstance(value, dict):
        record_id = value.get('@id', None)
        record_type = value.get('@type', None)
        if record_id and record_type:
            record['_value_id'] = record_id
            record['_value_type'] = record_type
            record['_value_ref'] = record_type + '/' + record_id
        else:
            record['_value_json'] = json.dumps(record, default=str)
        
    return record
        


        

def convert_params_operator(operator):
    """
    Conver operator in sql type
    """
    
    if operator in ['==', '=', 'eq']:
        operator = '='
    elif operator in ['>', 'gt']:
        operator = '>'
    elif operator in ['<', 'lt']:
        operator = '<'
    elif operator in ['>=', 'ge']:
        operator = '>='
    elif operator in ['<=', 'le']:
        operator = '<='

    return operator


def get_search_field(value):
    """Returns proper search field and adds "" to value if required
    """


    # Try float
    if isinstance(value, int) or isinstance(value, float):
        return '_value_real', value

    # Try datetime
    elif isinstance(value, datetime.datetime):
        return '_value_datetime', value

    # Try dict
    elif isinstance(value, dict):

        record_type = value.get('@type', None)
        record_id = value.get('@id', None)
        record_ref = '"' + record_type + '/' + record_id + '"'
        
        return '_value_ref', record_ref

    # Try text
    else:
        content =  '"' + str(value) + '"' 
        content = content.replace('""', '"')
        return '_value_text', content
        
    


def get_condition(field, operator, search_field, value):

    conditions = []


    if search_field == '_value_text':
        operator = ' LIKE '

    
    # Deal with type, id
    if field in ['record_type', '@type']:
        condition = 'record_type{operator}{value}'.format(operator=operator, value=value)
        return condition
    
    if field in ['record_id', '@id']:
        condition = 'record_id{operator}{value}'.format(operator=operator, value=value)
        return condition

    

    # Deal with field

    if field not in [None, '', '*', 'ALL', 'ANY']:
        condition = 'key="{field}"'.format(field=field)
        conditions.append(condition)

        

    # Deal with values
        
    
    if isinstance(value, dict) and '@type' in value.keys():
        condition = '''_value_type{operator}"{_value_type}" AND _value_id{operator}"{_value_id}"'''.format(
            operator=operator, 
            _value_type=value.get('@type', ''),
            _value_id=value.get('@id', '')
        )
        conditions.append(condition)
    else:
        condition = '''{search_field}{operator}{value}'''.format(
            field=field,
            operator=operator, 
            search_field=search_field,
            value=value
        )
        conditions.append(condition)
    
    # Join and add parentheses
    condition = ' AND '.join(conditions)
    condition =  '(' + condition + ')'

    
    return condition

def convert_params(params):
    """
    Convert params to sql
    """

    sql_conditions = []

    if not isinstance(params, list):
        params=[params]

    
    for field, operator, value in params:

        # Fix operator
        operator = convert_params_operator(operator)

        # Get search field
        search_field, value = get_search_field(value)
        
        # Get condition
        condition = get_condition(field, operator, search_field, value)

        # Add to conditions
        sql_conditions.append(condition)

    # Combine conditions

    sql_statement = ' AND '.join(sql_conditions)

    #print(sql_statement)
    
    return sql_statement

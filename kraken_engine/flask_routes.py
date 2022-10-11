
import os
from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import url_for
from flask import jsonify
import kraken_schema_org as norm 
import psutil
import kraken_engine.kraken_engine as engine

from kraken_engine.class_log import Kraken_log as Log

import datetime
import time
import uuid
import random

from kraken_engine import performance_trace as trace




# Initalize app
test_mode = False


# Initialize flask app
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')
app.secret_key = b'_5#mn"F4Q8z\n\xec]/'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



@app.route('/', methods=['GET'])
def main_get():
    """Process get data
    """

    content = '''
    Engine server.
    Access through /api
    /api
        - get: 
            - args: record_type, record_id, key, value
            - return: list of observations
        - post: 
            - args: json list of observation records
            - return: ok
    /api/summary
        - get: 
            - args: record_type, record_id, key, value
            - return: max observation for each key
    
    /search
        - post: 
            - args: 
                -'key_name' = 'value' - list of things to search
                - limit:
                - offset:
                - order_by
                - order_direction
            - return:
                - list of observations
    
    '''

    return Response(content)



@app.route('/datafeed/<datafeed_id>', methods=['POST'])
def datafeed_post(datafeed_id):
    """ Created datafeeditems from posted data
    """
    
    ('request', request.data.decode("utf-8") )
    input_records = request.get_json()
    
    if not isinstance(input_records, list):
        input_records = [input_records]

    records = []
    for r in input_records:
        record = {
            '@type': 'schema:datafeed',
            '@id': datafeed_id,
            'schema:dataFeedElement': {
                '@type': 'schema:DataFeedItem',
                'schema:item': r
            }
        }
        records.append(record)

    out_records = engine.post(records)
    
    return jsonify(out_records)




@app.route('/api', methods=['GET'])
def api_get():
    """Process get data
    """
    log = Log('api_get')
    print('Get')

    record_type = request.values.get('record_type', request.values.get('@type', None))
    record_id = request.values.get('record_id', request.values.get('@id', None))
    key = request.values.get('key', None)
    value = request.values.get('value', None)


    # Normalize values
    if record_type:
        new_record_type = norm.normalize_type(record_type)
        if new_record_type:
            record_type = new_record_type

    if key:
        new_key = norm.normalize_key(key)
        if new_key:
            key = new_key

    
    records = engine.get(record_type, record_id, key, value)

    log.stop()
    return jsonify(records)



@app.route('/api', methods=['POST'])
def api_post():
    """Process get data
    """


    real_time = request.values.get('real_time', None)


    print('post')
    log = Log('api_post')
    
    records = request.get_json()
    if not records:
        return Response('none')

    if not isinstance(records, list):
        records = [records]


    if real_time == True:
        out_records = engine.post(records)
    else:
        out_records = engine.post_to_queue(records)
    
    
    log.stop()


    print('Done post')
    return jsonify(out_records)



@app.route('/api/entities', methods=['GET'])
def api_get_entities():
    """Process get data
    """

    records = engine.get_entities()

    return jsonify(records)



@app.route('/api/search', methods=['GET', 'POST'])
def api_search():
    """Process get data
    """
    log = Log('api_search')

    
    order_by = 'created_date'
    order_direction = 'desc'
    limit = 100
    offset = 0
    response_format = 'json'
    params = []


    # Get values from json
    records = request.get_json()


    inputs = {}

    if isinstance(records, dict):
        for i in records:
            inputs[i] = records[i]

    for i in request.values:
        inputs[i] = request.values[i]

    

    for i in inputs:
        value = inputs[i]
        if not value or value == '':
            continue
        
        elif i == 'limit':
            limit = inputs.get(i, None)
        elif i == 'offset':
            offset = inputs.get(i, None)
        elif i == 'order_by':
            order_by = inputs.get(i, None)
        elif i == 'order_direction':
            order_direction = inputs.get(i, None)
        elif i == 'format':
            response_format = inputs.get(i, None)   

        
        elif isinstance(value, str) and len(value) > 2 and value[0:2] in ['eq', 'gt', 'ge', 'lt', 'le']:
            # float comparison
            for operator in ['eq', 'gt', 'ge', 'lt', 'le', 'contains', 'c']:
                if value.startswith(operator):
                    new_value = value.replace(operator, '')
                    new_value.strip()
                    try:
                        new_value = float(new_value)

                        param = (i, operator, new_value)
                        params.append(param)
                        break
                    except:
                        continue

        elif i not in ['operator', 'key', 'value']:
            param = (i, 'eq', value)
            params.append(param)
    records = engine.search(params, order_by, order_direction, limit, offset)
    
    log.stop()
    return jsonify(records)




@app.route('/api/exists', methods=['GET'])
def api_exists():
    """Return True if exist.
    Quick method that keeps a cache
    """
    
    record_type = request.values.get('record_type', request.values.get('@type', None))
    record_id = request.values.get('record_id', request.values.get('@id', None))
    
    
    exists = engine.exists(record_type, record_id)

    return Response(str(exists))



@app.route('/api/observations', methods=['GET', 'POST'])
def api_get_observations():
    """Process get data
    """

    
    log = Log('api_get_observations')

    
    order_by = 'created_date'
    order_direction = 'desc'
    limit = 100
    offset = 0
    response_format = 'json'
    params = []


    # Get values from input (json, values, etc)
    inputs = {}
    records = {}
    
    try:
        records = request.get_json()
    except Exception as e:
        print(e)
    
    if isinstance(records, dict):
        for i in records:
            inputs[i] = records[i]

    for i in request.values:
        inputs[i] = request.values[i]

    # Transform inputs
    for i in inputs:
        value = inputs[i]
        if not value or value == '':
            continue
        
        elif i == 'limit':
            limit = inputs.get(i, None)
        elif i == 'offset':
            offset = inputs.get(i, None)
        elif i == 'order_by':
            order_by = inputs.get(i, None)
        elif i == 'order_direction':
            order_direction = inputs.get(i, None)
        elif i == 'format':
            response_format = inputs.get(i, None)   

        
        elif isinstance(value, str) and len(value) > 2 and value[0:2] in ['eq', 'gt', 'ge', 'lt', 'le']:
            # float comparison
            for operator in ['eq', 'gt', 'ge', 'lt', 'le', 'contains', 'c']:
                if value.startswith(operator):
                    new_value = value.replace(operator, '')
                    new_value.strip()
                    try:
                        new_value = float(new_value)

                        param = (i, operator, new_value)
                        params.append(param)
                        break
                    except:
                        continue

        elif i not in ['operator', 'key', 'value']:
            param = (i, 'eq', value)
            params.append(param)

    #print(params)
    records = engine.search_observations(params, order_by, order_direction, limit, offset)
    
    log.stop()
    return jsonify(records)



@app.route('/api/observations2', methods=['GET'])
def api_get_observations2():
    """Process get data
    """


    record_type = request.values.get('record_type', None)
    record_id = request.values.get('record_id', None)
    key = request.values.get('key', None)
    value = request.values.get('value', None)

    records = engine.get_observations(record_type, record_id, key, value)

    return jsonify(records)

@app.route('/admin', methods=['GET'])
def api_get_admin():


    content = '<!DOCTYPE html><html>'
    content += '<head><meta http-equiv="Refresh" content="1"></head>'
    content += '<h1>Admin console</H1><br>'
    content +='<a href="/admin/trace">Trace</a><br>'
    content += 'Queue size: {size} <br>'.format(size=str(engine.get_daemon_queue_size()))
    
    content += 'memory: ' + str(psutil.virtual_memory().percent) + '<br>'
    content += 'cpu: ' + str(psutil.cpu_percent()) + '<br>'

    content += '</html>'
    
    return Response(content)

@app.route('/admin/trace', methods=['GET'])
def api_get_admin_trace():

    content = '<h1>Admin console - Trace</H1><br>'
    content += '<H2>Trace Status: {status}<H2>'.format(status=trace.get_status())
    content +='<a href="/admin/trace/start">Start trace</a><br>'
    content +='<a href="/admin/trace/stop">Stop trace</a><br>'

    if trace.get_status()=='completed':
        trace_content = trace.get()
        print(trace_content)
        trace_content.replace('\n', '<br>')
        
        from ansi2html import Ansi2HTMLConverter
        conv = Ansi2HTMLConverter(dark_bg=False)
        #trace_contentansi = "".join(sys.stdin.readlines())
        html = conv.convert(trace_content)

        content += html
    
    return Response(content)

    
@app.route('/admin/trace/start', methods=['GET'])
def api_get_admin_trace_start():

    content = 'Admin console'
    trace.start()
    
    return redirect('/admin/trace')

@app.route('/admin/trace/stop', methods=['GET'])
def api_get_admin_trace_stop():

    content = 'Admin console'
    trace.stop()
    return redirect('/admin/trace')


def run_api():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080, threads= 20)
    #app.run(host='0.0.0.0', debug=False)


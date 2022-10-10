import cProfile
import pstats
from io import StringIO
import sys


profiler = cProfile.Profile()
status = 'None'

def start():
    """Start profiler tracing
    """
    global profiler
    global status
    status = 'started'

    profiler.enable()

def stop():
    """Stops and dump profiler tracing
    """
    
    global profiler
    global status
    status = 'completed'
    profiler.disable()
    

def get():
    """
    """
    global profiler

    # Change standard out 
    tmp = sys.stdout
    my_result = StringIO()
    sys.stdout = my_result

    # Get results
    profiler.dump_stats("example.stats")
    stats = pstats.Stats("example.stats")

    # Print results    
    print('bob')
    stats.sort_stats("cumtime").print_stats(150)
    
    # Revert back standard out
    sys.stdout = tmp

    return my_result.getvalue()
    
def get_status():
    global status
    return status
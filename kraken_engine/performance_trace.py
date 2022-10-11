import cProfile
import pstats
from io import StringIO
import sys
import yappi


#profiler = cProfile.Profile()
status = 'None'

def start():
    """Start profiler tracing
    """
    global yappi
    global status
    status = 'started'

    yappi.set_clock_type("cpu") # Use set_clock_type("wall") for wall time
    yappi.start()

def stop():
    """Stops and dump profiler tracing
    """
    global yappi
    global status
    yappi.stop()
    status = 'completed'
        

def get():
    """
    """
    global profiler

    # Change standard out 
    tmp = sys.stdout
    my_result = StringIO()
    sys.stdout = my_result

    # Get results


    if 1==1:
        stats = yappi.get_func_stats()
        stats = stats.sort("ttot", "desc")

        x = 0
        for i in stats:
            if x < 50:
                print(i.ncall, i.tsub, i.ttot, i.lineno, i.full_name,)
            x += 1

    if 1==0:
        threads = yappi.get_thread_stats()
        for thread in threads:
            print(
                "Function stats for (%s) (%d)" % (thread.name, thread.id)
            )  # it is the Thread.__class__.__name__
            stats = yappi.get_func_stats(ctx_id=thread.id)
            stats = stats.sort("ttot", "desc")
            
            for i in stats:
                print(i.name, i.module, i.ttot)
    
    # Revert back standard out
    sys.stdout = tmp

    return my_result.getvalue()
    
def get_status():
    global status
    return status
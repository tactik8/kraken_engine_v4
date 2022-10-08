import functools
import datetime
import inspect

import functools
import time

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer




def error_log(func):
    @functools.wraps(func)
    def wrapper_error_log(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return func(*args, **kwargs)
        except Exception as e:
            print('error', e)
            
            content = '-' * 40 + '\n'
            content += str(datetime.datetime.now()) + '\n'
            content += 'module: ' + str(func.__module__) + '\n'
            content += 'function: ' + str(func.__name__) + '\n'
            content += 'args: ' + '\n'
            for i in args:
                content += '  -' + str(i) + '\n'
            content += 'error: ' + str(e) + '\n'
            f = open("error_log.txt", "a")
            f.write(content)
            f.close()
        
    return wrapper_error_log

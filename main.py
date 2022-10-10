import os
from kraken_engine import performance_trace as trace

test_mode = False

trace.start()

if test_mode == True:
    if __name__ == '__main__':
        os.system("pip install pytest")
        os.system("python -m pytest tests -vv")

else:

    import kraken_engine.kraken_engine as e

    e.run_api()

    
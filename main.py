import os


test_mode = False

if test_mode == True:
    if __name__ == '__main__':
        os.system("pip install pytest")
        os.system("python -m pytest tests -vv")

else:

    import kraken_engine.kraken_engine as e

    e.run_api()

    
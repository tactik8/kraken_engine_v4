
import datetime

import os
filepath = 'log/log.txt'
os.makedirs(os.path.dirname(filepath), exist_ok=True)


class Kraken_log:

    def __init__(self, name):
        self.name = name
        self.start_time = datetime.datetime.now()
        self.end_time = None

    def stop(self):
        self.end_time = datetime.datetime.now()
        self.write_to_log()
    
    @property
    def duration(self):

        if self.end_time:
            return (self.end_time-self.start_time).total_seconds()
        else:
            return 0

    def write_to_log(self):

        content = str(datetime.datetime.now()) + ' ' + self.name + '-' + str(self.duration) + '\n'
        
        with open('log/log.txt', 'a') as f:
            f.write(content)
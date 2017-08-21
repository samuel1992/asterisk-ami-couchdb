import os, errno
import logging

from datetime import datetime
from config import config

path = config['log_directory'] + '/urd.log'
logging.basicConfig(filename=path, level=logging.INFO)

def create_log_directory():
    directory = config['log_directory']

    try:
        os.makedirs(directory)
    except OSError,e:
        if e.errno != errno.EEXIST:
            raise

def access_log(message):
    message = datetime.now().strftime(" %F %T ") + message
    logging.info(message)

def error_log(message):
    message = datetime.now().strftime(" %F %T ") + message
    logging.warning(message)

def parse_event(func):
    def func_wrapper(self, event, **kwargs):
        event.keys['Timestamp'] = datetime.now().strftime("%F %T")
        event.keys['Event'] = event.name

        access_log("RECEIVED {0} EVENT".format(event.name))

        return func(self, event, **kwargs)

    return func_wrapper

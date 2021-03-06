import ConfigParser
import logging
import os

from elasticsearch_dsl.connections import connections

import osc.handlers.slackbot as slack_handler
import osc.handlers.file as file_handler

import atexit

config = ConfigParser.ConfigParser(defaults={'data_dir': '../data',
                                             'tmp_dir': '../tmp',
                                             'errors_dir': '../errors',
                                             'token': '',
                                             'port': None,
                                             'chunk_size': '100',
                                             'flush_bucket': '1000'})

config.read([os.path.expanduser('~/opensmartcountry.ini')])

# Logging configuration
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)

# Directories
data_dir = config.get('importer', 'data_dir')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

tmp_dir = config.get('importer', 'tmp_dir')
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

error_dir = config.get('importer', 'errors_dir')
if not os.path.exists(error_dir):
    os.makedirs(error_dir)

dataframes_dir = config.get('importer', 'dataframes_dir')
if not os.path.exists(dataframes_dir):
    os.makedirs(dataframes_dir)

#Inforiego
inforiego_daily_url=config.get('inforiego', 'url.daily')
inforiego_user=config.get('inforiego', 'user')
inforiego_password=config.get('inforiego', 'passwd')
inforiego_index=config.get('inforiego', 'index')
inforiego_daily_mapping=config.get('inforiego', 'daily.mapping')
inforiego_station_mapping=config.get('inforiego', 'station.mapping')


#web
url = config.get('web', 'url')

# Error handler
class ErrorHandler:

    error_handlers = None

    def __init__(self, error_handlers):
        self.error_handlers = error_handlers

    def error(self, module_name, function_name, message):
        for handler in self.error_handlers:
            handler.error(module_name, function_name, message)

    def warning(self, module_name, function_name, message):
        for handler in self.error_handlers:
            handler.warning(module_name, function_name, message)

    def flush(self):
        for handler in self.error_handlers:
            handler.flush()

error_handler = ErrorHandler([slack_handler.ErrorHandler(config.get('slack', 'token'),
                                                         config.getint('slack', 'flush_bucket'),
                                                         error_dir,
                                                         url),
                              file_handler.ErrorHandler(config.get('importer', 'tmp_dir'))])


def flush_handlers():
    error_handler.flush()


atexit.register(flush_handlers)

# Elastic Search
connections.create_connection('default', hosts=[
    {'host': config.get('elasticsearch', 'host'),
     'port': config.get('elasticsearch', 'port')}],
                              timeout=1200)


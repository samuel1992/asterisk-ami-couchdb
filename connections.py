import couchdb
import dataset 

from utils import access_log, error_log
from config import config

err_log_file = config['log_directory'] + '/error.log'
access_log_file = config['log_directory'] + '/access.log'


try:
    mydb = dataset.connect('mysql://{0}:{1}@{2}:{3}/{4}'.format(config['mydb_user'],
                                                                config['mydb_password'],
                                                                config['mydb_address'],
                                                                config['mydb_port'],
                                                                config['mydb_name']))
    access_log("CONNECTED AT MYSQL DB")
except Exception, e:
    error_log("MYSQL CONNECTION " + str(e))


try:
    couch = couchdb.Server('http://{0}:{1}@{2}:{3}/'.format(config['couchdb_user'],
                                                            config['couchdb_password'],
                                                            config['couchdb_address'],
                                                            config['couchdb_port']))
    db = couch[config['couchdb_name']]
    access_log("CONNECTED AT COUCH DB")
except Exception, e:
    error_log("COUCH CONNECTION " + str(e))


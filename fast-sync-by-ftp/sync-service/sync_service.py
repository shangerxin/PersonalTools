#! /usr/bin/python
# author:Edwin Shang
# Time: 2016-03-14
# Design for quickly sync and copy remote content by a single request 
# Implementation:
# The server recieve a request then compress the aim directorys into small volumes 
# of zip files. The compressed zip files will saved to the FTP server. 
# After the compression done. The server will send a message to the client 
# When the client is notified the aim files are done, it will start several 
# FTP connections to parallel sync all the zip volumes from the FTP server 
# After the sync done. The client will start unzip the file to specify location
# When the unzip is done, will notify the user. 
# To improve the performance we could use cache to save the previous copied files 
# to the server and use robo copy to sync the changes

import os 
import SimpleXMLRPCServer
import json
import multiprocessing
import socket
import logging 
import logging.handlers
import subprocess
import threading 
import doctest
import argparse
import xmlrpclib
import shutil
import collections 

#>7z a f:\tc-script.zip f:\tc-script\* -v12k
#>7z a f:\tc-script.zip f:\tc-script\*

class Task(object):
    def __init__(self, *args, **kwargs):
        self.src       = kwargs.get('src')
        self.user      = kwargs.get('user')
        self.timestamp = kwargs.get('timestamp')
        self.port      = kwargs.get('port')
        self.client    = kwargs.get('client')

    def __str__(self):
        return '__type__:task, src:{src}, user:{user}, timestamp:{timestamp}, port:{port}, client:{client}'.format(src=self.src,
                                                                                                            user=self.user,
                                                                                                            timestamp=self.timestamp,
                                                                                                            port=self.port,
                                                                                                            client=self.client)
    @property
    def obj(self):
        return {'__type__':'task',
                'src':self.src,
                'user':self.user,
                'timestamp':self.timestamp,
                'port':self.port,
                'client':self.client}

#task is a json contain the relative parameters 
#{src, user, timestamp, port}
#hostname           = lambda :socket.gethostname()
hostname		   = lambda :'15.107.8.92'
default_port  	   = 8080 #Isral machine works on 1028
tasks              = multiprocessing.Queue()
ftp_root           = r'c:\ftp_root'
ftp_server         = hostname()
ftp_port           = 21
ftp_user           = 'edwin'
ftp_password       = 'edwin'
file_pattern       = 'archives.zip'
information        = collections.namedtuple('information', ['info', 'result', 'error'])
info_types         = information(info='info', result='result', error='error')
cache_root         = r'c:\cache_root'
exe7z              = r'C:\Program Files\7-Zip\7z.exe'
#exe7z              = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'bin/7z.exe')
task_arrived_event = multiprocessing.Event()
log_rfile_handler  = logging.handlers.RotatingFileHandler('sync-service.log',maxBytes=10485760)
log_rfile_handler.setFormatter(logging.Formatter('%(levelname)s \t %(asctime)s \t pid:%(process)d \t %(message)s'))

def parse_cmdline(arg_list=None):
    '''
    Parse the command parameters 

    @arg_list, the arguments list which is used for test purpose 
    @return, an arguments object which property contain the defined parameters 

    >>> args = parse_cmdline("-p 8000 -t".split()).args
    >>> args.port
    8000
    >>> args.test
    True
    '''
    ps =argparse.ArgumentParser(description='Remote sync server, design for quickly sync remote files')
    ps.add_argument('-p', '--port', type=int, help='The port to start the server')
    ps.add_argument('-t', '--test', default=False, help='Run all the document test', action='store_true')
    ps.args = ps.parse_args(arg_list)
    return ps


def robo_copy(src, dst):
    '''
    '''



def zip_path_if_not_cached(src, dst, volume_size='12m', exe7z=exe7z):
    '''
    zip a specify directory into several volumes, if the output directory already exist then the 
    zip process will be skipped

    #>>> zip_volumes('f:/build', 'f:/7zip', exe7z='D:/Project/PersontalTools/fast-sync-by-ftp/sync-service/bin/7z.exe')
    #'f:/7zip'
    #>>> os.path.isfile('f:/7zip/archives.zip.001')
    #True
    '''
    if not os.path.isdir(dst):
        os.mkdir(dst)

        archive_path = os.path.join(dst, file_pattern)
        cmd = '"{exe7z}" a {output} {source} -v{volume_size} '.format(exe7z=exe7z,
                                                                        output=archive_path,
                                                                        source=src,
                                                                        volume_size=volume_size)
        p = subprocess.Popen([exe7z, 'a', archive_path, src, '-v%s' % volume_size], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(p.communicate())

def notify_client(client, port, info):
    '''
    notify a information to the client 
    '''
    c = xmlrpclib.ServerProxy('http://%s:%s' % (client, port))
    c.notify(json.dumps(info))

def init_logger(logger, level):
    logger.setLevel(level)
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(log_rfile_handler)
    
def space_keeper():
    pass

def handle_task():
    '''
    handle the task in the task queue 
    '''
    logger = multiprocessing.get_logger()
    init_logger(logger, multiprocessing.SUBDEBUG)
    logger.info('Start handling task')
    while True:
        task = None 
        try:
            if tasks.empty():
                task_arrived_event.wait()
                task_arrived_event.clear()
            else:
                task = tasks.get()
                logging.info('Start handle task %s' % task)
                notify_client(task.client, task.port, {'__type__':info_types.info,'message':'Start handling task'})
                subfolder = task.src.replace(':', '_').replace('\\', '_').replace('/', '_')
                ftp_cache = os.path.join(ftp_root, subfolder)
                is_cached = os.path.exists(ftp_cache)
                if os.path.exists(task.src) or is_cached:
                    zip_path_if_not_cached(task.src, ftp_cache)

                    notify_client(task.client, 
                                  task.port, 
                                  {'__type__'    :info_types.result, 
                                   'ftp_path'    :os.path.join('/', subfolder), 
                                   'ftp_server'  :ftp_server,
                                   'ftp_port'    :ftp_port,
                                   'ftp_user'    :ftp_user,
                                   'ftp_password':ftp_password})
                else:
                    notify_client(task.client, task.port, {'__type__':info_types.error, 'message':'The aim directory not exist'})
        except Exception as e:
            logger.error('Handle task %s fail, error info %s' % (task, e))

def as_task(dict_obj):
    '''
    A hook function to help convert json to Task object 
    >>> task = as_task({'__type__':'task', 'src':'c:/abc', 'user':'admin', 'timestamp':'2016-03-14', 'port':10101, 'client':'localhost'})
    >>> isinstance(task, Task)
    True
    >>> task = as_task({})
    >>> task == None
    True
    '''
    if '__type__' in dict_obj and dict_obj['__type__'] == 'task':
        return Task(src       = dict_obj['src'],
                    user      = dict_obj['user'],
                    timestamp = dict_obj['timestamp'],
                    port      = dict_obj['port'],
                    client    = dict_obj['client'])

def append_task(task_json):
    '''
    append the required task into the task queue 
    >>> append_task('{"src": "c:/append", "timestamp": "2016-03-14", "__type__": "task", "client": "localhost", "user": "admin", "port": 10101}')
    >>> tasks.qsize()
    1L
    '''
    task = json.loads(task_json, object_hook=as_task)
    if task:
        tasks.put(task)
        task_arrived_event.set()
        return True 
    else:
        return False

if __name__ == '__main__':
    multiprocessing.freeze_support() 
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)
    logging.getLogger().addHandler(log_rfile_handler)
    args = parse_cmdline().args
    if args.test:
        doctest.testmod()
    else:
        hostport = args.port if args.port else default_port
        proc = threading.Thread(target=handle_task)
        proc.start()
        server = SimpleXMLRPCServer.SimpleXMLRPCServer((hostname(), hostport), allow_none=True)
        server.register_introspection_functions()
        server.register_function(append_task)
        logging.info('Start sync service at %s:%s' % (hostname(), hostport))
        server.serve_forever()






































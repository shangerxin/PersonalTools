import os
import xmlrpclib
import ftplib
import threading
import sys
import doctest
import getpass
import argparse
import multiprocessing
import SimpleXMLRPCServer
import socket
import collections
import json
import logging
import threading
import datetime
import subprocess
import signal
import ctypes
import datetime
import ConfigParser
import time

user                    = getpass.getuser()
file_pattern            = 'archives.zip'
hostname                = '16.60.160.90'
hostport                = 1028
clientip                = '15.107.8.92'
output_path             = ''
max_connection          = 5
default_port            = 8081
client_port             = default_port
exe7z                   = 'C:\\Program Files\\7-Zip\\7z.exe'
is_clean                = False
is_buffer               = False
is_download             = False 
is_override             = False
information             = collections.namedtuple('information', ['info', 'result', 'error'])
info_types              = information(info='info', result='result', error='error')
cwd                     = os.path.split(os.path.realpath(__file__))[0]
tasks                   = multiprocessing.Queue()
download_complete_event = multiprocessing.Event()
complete_event          = multiprocessing.Event()
inserted_task_event     = multiprocessing.Event()
worker_semaphore        = None
log_format              = None 
log_level               = None 
log_level_map           = {'warn':logging.WARN, 'info':logging.INFO, 'debug': logging.DEBUG, 'error':logging.ERROR}

class Task(object):

    def __init__(self, *args, **kwargs):
        self.src       = kwargs.get('src')
        self.user      = kwargs.get('user')
        self.timestamp = kwargs.get('timestamp')
        self.port      = kwargs.get('port')
        self.client    = kwargs.get('client')

    def __str__(self):
        return '__type__:task, src:{src}, user:{user}, timestamp:{timestamp}, port:{port}, client:{client}'.format(src=self.src, user=self.user, timestamp=self.timestamp, port=self.port, client=self.client)

    @property
    def json(self):
        return {'__type__' : 'task',
                'src'      : self.src,
                'user'     : self.user,
                'timestamp': self.timestamp,
                'port'     : self.port,
                'client'   : self.client}

def dir(path):
    if os.path.exists(path):
        return path
    raise argparse.ArgumentError('The given path %s do not exst' % path)


def parse_config(config_path):
    '''
    Parse the configuration
    >>> file_pattern, hostname, hostport, clientip, max_connection, clientport, exe7z, log_format, log_level = parse_config('config.config')
    >>> file_pattern   == 'archives.zip'
    True
    >>> hostname       == '16.60.160.90'
    True
    >>> hostport       == 1028
    True
    >>> clientip       == '15.107.8.92'
    True
    >>> max_connection == 30
    True
    >>> clientport     == 8081
    True
    >>> exe7z 
    'C:\\\\Program Files\\\\7-Zip\\\\7z.exe'
    >>> log_level
    '%(levelname)s %(asctime)s pid:%(process)d %(message)s'
    >>> log_format == logging.WARN
    True
    '''
    if os.path.exists(config_path):
        parser = ConfigParser.ConfigParser()
        parser.readfp(open(config_path, 'r'))

        fp = parser.get('setting', 'file_pattern')
        hn = parser.get('setting', 'hostname') 
        hp = parser.getint('setting', 'hostport')   
        ci = parser.get('setting', 'clientip')     
        mc = parser.getint('setting', 'max_connection') 
        cp = parser.getint('setting', 'clientport')
        e7 = parser.get('setting', 'exe7z')   
        lf = parser.get('setting', 'log_format', '%(levelname)s %(asctime)s pid:%(process)d %(message)s')
        ll = log_level_map.get(parser.get('setting', 'log_level'), logging.WARN)

        return (fp, hn, hp, ci, mc, cp, e7, lf, ll)


def parse_cmdline(arg_list = None):
    """
    Parse the command parameters 
    
    @arg_list, the arguments list which is used for test purpose 
    @return, an arguments object which property contain the defined parameters 
    
    #>>> args = parse_cmdline("-p 8000 -t -s hostip -o c:".split()).args
    #>>> args.port
    #8000
    #>>> args.test
    #True
    #>>> args.server
    #'hostip'
    #>>> args.output
    #'c:'
    """
    ps = argparse.ArgumentParser(description='Remote sync server, design for quickly sync remote files', epilog='Created by Edwin, Shang(Shang, Erxin), License under GNU LGPLv3. Version 1.0.0')
    ps.add_argument('source', help='The source path')
    ps.add_argument('-b', '--buffer', action='store_true', help='Only zip and save the aim directory to server', default=False)
    ps.add_argument('-c', '--clean', action='store_true', help='Delete the downloaded zip files, by default will be kept', default=False)
    ps.add_argument('-d', '--download', action='store_true', help='Only download the zipped files without unzip', default=False)
    ps.add_argument('-f', '--force', help='The force override download zip files', action='store_true', default=False)
    ps.add_argument('-n', '--number', help='The parallel download connection number', type=int, default=max_connection)
    ps.add_argument('-p', '--port', type=int, help='Avaliable port number, default %s' % default_port)
    ps.add_argument('output', help='The output path', default=output_path)
    ps.add_argument('-s', '--server', help='The server name', default=hostname)
    #ps.add_argument('-t', '--test', default=False, help='Run all the document test', action='store_true')
    ps.args = ps.parse_args(arg_list)
    return ps


def request_sync(task, hostname, hostport):
    logging.info('Request to sync remote path %s' % task.src)
    c = xmlrpclib.ServerProxy('http://%s:%s' % (hostname, hostport))
    json_task = json.dumps(task.json)
    c.append_task(json_task)


def init_logger(logger, level, log_format):
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(log_format))
    consoleHandler.setLevel(level)
    logger.setLevel(level)
    logger.addHandler(consoleHandler)


def ftp_download(file_path, is_override, output_directory, uri, user, password, worker_semaphore, inserted_task_event, tasks, log_format, log_level):
    """
    download a specify file from the given ftp server and output the specify directory
    
    #>>> ftp_download('/tmp/archives.zip.002', True, 'f:/', '16.60.160.90', 'edwin', 'edwin')
    #>>> os.path.isfile('f:/archives.zip.002')
    #True
    """
    try:
        path, filename = os.path.split(file_path)
        logger         = multiprocessing.get_logger()
        init_logger(logger, log_level, log_format)
        ftp = ftplib.FTP(host=uri, user=user, passwd=password)
        ftp.cwd(path)
        output_file = os.path.join(output_directory, filename)
        logger.info('Start downloading %s' % file_path)
        if os.path.isfile(output_file) and not is_override:
            return
        if os.path.isfile(output_file):
            os.remove(output_file)
        ftp.retrbinary('RETR %s' % filename, lambda data: open(output_file, 'ab').write(data))
        ftp.close()
        logger.info('Complete file to %s' % output_file)
    except Exception as e:
        logger = multiprocessing.get_logger()
        logger.error('Download %s failed, error info %s' % (file_path, e))
        output_file = os.path.join(output_directory, filename)
        if os.path.exists(output_file):
            os.remove(output_file)
        tasks.put(filename)
        inserted_task_event.set()
    finally:
        logger = multiprocessing.get_logger()
        logger.debug('Release lock %s' % id(worker_semaphore))
        worker_semaphore.release()


def parallel_downloads(ftp_server, ftp_port, ftp_user, ftp_password, file_path):
    worker_processes = []
    inserted_task_event.wait()
    inserted_task_event.clear()
    logging.info('Start parallel downloads')
    while True:
        if not tasks.empty():
            logging.debug('Try get semaphore %s' % id(worker_semaphore))
            worker_semaphore.acquire()
            task = tasks.get()
            logging.info('Start handle task %s' % task)
            if not os.path.isdir(output_path):
                os.makedirs(output_path)

            proc = multiprocessing.Process(target = ftp_download, 
                                           args   = (os.path.join(file_path, task),
                                                     is_override,
                                                     output_path,
                                                     ftp_server,
                                                     ftp_user,
                                                     ftp_password,
                                                     worker_semaphore,
                                                     inserted_task_event,
                                                     tasks,
                                                     log_format, 
                                                     log_level))
            worker_processes.append(proc)
            proc.start()
        else:
            logging.info('task queue empty')
            for proc in worker_processes:
                logging.info('wait process %s finished' % proc.pid)
                proc.join()

            if inserted_task_event.is_set():
                inserted_task_event.clear()
                logging.info('inserted new task into queue')
                continue
                
            else:
                logging.info('Complete download')
                download_complete_event.set()
                return


def start_sync(info, output):
    ftp_path     = info['ftp_path']
    ftp_server   = info['ftp_server']
    ftp_port     = info['ftp_port']
    ftp_user     = info['ftp_user']
    ftp_password = info['ftp_password']
    ftp          = ftplib.FTP(ftp_server, ftp_user, ftp_password)
    ftp.cwd(ftp_path)
    files        = ftp.nlst()
    files.sort()
    for file in files:
        if file.startswith(file_pattern):
            tasks.put(file)

    proc = threading.Thread(target=parallel_downloads, args=(ftp_server,
                            ftp_port,
                            ftp_user,
                            ftp_password,
                            ftp_path))
    inserted_task_event.set()
    proc.start()
    download_complete_event.wait()

    if not is_download:
        first_zip_file = os.path.join(output, files[0])
        time.sleep(3) #wait for file I/O completion 
        unzip(first_zip_file, output, exe7z)

    if is_clean and not is_download:
        for f in files:
            os.remove(os.path.join(output_path, f))

    logging.info('Sync file %s complete!' % ftp_path)


def notify(info):
    info = json.loads(info)
    type = info.get('__type__')
    if type == info_types.info:
        logging.info(info['message'])
    elif type == info_types.error:
        logging.error(info['message'])
        complete_event.set()
    elif type == info_types.result:
        try:
            if not is_buffer:
                start_sync(info, output_path)
        except Exception as e:
            logging.error('Sync failed, error info %s' % e)
        finally:
            complete_event.set()
    else:
        logging.warn('Recieve unknown message %s' % info)
    return True


def unzip(src, output, exe7z):
    """
    unzip a specify file to a directory 
    #>>> unzip('f:/archives.zip.001', 'f:', 'D:/Project/PersontalTools/fast-sync-by-ftp/sync-service/bin/7z.exe')
    """
    cmd = '"{exe7z}" x {archive} -o{output} -aoa -y'.format(exe7z=exe7z, archive=src, output=output)
    logging.info('Start unzip with command %s' % cmd)
    p = subprocess.Popen([exe7z,
                         'x',
                         src,
                         '-o%s' % output,
                         '-aoa',
                         '-y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info(p.communicate())


def communicator():
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((clientip, client_port), allow_none=True)
    logging.info('Start sync client at %s:%s' % (clientip, client_port))
    server.register_function(notify)
    server.serve_forever()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    file_pattern, hostname, hostport, clientip, max_connection, clientport, exe7z, log_format, log_level = parse_config(os.path.join(cwd, 'config.config'))
    args = parse_cmdline().args
    logging.basicConfig(format=log_format, level=log_level)
    if 'test' in args and args.test:
        doctest.testmod()
    else:
        start_time       = datetime.datetime.now()
        client_port      = args.port     if args.port     else default_port
        output_path      = args.output   if args.output   else output_path
        is_override      = args.force    if args.force    else is_override
        is_clean         = args.clean    if args.clean    else is_clean
        is_download      = args.download if args.download else is_download
        is_buffer        = args.buffer   if args.buffer   else is_buffer
        max_connection   = args.number   if args.number   else max_connection
        worker_semaphore = multiprocessing.Semaphore(max_connection)
        task             = Task(src       = args.source, 
                                user      = user, 
                                timestamp = datetime.datetime.utcnow().ctime(), 
                                port      = client_port, 
                                client    = clientip)
        monitor          = threading.Thread(target=communicator)
        monitor.start()
        request_sync(task, hostname, hostport)
        complete_event.wait()
        end_time         = datetime.datetime.now()
        spend_time       = end_time - start_time
        logging.info('Sync completed.')
        os.kill(os.getpid(), signal.SIGTERM)
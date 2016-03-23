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
user                    = getpass.getuser()
file_pattern            = 'archives.zip'
hostname                = lambda : '16.60.160.90'
hostport                = 1028
clientip                = lambda : '15.107.8.92'
output_path             = ''
max_connection          = 30
default_port            = 8081
client_port             = default_port
exe7z                   = 'C:\\Program Files (x86)\\7-Zip\\7z.exe'
is_clean                = False
is_override             = False
information             = collections.namedtuple('information', ['info', 'result', 'error'])
info_types              = information(info='info', result='result', error='error')
tasks                   = multiprocessing.Queue()
download_complete_event = multiprocessing.Event()
complete_event          = multiprocessing.Event()
worker_semaphore        = multiprocessing.Semaphore(60)
inserted_task_event     = multiprocessing.Event()

class Task(object):

    def __init__(self, *args, **kwargs):
        self.src = kwargs.get('src')
        self.user = kwargs.get('user')
        self.timestamp = kwargs.get('timestamp')
        self.port = kwargs.get('port')
        self.client = kwargs.get('client')

    def __str__(self):
        return '__type__:task, src:{src}, user:{user}, timestamp:{timestamp}, port:{port}, client:{client}'.format(src=self.src, user=self.user, timestamp=self.timestamp, port=self.port, client=self.client)

    @property
    def obj(self):
        return {'__type__': 'task',
         'src': self.src,
         'user': self.user,
         'timestamp': self.timestamp,
         'port': self.port,
         'client': self.client}


def dir(path):
    if os.path.exists(path):
        return path
    raise argparse.ArgumentError('The given path %s do not exst' % path)


def parse_cmdline(arg_list = None):
    """
    Parse the command parameters 
    
    @arg_list, the arguments list which is used for test purpose 
    @return, an arguments object which property contain the defined parameters 
    
    >>> args = parse_cmdline("-p 8000 -t -s hostip -o c:".split()).args
    >>> args.port
    8000
    >>> args.test
    True
    >>> args.server
    'hostip'
    >>> args.output
    'c:'
    """
    ps = argparse.ArgumentParser(description='Remote sync server, design for quickly sync remote files')
    ps.add_argument('source', help='The source path')
    ps.add_argument('-c', '--clean', action='store_true', help='Keep the copied zip volume files, by default will be keeped')
    ps.add_argument('-f', '--force', help='The force override download zip files', action='store_true', default=False)
    ps.add_argument('-p', '--port', type=int, help='Avaliable port number, default %s' % default_port)
    ps.add_argument('output', help='The output path', default=output_path)
    ps.add_argument('-s', '--server', help='The parallel ftp download thread number', default=hostname())
    ps.add_argument('-t', '--test', default=False, help='Run all the document test', action='store_true')
    ps.args = ps.parse_args(arg_list)
    return ps


def request_sync(task, hostname, hostport):
    logging.info('Request to sync remote path %s' % task.src)
    c = xmlrpclib.ServerProxy('http://%s:%s' % (hostname, hostport))
    json_task = json.dumps(task.obj)
    c.append_task(json_task)


def init_logger(logger, level):
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter('%(levelname)s \t %(asctime)s \t pid:%(process)d \t %(message)s'))
    consoleHandler.setLevel(level)
    logger.addHandler(consoleHandler)


def ftp_download(file_path, is_override, output_directory, uri, user, password):
    """
    download a specify file from the given ftp server and output the specify directory
    
    #>>> ftp_download('/tmp/archives.zip.002', True, 'f:/', '16.60.160.90', 'edwin', 'edwin')
    #>>> os.path.isfile('f:/archives.zip.002')
    #True
    """
    path, filename = os.path.split(file_path)
    logger = multiprocessing.get_logger()
    init_logger(logger, logging.DEBUG)
    try:
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
        logger.info('Complete download to %s' % output_file)
    except Exception as e:
        logger.error('Download %s failed, error info %s' % (file_path, e))
        tasks.put(filename)
        inserted_task_event.set()
    finally:
        worker_semaphore.release()


def parallel_downloads(ftp_server, ftp_port, ftp_user, ftp_password, file_path):
    worker_processes = []
    inserted_task_event.wait()
    inserted_task_event.clear()
    logging.info('Start parallel downloads')
    while True:
        if not tasks.empty():
            worker_semaphore.acquire()
            task = tasks.get()
            proc = multiprocessing.Process(target=ftp_download, args=(os.path.join(file_path, task),
             is_override,
             output_path,
             ftp_server,
             ftp_user,
             ftp_password))
            worker_processes.append(proc)
            proc.start()
        else:
            for proc in worker_processes:
                proc.join()

            if inserted_task_event.is_set():
                inserted_task_event.clear()
                continue
            else:
                download_complete_event.set()
                return


def start_sync(info, output):
    ftp_path = info['ftp_path']
    ftp_server = info['ftp_server']
    ftp_port = info['ftp_port']
    ftp_user = info['ftp_user']
    ftp_password = info['ftp_password']
    ftp = ftplib.FTP(ftp_server, ftp_user, ftp_password)
    ftp.cwd(ftp_path)
    files = ftp.nlst()
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
    first_zip_file = os.path.join(output, files[0])
    unzip(first_zip_file, output, exe7z)
    if is_clean:
        for f in files:
            os.remove(os.path.join(output_path, f))

    logging.info('Sync file %s complete!' % ftp_path)
    complete_event.set()


def notify(info):
    info = json.loads(info)
    type = info.get('__type__')
    if type == info_types.info:
        logging.info(info['message'])
    elif type == info_types.error:
        logging.error(info['message'])
    elif type == info_types.result:
        try:
            start_sync(info, output_path)
        except Exception as e:
            complete_event.set()
            logging.error('Sync failed, error info %s' % e)

    else:
        logging.warn('Recieve unknown message %s' % info)
    return True


def unzip(src, output, exe7z):
    """
    unzip a specify file to a directory 
    >>> unzip('f:/archives.zip.001', 'f:', 'D:/Project/PersontalTools/fast-sync-by-ftp/sync-service/bin/7z.exe')
    """
    cmd = '"{exe7z}" x {archive} -o{output} -aoa'.format(exe7z=exe7z, archive=src, output=output)
    logging.info('Start unzip with command %s' % cmd)
    p = subprocess.Popen([exe7z,
     'x',
     src,
     '-o%s' % output], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info(p.communicate())


def communicator():
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((clientip(), client_port), allow_none=True)
    logging.info('Start sync client at %s:%s' % (clientip(), client_port))
    server.register_function(notify)
    server.serve_forever()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    args = parse_cmdline().args
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)
    if args.test:
        doctest.testmod()
    else:
        start_time = datetime.datetime.now()
        client_port = args.port if args.port else default_port
        output_path = args.output if args.output else output_path
        is_override = args.force if args.force else is_override
        is_clean = args.clean if args.clean else is_clean
        task = Task(src=args.source, user=user, timestamp=datetime.datetime.utcnow().ctime(), port=client_port, client=clientip())
        monitor = threading.Thread(target=communicator)
        monitor.start()
        request_sync(task, hostname(), hostport)
        complete_event.wait()
        end_time = datetime.datetime.now()
        spend_time = end_time - start_time
        logging.info('Sync completed.')
        os.kill(os.getpid(), signal.SIGTERM)
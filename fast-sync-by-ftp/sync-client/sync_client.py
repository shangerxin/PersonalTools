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
import datetime

# 7z e *.zip -opath-to-output -y
user                = getpass.getuser()
file_pattern        = 'archives.zip'
hostname            = lambda:'16.60.160.90'
hostport            = 1028
clientip            = lambda:socket.gethostbyname(socket.gethostname())
output_path         = ''
default_port        = 1028
client_port         = default_port
exe7z               = r'C:\Program Files\7-Zip\7z.exe'
max_threads         = 20
is_override         = False 
current_threads     = 0
information         = collections.namedtuple('information', ['info', 'result', 'error'])
info_types          = information(info='info', result='result', error='error')
tasks               = multiprocessing.Queue()
complete_event      = multiprocessing.Event()
inserted_task_event = multiprocessing.Event()


class Task(object):
    def __init__(self, *args, **kwargs):
        self.src       = kwargs.get('src')
        self.user      = kwargs.get('user')
        self.timestamp = kwargs.get('timestamp')
        self.port      = kwargs.get('port')
        self.client    = kwargs.get('client')

    def __str__(self):
        return 'src:{src}, user:{user}, timestamp:{timestamp}, port:{port}, client:{client}'.format(src=self.src,
                                                                                                    user=self.user,
                                                                                                    timestamp=self.timestamp,
                                                                                                    port=self.port,
                                                                                                    client=self.client)
    def obj(self):
        return {'src':self.src,
                'user':self.user,
                'timestamp':self.timestamp,
                'port':self.port,
                'client':self.client}
                                                                                                   
def dir(path):
    if os.path.exists(path):
        return path 
    else:
        raise argparse.ArgumentError('The given path %s do not exst' % path)

def parse_cmdline(arg_list=None):
    '''
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
    '''
    ps =argparse.ArgumentParser(description='Remote sync server, design for quickly sync remote files')
    ps.add_argument('-p', '--port', type=int, help='The port to start the server')
    ps.add_argument('-a', '--aim', type=dir, help='The aim path')
    ps.add_argument('-o', '--output', help='The output path')
    ps.add_argument('-f', '--force', help='The force override download zip files', action='store_true', default=False)
    ps.add_argument('-k', '--keep', action='store_true', help='Keep the copied zip volume files, by default will be deleted')
    ps.add_argument('-n', '--number', type=int, help='The parallel ftp download thread number', default=20)
    ps.add_argument('-s', '--server', help='The parallel ftp download thread number', default=hostname())
    ps.add_argument('-t', '--test', default=False, help='Run all the document test', action='store_true')
    ps.args = ps.parse_args(arg_list)
    return ps

def request_sync(task, hostname, hostport):
    logging.info('Request to sync remote path %s' % task.src)
    c = xmlrpclib.ServerProxy('http://%s:%s' % (hostname, hostport))
    c.append_task(json.dumps(task.obj))

def ftp_download(file_path, is_override, output_directory, uri, user, password):
    '''
    download a specify file from the given ftp server and output the specify directory

    #>>> ftp_download('/tmp/archives.zip.002', True, 'f:/', '16.60.160.90', 'edwin', 'edwin')
    #>>> os.path.isfile('f:/archives.zip.002')
    #True
    '''
    path, filename = os.path.split(file_path)
    try:
        ftp = ftplib.FTP(host=uri, user=user, passwd=password)
        ftp.cwd(path)
        output_file = os.path.join(output_directory, filename)
        if os.path.isfile(output_file) and not is_override:
            return

        if os.path.isfile(output_file):
            os.remove(output_file)
        
        ftp.retrbinary('RETR %s' % filename, lambda data:open(output_file, 'ab').write(data))
        ftp.close()
    except Exception as e:
        logging.error('Download %s failed, error info %s' % (file_path, e))
        tasks.put(filename)
        inserted_task_event.set()

def parallel_downloads(ftp_server, ftp_port, ftp_user, ftp_password, file_path):
    worker_processes = []
    inserted_task_event.wait()
    while True:
        if not tasks.empty():
            task = tasks.get()
            proc = multiprocessing.Process(target=ftp_download, args=(os.path.join(file_path, task), 
                                                                      is_override, 
                                                                      output_path, 
                                                                      server, 
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
                complete_event.set()
                return

#{'__type__':'result', 
#'ftp_path':path, 
#'ftp_server':ftp_server,
#'ftp_port':ftp_port,
#'ftp_user':ftp_user,
#'ftp_password':ftp_password}
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

    proc = multiprocessing.Process(target=parallel_downloads, args=(ftp_server, ftp_port, ftp_user, ftp_password, ftp_path))
    proc.start()
    inserted_task_event.set()
    complete_event.wait()
    unzip(os.path.join(output, files[0]), output, exe7z)
    logging.info('Sync file %s complete!' % ftp_path)
    sys.exit()


def notify(info):
    info = json.loads(info)
    type = info.get('__type__')
    if type == info_types.info:
        logging.info(info['message'])
    elif type == info_types.error:
        logging.error(info['message'])
    elif type == info.result:
        start_sync(info)
    else:
        logging.warn('Recieve unknown message %s' % info)
    
def unzip(src, output, exe7z):
    '''
    unzip a specify file to a directory 
    >>> unzip('f:/archives.zip.001', 'f:', 'D:/Project/PersontalTools/fast-sync-by-ftp/sync-service/bin/7z.exe')
    '''
    cmd = '"{exe7z}" e {archive} -o{output} -y'.format(exe7z = exe7z,
                                                      archive = src,
                                                      output=output)
    logging.info('Start unzip with command %s' % cmd)
    os.system(cmd)

if __name__ == '__main__':
    args = parse_cmdline().args
    if args.test:
        doctest.testmod()
    else:
        client_port = args.port if args.port else default_port
        output_path = args.output if args.output else output_path
        is_override = args.force if args.force else is_override
        task = Task(src=args.aim,
                    user=user,
                    timestamp=datetime.datetime.utcnow().ctime(),
                    port=client_port,
                    client=clientip)
        server = SimpleXMLRPCServer.SimpleXMLRPCServer((clientip, client_port))
        server.register_function(notify)

        request_sync(task, hostname, hostport)
        server.serve_forever()
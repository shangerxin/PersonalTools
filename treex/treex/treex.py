#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# tree.py
#
# Written by Erxin, Version 1.1.0, 2015-11-11
#
# Prints the tree structure for the path specified on the command line

from os import listdir, sep, walk
from os.path import abspath, basename, isdir, isfile, join
from sys import argv
from argparse import ArgumentParser
from pprint import pprint as pp
from collections import namedtuple
import logging
import sys
import codecs

def commandline_arg(bytestring):
    unicode_string = bytestring.decode(sys.getfilesystemencoding())
    return unicode_string

def parse_cmdline():
    ps = ArgumentParser(description='A Cmd Line Tool for Graphically displays the folder structure of a drive or path',
                        epilog = 'Created by Edwin, Shang(Shang, Erxin) License under GNU GPLv3. Version 1.0.0')
    ps.add_argument('-f', '--file', help='Display the names of the files in each folder', action='store_true')
    ps.add_argument('-d', '--depth', help='Display the depth number', type=int, default=-1)
    ps.add_argument('-m', '--mark', help='Mark the item is file or directory', action='store_true')
    ps.add_argument('-e', '--ellipsis', help='Mark the next sub-item with ellipsis', action='store_true')
    ps.add_argument('path', nargs=1, type=commandline_arg)
    args = ps.parse_args()
    
    return args

def tree(dir, depth, is_ellipsis, is_print_files=False):
    if isdir(dir):
        print(u'Folder path listing')
        dmap      = {}
        cur_depth = 0
        max_depth = depth + 1 if is_ellipsis else depth
        for cur_root, subdirs, files in walk(dir):
            dirs      = dir_array(cur_root, dir)
            cur_depth = len(dirs)

            is_reachable_dir = ((max_depth >= 0 and cur_depth <= max_depth) or max_depth < 0)
            is_reachable_file = ((max_depth >= 0 and cur_depth <= max_depth -1) or max_depth < 0)
            #ignore the root directory which pass by the parameter dir
            # and only iterator to the given max depth
            if dirs and is_reachable_dir: 
                cmap, cdir = init_and_get_sub_dict(dirs, dmap)
                if is_print_files and is_reachable_file:
                    for f in files:
                        cmap[cdir].setdefault(f, None)

            #if it is the root directory and required to print files
            if not dirs and is_print_files:
                for f in files:
                    dmap.setdefault(f, None)
    return dmap

def sprint(s):
    s = s.encode('utf-8')
    print(s)

def map_readable(dmap, is_ellipsis, is_mark, max_depth, root):
    '''
    to produce a lines like
    
\---win32
    +---bin
    |   +---chrome
    |   |   +---en-US
    |   |   |   \---locale
    |   |   |       \---en-US
    |   |   |           +---alerts
    |   |   |           +---autoconfig
    |   |   |           +---cookie
    |   |   |           +---formautofill
    |   |   |           +---global
    |   |   |           |   +---devtools
    |   |   |           |   +---dom
    |   |   |           |   +---layout
    |   |   |           |   +---mathml
    ...

    '''
    headers = namedtuple('headers', 'empty bar plus_dash slash_dash ellipsis')
    hd = headers(u'    ', u'|   ', u'+---', u'\---', u'... ')

    sprint(abspath(root))
    pre_line = u''
    for line in travel_deep_first(dmap, hd, max_depth, is_ellipsis, is_mark):
        if is_ellipsis:
            if pre_line and line.replace(u'\\', u'+') != pre_line:
                sprint(line)
            elif not pre_line:
                sprint(line)

            pre_line = line
        else:
            sprint(line)


def travel_deep_first(dmap, headers, max_depth, is_ellipsis, is_mark):
    keys         = get_sorted_keys(dmap)
    header_stack = []
    len_keys     = len(keys)
    key_stack    = [keys] if len_keys > 0 else []
    index_stack  = [0] if len_keys > 0 else []
    dirs         = []
    cur_depth    = 0
    delta_depth  = 0
    prefix       = u''
    
    while True and index_stack:
        key_index      = index_stack[-1]
        key            = keys[key_index]

        dirs.append(key)
        cur_depth      = len(dirs)
        last_key_index = len_keys - 1

        if len_keys == 1:
            adjust_preheader(header_stack, headers)
            header_stack.append(headers.slash_dash)
                
        elif len_keys > 1:
            if key_index == last_key_index:
                adjust_preheader(header_stack, headers)
                header_stack.append(headers.slash_dash)
                
            else:
                adjust_preheader(header_stack, headers)
                header_stack.append(headers.plus_dash)

        if is_mark:
            prefix = u'[d]' if is_dir(dirs, dmap) else u'[f]'

        if is_ellipsis and max_depth > 0:
            if cur_depth <= max_depth:
                tail = key
            else:
                tail = headers.ellipsis
        else:
            tail = key
        ret = u'%s%s%s' % (prefix, u''.join(header_stack), tail)
        
        index_stack[-1] += 1
        if index_stack[-1] == len_keys:
            sub_map = get_dict(dirs, dmap)
            if sub_map:
                keys = get_sorted_keys(sub_map)
                len_keys = len(keys)
                key_stack.append(keys)
                index_stack.append(0)
                yield ret
            else:
                while index_stack and \
                        key_stack and \
                        index_stack[-1] == len(key_stack[-1]):
                    index_stack.pop()
                    key_stack.pop()

                    if dirs:
                        dirs.pop()
                        header_stack.pop()
                    if key_stack:
                        keys = key_stack[-1]
                        len_keys = len(keys)
                yield ret

                if dirs:
                    dirs.pop()
                    header_stack.pop()
            continue

        sub_map = get_dict(dirs, dmap)
        if sub_map:
            keys = get_sorted_keys(sub_map)
            len_keys = len(keys)
            key_stack.append(keys)
            index_stack.append(0)
        else:
            dirs.pop()
            header_stack.pop()

        yield ret

def get_sorted_keys(dmap):
    keys = dmap.keys()
    dir_keys = sorted([k for k in keys if isinstance(dmap[k], dict)])
    file_keys = sorted([k for k in keys if dmap[k] == None])
    return file_keys + dir_keys


def is_dir(dirs, dmap):
    tmp = dmap 
    for dir in dirs:
        tmp = tmp[dir]

    return isinstance(tmp, dict)

def adjust_preheader(header_stack, headers):
    if header_stack:
        pre_header = header_stack.pop()
        if pre_header == headers.plus_dash:
            header_stack.append(headers.bar)
                        
        elif pre_header == headers.slash_dash:
            header_stack.append(headers.empty)
                        
        elif pre_header == headers.empty:
            header_stack.append(headers.empty)

        elif pre_header == headers.bar:
            header_stack.append(headers.bar)

def dir_array(cur_root, root):
    root = abspath(root)
    path = abspath(cur_root)[len(root):]
    
    return [x for x in path.split('\\') if x]

def get_dict(dirs, dmap):
    '''
    unmodify the dmap
    '''
    tdict = dmap
    for dir in dirs:
        if tdict and (dir in tdict):
           tdict = tdict[dir]
    return tdict

def init_and_get_sub_dict(dirs, dmap):
    '''
    get the directory dict along the dir array and return
    the current dict and current directory name
    '''
    tdict = dmap
    for dir in dirs:
        if dir in tdict:
            tdict = tdict[dir]
        else:
            tdict.setdefault(dir, {})
            break
    return (tdict, dirs[-1])

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN, format=u'%(levelname)s\t%(asctime)s %(message)s')
    logging.info(u'get cmdline arguments %s' % argv)

    args  = parse_cmdline()
    path  = args.path[0]
    logging.info(u'get arguments %s' % args)

    dtree = tree(path, args.depth, args.ellipsis, args.file)
    map_readable(dtree, args.ellipsis, args.mark, args.depth, path)
















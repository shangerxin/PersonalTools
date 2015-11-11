#! /usr/bin/env python
# 
# tree.py
#
# Written by Erxin
#
# Prints the tree structure for the path specified on the command line

from os import listdir, sep, walk
from os.path import abspath, basename, isdir, isfile, join
from sys import argv
from argparse import ArgumentParser
from pprint import pprint as pp
from collections import namedtuple
import logging

def parse_cmdline():
    ps = ArgumentParser(description='A Cmd Line Tool for Graphically displays the folder structure of a drive or path')
    ps.add_argument('-f', '--file', help='Display the names of the files in each folder', action='store_true')
    ps.add_argument('-d', '--depth', help='Display the depth number', type=int, default=-1)
    ps.add_argument('-m', '--mark', help='Mark the item is file or directory', action='store_true')
    ps.add_argument('path', nargs=1)
    args = ps.parse_args()
    
    return args

def tree(dir, depth, is_print_files=False):
    if isdir(dir):
        print('Folder path listing')
        dmap = {}
        cur_depth = 0
        for cur_root, subdirs, files in walk(dir):
            dirs = dir_array(cur_root, dir)
            cur_depth = len(dirs)
            #ignore the root directory which pass by the parameter dir
            # and only iterator to the given max depth
            if dirs and ((depth >= 0 and cur_depth <= depth) or \
                         depth < 0): 
                cmap, cdir = init_and_get_sub_dict(dirs, dmap)
                if is_print_files:
                    for f in files:
                        cmap[cdir].setdefault(f, None)

            #if it is the root directory and required to print files
            if not dirs and is_print_files:
                for f in files:
                    dmap.setdefault(f, None)
    return dmap

def map_readable(dmap, is_mark, max_depth, root):
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
    hd = headers('    ', '|   ', '+---', '\---', '... ')

    print(abspath(root))
    for line in travel_deep_first(dmap, hd, is_mark):
        print(line)


def travel_deep_first(dmap, headers, is_mark):
    keys = sorted(dmap.keys())
    header_stack = []
    len_keys = len(keys)
    key_stack = [keys] if len_keys > 0 else []
    index_stack = [0] if len_keys > 0 else []
    dirs = []
    cur_depth = 0
    delta_depth = 0
    
    while True and index_stack:
        key_index = index_stack[-1]
        key = keys[key_index]

        dirs.append(key)
        cur_depth = len(dirs)

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
            prefix = '[d]' if is_dir(dirs, dmap) else '[f]'
            ret = prefix + ''.join(header_stack) + key 
        else:
            ret = ''.join(header_stack) + key
        
        index_stack[-1] += 1
        if index_stack[-1] == len_keys:
            sub_map = get_dict(dirs, dmap)
            if sub_map:
                keys = sorted(sub_map.keys())
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
            keys = sorted(sub_map.keys())
            len_keys = len(keys)
            key_stack.append(keys)
            index_stack.append(0)
        else:
            dirs.pop()
            header_stack.pop()

        yield ret

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
        if tdict and tdict.has_key(dir):
           tdict = tdict[dir]
    return tdict

def init_and_get_sub_dict(dirs, dmap):
    '''
    get the directory dict along the dir array and return
    the current dict and current directory name
    '''
    tdict = dmap
    for dir in dirs:
        if tdict.has_key(dir):
            tdict = tdict[dir]
        else:
            tdict.setdefault(dir, {})
            break
    return (tdict, dirs[-1])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s\t%(asctime)s %(message)s')
    logging.info('get cmdline arguments %s' % argv)
    args = parse_cmdline()
    path = args.path[0]
    logging.info('get arguments %s' % args)
    dtree = tree(path, args.depth, args.file)
    map_readable(dtree, args.mark, args.depth, path)
















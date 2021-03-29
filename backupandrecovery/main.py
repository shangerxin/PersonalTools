import os
import shutil
import uuid
import time
import random

def is_contains(src, records):
    for k, v in records.items():
        try:
            is_same = os.path.samefile(src, k)
        except Exception as e:
            is_same = False
        if is_same:
            return (True, v)
    return (False, 'Failed')


def safe_copy(src, dst, records, record_file):
    try:
        src = os.path.normpath(src)
        to = os.path.normpath(os.path.join(dst, str(uuid.uuid4()) +
                                           os.path.splitext(src)[1]))

        is_src_contained, copy_result = is_contains(src, records)
        if not is_src_contained or \
            (is_src_contained and
             (copy_result == 'Failed' or os.path.getsize(to) == 0)):
            print('copying ', src, to)
            shutil.copy(src, to)
            update_record(src, to, records, record_file)
            time.sleep(2)
    except Exception as e:
        try:
            os.system('xcopy "%s" "%s" /Y /X /R' % (src, to))
        except Exception as e:
            update_record(src, 'Failed', records, record_file)


def read_records(path, records):
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                splitter_index = line.rfind(':')
                k = line[:splitter_index]
                v = line[splitter_index+1:]
                records[k] = v
    else:
        open(path, 'w', encoding='utf-8')


def update_record(k, v, records, record_file):
    records[k] = v
    record_file.write('%s:%s\n' % (k, v))


def shake(array):
    length = len(array)
    for i in range(int(length / 2)):
        rand_index = random.randrange(0, length)
        t = array[0]
        array[0] = array[rand_index]
        array[rand_index] = t

    return array


def backup_files(src, dst):
    records = {}
    if os.path.isdir(dst):
        record_dir = os.path.join(dst, 'record.txt')
        read_records(record_dir, records)
        with open(record_dir, 'a', encoding='utf-8') as record_file:
            if os.path.isdir(src) or (os.path.exists(src) and (not os.path.isfile(src))):
                for root, dirs, files in os.walk(src):
                    print('current dir:', root)
                    files = shake(files)
                    for file in files:
                        safe_copy(os.path.join(root, file),
                                  dst, records, record_file)
            elif os.path.isfile(src):
                safe_copy(src, dst, records, record_file)


if __name__ == '__main__':
    backup_files('h:/', 'g:/usbbackup')

import difflib 
import os 
import doctest
import re
import sys 
import xlsxwriter
from collections import namedtuple


cfg37    = u'./data/tc-firefox-37.txt'
cfg40    = u'./data/tc-firefox-40.txt'
userjs   = u'./data/user.js'

diffs    = namedtuple('diffs', ['changed', 'uniques', 'commons', 'dummy'])
settings = namedtuple('settings', ['overwrite_userjs', 'new_changes', 'uniques', 'pre_settings', 'removes', 'commons'])

splitter = lambda f, m: f.write('%s%s%s\n' % ('='*40, m, '='*40))

def parse_cfg(cfgs, output):
    '''
    Parse the Firefox configuration file

    >>> output = {}
    >>> parse_cfg(['TC.Global.DontPromptOnEnter;true', 'advanced.system.supportDDEExec;false'], output)
    >>> len(output.keys()) == 2
    True
    '''
    if cfgs:
        for cfg in cfgs:
            m = re.match('(.+?);(.*)$', cfg)
            if m:
                k, v = m.group(1), m.group(2)
                output.setdefault(k, v)

def parse_userjs(path):
    '''
    parse the user.js content, load all the configuration settings into dict
    >>> parse_userjs(userjs) != {}
    True
    '''
    if os.path.isfile(path):
        ret = {}
        for line in open(path, 'r'):
            m = re.match('user_pref\("(.+?)",\s*(.+)\);', line)
            if m:
                ret.setdefault(m.group(1), m.group(2))
        return ret

def compare_cfg(cfg0, cfg1):
    '''
    compare two configuration file 

    ndiff function 
    '- ' line unique to sequence 1 
    '+ ' line unique to sequence 2 
    '  ' line common to both sequences 
    '? ' line not present in either input sequence 
    >>> diff0, diff1 = compare_cfg(cfg37, cfg40) 
    >>> diff0 != None 
    True
    >>> diff1 != None 
    True
    >>> len(diff1.changed) + len(diff1.uniques) + len(diff1.commons) == 2647  #2647 is the total number of items in tc-firefox-40.txt
    True
    '''
    if os.path.isfile(cfg0) and os.path.isfile(cfg1):
        diff0    = diffs({}, {}, {}, [])
        diff1    = diffs({}, {}, {}, [])
        gdiffs   = difflib.ndiff(open(cfg0, 'r').readlines(), open(cfg1, 'r').readlines())
        uniques0 = []
        uniques1 = []
        commons  = []
        for d in gdiffs:
            if d:
                h = d[:2]
                if h == '- ':
                    uniques0.append(d[2:])
                elif h == '+ ':
                    uniques1.append(d[2:]) 
                elif h == '? ':
                    diff0.dummy.append(d[2:]) 
                    diff1.dummy.append(d[2:]) 
                else:
                    commons.append(d[2:])

        parse_cfg(uniques0, diff0.uniques)
        parse_cfg(uniques1, diff1.uniques)
        parse_cfg(commons, diff0.commons)
        parse_cfg(commons, diff1.commons)

        set_keys0 = set(diff0.uniques.keys())
        set_keys1 = set(diff1.uniques.keys())

        same_keys = set_keys0 & set_keys1

        for k in same_keys:
            v0 = diff0.uniques.pop(k)
            v1 = diff1.uniques.pop(k)

            diff0.changed.setdefault(k, (v0, v1))
            diff1.changed.setdefault(k, (v1, v0))

        return (diff0, diff1)

def generate_settings(diff, pre_settings):
    '''
    generate the setting result compare to the previous settings and the diff result 

    '''
    set_changes  = set(diff.changed.keys())
    set_pres     = set(pre_settings.keys())
    set_uniques  = set(diff.uniques.keys())
    set_commons  = set(diff.commons.keys())

    overwrite_userjs = set_pres & set_changes
    new_changes  = set_changes - set_pres
    removes = set_pres - (set_uniques | set_changes | set_commons)
    cur_settings = set_pres - removes - overwrite_userjs

    return settings({k:(pre_settings[k], diff.changed[k]) for k in overwrite_userjs},
                    {k:diff.changed[k] for k in new_changes}, 
                     diff.uniques, 
                    {k:pre_settings[k] for k in cur_settings},
                    {k:pre_settings[k] for k in removes},
                    diff.commons)
    

def generate_userjs(diff, cfg_uniques, cfg_new_changes, pre_settings):
    '''
    generate the new user.js file base on the uniques setting, new changes setting and previous settings
    '''

def output_diff(diff, path):
    '''
    output the difference result into a specify path 
    '''
    f = open(path, 'w')
    splitter(f, 'changed items')
    for k, v in diff.changed.items():
        f.write('%s ; %s\n' % (k, v))

    splitter(f, 'uniques items')
    for k, v in diff.uniques.items():
        f.write('%s ; %s\n' % (k, v))

    splitter(f, 'commons items')
    for k, v in diff.commons.items():
        f.write('%s ; %s\n' % (k, v))

    f.close()

def _alphabet_cmp(str0, str1):
    '''
    Alphabet compare the two given strings and ignore the length 

    >>> _alphabet_cmp('abc', 'be')
    1
    >>> _alphabet_cmp('a','a')
    0
    >>> _alphabet_cmp('abc', '')
    1
    >>> _alphabet_cmp('defg', 'a') < 0
    True
    '''
    str0 = str0.lower()
    str1 = str1.lower()
    len0 = len(str0)
    len1 = len(str1)
    if str0 and str1:
        min_len = min(len0, len1)
        for i in range(min_len):
            if str0[i] == str1[i]:
                continue
            else:
                return ord(str0[i]) - ord(str1[i])

    if len0 == len1:
        return 0
    elif len0 > len1:
        return 1
    else:
        return -1

def output_settings(setting, path):
    '''
    output the setting result into a specify path 
    '''
    title = lambda data, sh: sh.write_row(0, 0, data)
    f = open(path, 'w')
    wb = xlsxwriter.Workbook('settings.xlsx')
    ou_st = wb.add_worksheet('FF Overwrite User.js')
    nc_st = wb.add_worksheet('Overwrite Previous Settings')
    un_st = wb.add_worksheet('New Added')
    ps_st = wb.add_worksheet('Unchanged Settings in User.js')
    rm_st = wb.add_worksheet('Removed from User.js')
    cm_st = wb.add_worksheet('Common Settings')
    
    splitter(f, 'overwrite_userjs')
    row = 1
    title(('Item', 'Current in Userjs', 'Firefox Default'), ou_st)
    for k, v in sorted(setting.overwrite_userjs.items(), lambda x, y: _alphabet_cmp(x[0], y[0])):
        f.write('%s ; %s\n' % (k, v))
        ou_st.write(row, 0, k)
        ou_st.write(row, 1, v[0])
        ou_st.write(row, 2, _w(v[1]))
        row += 1

    splitter(f, 'new_changes')
    row = 1
    title(('Item', 'Current Value', 'Previous Value'), nc_st)
    for k, v in sorted(setting.new_changes.items(), lambda x, y: _alphabet_cmp(x[0], y[0])):
        f.write('%s ; %s\n' % (k, v))
        nc_st.write(row, 0, k)
        nc_st.write(row, 1, v[0])
        nc_st.write(row, 2, _w(v[1]))
        row += 1

    splitter(f, 'uniques')
    row = 1
    title(('Item', 'Value'), un_st)
    for k, v in sorted(setting.uniques.items(), lambda x, y: _alphabet_cmp(x[0], y[0])):
        f.write('%s ; %s\n' % (k, v))
        un_st.write(row, 0, k)
        un_st.write(row, 1, _w(v))
        row += 1

    splitter(f, 'pre_settings')
    row = 1
    title(('Item', 'Value'), ps_st)
    for k, v in sorted(setting.pre_settings.items(), lambda x, y: _alphabet_cmp(x[0], y[0])):
        f.write('%s ; %s\n' % (k, v))
        ps_st.write(row, 0, k)
        ps_st.write(row, 1, _w(v))
        row += 1

    splitter(f, 'removes')
    row = 1
    title(('Item', 'Value'), rm_st)
    for k, v in sorted(setting.removes.items(), lambda x, y: _alphabet_cmp(x[0], y[0])):
        f.write('%s ; %s\n' % (k, v))
        rm_st.write(row, 0, k)
        rm_st.write(row, 1, _w(v))
        row += 1

    splitter(f, 'commons')
    row = 1
    title(('Item', 'Value'), cm_st)
    for k, v in sorted(setting.commons.items(), lambda x, y: _alphabet_cmp(x[0], y[0])):
        f.write('%s ; %s\n' % (k, v))
        cm_st.write(row, 0, k)
        cm_st.write(row, 1, _w(v))
        row += 1
    wb.close()
    f.close()

def _w(s):
    return str(s).decode(sys.getfilesystemencoding())

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-t':
        doctest.testmod()
    else:
        diff0, diff1 = compare_cfg(cfg37, cfg40) 

        output_diff(diff0, 'result37.txt')
        output_diff(diff1, 'result40.txt')

        pre_settings = parse_userjs(userjs)
        #cur_settings0 = generate_settings(diff0, pre_settings)
        cur_settings1 = generate_settings(diff1, pre_settings)

        output_settings(cur_settings1, 'setting40.txt')
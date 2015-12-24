import os 
import re
import doctest

PRE_HOOK = '''console.log('start');'''
POST_HOOK = '''console.log('end');'''

NOT_FOUND = -1

def loadjs(path):
    '''
    load the js file from the given path and remove all the comments
    '''
    if os.path.isfile(path):
        lines = open(path, 'r').readlines()
        is_start_multi_lines_comment = False 
        ret = []
        for line in lines:
            if not is_start_multi_lines_comment:
                m = re.match('(.*)/\*', line)
                if m:
                    is_start_multi_lines_comment = True
                    remain = m.group(1)
                    if remain:
                        ret.append(remain)
                    
                    continue

                if is_not_single_line_comment(line):
                    ret.append(line)
            else:
                m = re.match('.*\*/(.*)', line)
                if m:
                    is_start_multi_lines_comment = False 
                    remain = m.group(1)
                    ret.append(remain)
                
        return ret



def is_not_single_line_comment(line):
    '''
    >>> is_not_single_line_comment('   //abc')
    False
    >>> is_not_single_line_comment('   /abe def')
    True
    >>> is_not_single_line_comment('/* abcd */')
    False
    >>> is_not_single_line_comment('/**/')
    False
    '''
    return not (re.match('\s*//', line) or re.match('\s*/\*.*\*/', line))

def get_js_list(path, black_file_list, black_dir_list):
    '''
    Get a JavaScript file list and bypass the black file list and black dir list 

    @path, the aim path is a file or a directory 
    @black_file_list, the file will be excluded. Support regex match 
    @black_dir_list, the dir will be excluded, Support regex match 
    '''
    if os.path.isfile(path):
        return [path]

    elif os.path.isdir(path):
        ret = []
        for root, dirs, files in os.walk(path):
            filtered_dirs = []
            for dir in dirs:
                for bl in black_dir_list:
                    if re.search(bl, dir):
                        dirs.remove(dir)
            

            for f in [x for x in files if x.endswith('.js')]:
                if not any([re.search(bl, f) for bl in black_file_list]):
                    ret.append(os.path.join(root, f))
        return ret

def insert(s, i, sub):
    return '%s%s%s' % (s[:i], sub, s[i:])

def find_pre_pos(line):
    '''
    >>> find_pre_pos('(){')
    3
    '''
    brace_index = line.find('{')
    if brace_index != NOT_FOUND:
        return brace_index + 1
    else:
        return NOT_FOUND

def find_post_pos(line, brace_stack):
    '''
    >>> find_post_pos('#start #end}', ['{'])
    (11, 12, 1)
    >>> find_post_pos('return;}', ['{'])
    (0, 6, 6)
    '''
    len_return = len('return')
    if not brace_stack:
        return (NOT_FOUND, 0, 0)

    first_brace_pos = NOT_FOUND
    for index, c in enumerate(line):
        if c == '{':
            brace_stack.append(c)
        elif c == '}':
            brace_stack.pop()
            first_brace_pos = index + 1 if first_brace_pos == NOT_FOUND else first_brace_pos
            if not brace_stack:
                return (index, index+1, 1)

        filtered = line[:index]
        m = re.search('[^a-zA-Z0-9_]*return[^a-zA-Z0-9_]*', filtered)
        if m:
            finded = m.group()
            return (filtered.find('return'), len(filtered), len_return)
        
    return (NOT_FOUND, first_brace_pos, 0)

def is_contain_post_symbols(line):
    result = line.find('}') != NOT_FOUND or re.search('[^a-zA-Z0-9_]*return[^a-zA-Z0-9_]*', line)
    return result

def find_func_index(line, char_index):
    '''
    >>> find_func_index('function foo(){', 0)
    (0, 12)
    >>> find_func_index('abc; function (){', 3)
    (3, 14)
    '''
    m = re.search('[^a-zA-Z0-9_]*function[\s\(]*[a-zA-Z0-9_]*(?=\()', line)
    if m:
        finded = m.group()
        return (line.index(finded), line.index(finded) + len(finded))
    else:
        return (NOT_FOUND, NOT_FOUND)

def handle_func(content, line_index, char_index, pre, post):
    brace_stack = []
    is_handled_pre = False
    while True:
        unhandled_line = content[line_index][char_index:]
        if not is_handled_pre:
            pre_start = find_pre_pos(unhandled_line)
            if pre_start != NOT_FOUND:
                changed_line = insert(unhandled_line, pre_start, pre)
                content[line_index] = content[line_index][:char_index] + changed_line
                char_index += pre_start + len(pre)
                unhandled_line      = content[line_index][char_index:]
                is_handled_pre      = True
                brace_stack.append('{')
        
        func_start, func_end = find_func_index(unhandled_line, char_index)
        if func_start != NOT_FOUND and not is_contain_post_symbols(unhandled_line[:func_start]):
            char_index += func_end
            line_index, char_index = handle_func(content, line_index, char_index, pre, post)
            unhandled_line = content[line_index][char_index:]
            
        if is_handled_pre:
            while True:
                post_start, first_brace_pos, additional_step = find_post_pos(unhandled_line, brace_stack)
                if post_start != NOT_FOUND:
                    changed_line        = insert(unhandled_line, post_start, post)
                    content[line_index] = content[line_index][:char_index] + changed_line
                    char_index += post_start + len(post) + additional_step
                    unhandled_line      = unhandled_line[first_brace_pos:]
                else:
                    if first_brace_pos != NOT_FOUND:
                        char_index += first_brace_pos

                    break

        if is_handled_pre and not brace_stack:
            return (line_index, char_index if char_index <= len(content[line_index]) else 0)
        else:
            if find_func_index(unhandled_line, char_index)[0] == NOT_FOUND:
                line_index += 1
                char_index = 0
                

def add_hook(content, pre, post):
    '''
    >>> ct = loadjs('test-fixtures/test-fixture.js')
    >>> hooked = add_hook(ct, PRE_HOOK, POST_HOOK)
    >>> open('test-fixtures/test-output.js', 'w').writelines(hooked)
    >>> import filecmp
    >>> filecmp.cmp('test-fixtures/test-answer.js', 'test-fixtures/test-output.js')
    True
    '''
    line_index = 0
    char_index = 0
    for index, line in enumerate(content):
        if index >= line_index:
            func_start, func_end = find_func_index(line, char_index)
            if func_start != NOT_FOUND:
                char_index = func_end
                line_index, char_index = handle_func(content, index, char_index, pre, post)

            else:
                char_index = 0
                continue
    return content

if __name__ == '__main__':
    #error_list = []
    #for f in get_js_list(r'C:\Program Files (x86)\HP\LoadRunner\dat\TCChrome\Extension - Copy', ['.*jquery.*', '.*galleria.*', '.*knockout.*'], ['libs', 'rotate3Di-1.6', 'TPS']):
    #    ct = loadjs(f)
    #    try:
    #        if ct:
    #            hooked = add_hook(ct, "console.log('start');", "console.log('end');")
    #            open(f, 'w').writelines (hooked)
    #            print(f)
    #    except Exception as e:
    #        error_list.append(f + '\n')

    #open('error.log', 'w').writelines(error_list)


    #f = r'C:\Program Files (x86)\HP\LoadRunner\dat\TCChrome\Extension - Copy\DebuggerBridge.js'
    #ct = loadjs(f)
    #hooked = add_hook(ct, "console.log('start');", "console.log('end');")
    #if hooked:
    #    open(f, 'w').writelines(hooked)

    doctest.testmod()

import os 
import re
import doctest

PRE_HOOK = '''console.log('start');'''
POST_HOOK = '''console.log('end');'''

NOT_FOUND = -1

def loadjs(path):
    if os.path.isfile(path):
        return open(path, 'r').readlines()

def get_js_list(path, black_file_list, black_dir_list):
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        ret = []
        for root, dirs, files in os.walk(path):
            filtered_dirs = [x for x in dirs if x in black_dir_list]
            for fd in filtered_dirs:
                dirs.remove(fd)
            for f in files:
                if f.endswith('.js') and x not in black_file_list:
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
    (11, 12)
    >>> find_post_pos('return;}', ['{'])
    (0, 7)
    '''
    if not brace_stack:
        return (NOT_FOUND, NOT_FOUND)

    for index, c in enumerate(line):
        if c == '{':
            brace_stack.append(c)
        elif c == '}':
            brace_stack.pop()
            if not brace_stack:
                return (index, index+1)

        filtered = line[:index]
        m = re.search('[^a-zA-Z0-9_]*return[^a-zA-Z0-9_]*', filtered)
        if m:
            finded = m.group()
            return (filtered.find('return'), filtered.find('return') + len('return') + 1)
        
    return (NOT_FOUND, NOT_FOUND)

def find_func_index(line, char_index):
    '''
    >>> find_func_index('function foo(){', 0)
    (0, 12)
    >>> find_func_index('abc; function (){', 3)
    (3, 15)
    '''
    m = re.search('[^a-zA-Z0-9_]*function[\s\(]*[a-zA-Z0-9_]*', line)
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
        if func_start != NOT_FOUND:
            char_index += func_end
            line_index, char_index = handle_func(content, line_index, char_index, pre, post)
            unhandled_line = content[line_index][char_index:]
            
        if is_handled_pre:
            while True:
                post_start, post_end = find_post_pos(unhandled_line, brace_stack)
                if post_start != NOT_FOUND:
                    changed_line        = insert(unhandled_line, post_start, post)
                    content[line_index] = content[line_index][:char_index] + changed_line
                    char_index += post_start + len(post) + 1 #move additional one step to set after the char }
                    unhandled_line      = unhandled_line[post_end:]
                else:
                    break

        if is_handled_pre and not brace_stack:
            
            return (line_index, char_index if char_index <= len(content[line_index]) else 0)
        else:
            line_index += 1
            char_index = 0
                

def add_hook(content, pre, post):
    '''
    >>> ct = loadjs('test-fixtures/test-fixture.js')
    >>> hooked = add_hook(ct, PRE_HOOK, POST_HOOK)
    >>> answer = loadjs('test-fixtures/test-answer.js')
    >>> hooked == answer
    True
    >>> open('test-fixtures/test-output.js', 'w').writelines(hooked)
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
    #normal_list = []
    #for f in get_js_list(r'C:\Program Files (x86)\HP\LoadRunner\dat\TCChrome\Extension - Copy', [], []):
    #    ct = loadjs(f)
    #    try:
    #        hooked = add_hook(ct, "console.log('start');", "console.log('end');")
    #        open(f, 'w').writelines(hooked)
    #        normal_list.append(f+'\n')
    #    except Exception as e:
    #        error_list.append(f)

    #open('error.log', 'w').writelines(error_list)


    f = r'C:\Program Files (x86)\HP\LoadRunner\dat\TCChrome\Extension - Copy\DebuggerBridge.js'
    ct = loadjs(f)
    hooked = add_hook(ct, "console.log('start');", "console.log('end');")
    if hooked:
        open(f, 'w').writelines(hooked)

    #doctest.testmod()

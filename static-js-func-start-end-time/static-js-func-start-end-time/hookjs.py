import os 
import re
import doctest

PRE_HOOK = '''console.log('start');'''
POST_HOOK = '''console.log('end');'''

NOT_FOUND = -1

def loadjs(path):
    if os.path.isfile(path):
        return open(path, 'r').readlines()

def get_js_list(path):
    pass

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
    >>> find_post_pos('() {#start #end}', [])
    15
    >>> find_post_pos('() {return;}', [])
    4
    '''
    for index, c in enumerate(line):
        if c == '{':
            brace_stack.append(c)
        elif c == '}':
            brace_stack.pop()
            if not brace_stack:
                return index

        filtered = line[:index]
        m = re.search('[^a-zA-Z0-9_]*return[^a-zA-Z0-9_]*', filtered)
        if m:
            finded = m.group()
            return finded.find('return')
        
    return NOT_FOUND

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
            
        if is_handled_pre:
            while True:
                post_start = find_post_pos(unhandled_line, brace_stack)
                if post_start != NOT_FOUND:
                    changed_line        = insert(unhandled_line, post_start, post)
                    content[line_index] = content[line_index][:char_index] + changed_line
                    char_index += post_start + len(post) + 1
                    unhandled_line      = content[line_index][char_index:]
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
    doctest.testmod()

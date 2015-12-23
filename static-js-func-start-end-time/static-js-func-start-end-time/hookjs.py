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
    pass

def find_post_pos(line, brace_stack):
    pass

def find_func_index(line, line_index, char_index):
    m = re.search('[^a-zA-Z0-9_]*function[\s\(]*[^a-zA-Z0-9_]*', line)
    if m:
        finded = m.group()
        return (line.index(finded), line(finded) + len(finded))
    else:
        return (NOT_FOUND, NOT_FOUND)

def handle_func(content, line_index, char_index, pre, post):
    brace_stack = []
    is_handled_pre = False
    while True:
        unhandled_line = content[line_index][char_index:]
        if not is_handled_pre:
            pre_start, pre_end = find_pre_pos(unhandled_line)
            if pre_start != NOT_FOUND:
                changed_line = insert(unhandled_line, pre_start, pre)
                content[line_index] = content[line_index][:char_index] + changed_line
                char_index += pre_start + len(pre)
                unhandled_line = content[line_index][char_index:]
        
        func_start, func_end = find_func_index(unhandled_line, line_index, char_index)
        if func_start != NOT_FOUND:
            char_index += func_end
            line_index, char_index = handle_func(content, line_index, char_index, pre, post)
            
        if is_handled_pre:
            while True:
                post_start, post_end = find_post_pos(unhandled_line, brace_stack)
                if post_start != NOT_FOUND:
                    changed_line = insert(unhandled_line, post_start, post)
                    content[line_index] = content[line_index][:char_index] + changed_line
                    char_index += post_start + len(post) + 1
                    unhandled_line = content[line_index][char_index:]
                else:
                    break

        if is_handled_pre and not brace_stack:
            return (line_index, char_index)
        else:
            line_index += 1
            char_index = 0
                

def add_hook(content, pre, post):
    line_index = 0
    char_index = 0
    for index, line in enumerate(content):
        if index >= line_index:
            func_start, func_end = find_func_index(line, index, char_index)
            if func_start != NOT_FOUND:
                char_index = func_end
                line_index, char_index = handle_func(content, line_index, char_index, pre, post)
            else:
                char_index = 0
                continue
    return content

if __name__ == '__main__':
    doctest.testmode()

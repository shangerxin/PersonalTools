import os 
import re
import uuid
import doctest
import argparse

PRE_HOOK  = '''console.log('start');'''
POST_HOOK = '''console.log('end');'''

NOT_FOUND = -1

def _replace_string(line):

    '''
    replace all the javascript string into GUID to prevent bring in un-predicate result
    
    @line, code line
    @return, a tuple contain modified line, marks and original substring which is replaced by the mark 

    >>> ret = _replace_string("abc'def'g 2341ag' function (abc){}' xxx...1")
    >>> ret[0].find("'") == -1
    True
    >>> len(ret[1]) == 2
    True
    >>> ret[2][0]
    "'def'"
    >>> ret[2][1]
    "' function (abc){}'"
    '''
    marks, strings = [], []
    while True:
        m = re.search('''(?P<quote>['"]).*?(?P=quote)''', line)
        if m:
            mark   = str(uuid.uuid4())
            string = m.group()
            line   = line.replace(string, mark)
            marks.append(mark)
            strings.append(string)
        else:
            return (line, marks, strings)

def _replace_regex(line):

    '''
    replace all the javascript string into GUID to prevent bring in un-predicate result
    @line, code line 
    @return, a tuple contain modified line, marks and original regex string

    >>> ret = _replace_regex("abc/def/ 2341ag/ <>*dg\/*{}/ xxx...1")
    >>> ret[0].find("/") == -1
    True
    >>> len(ret[1]) == 2
    True
    >>> ret[2][0]
    '/def/'
    >>> ret[2][1]
    '/ <>*dg\\\\/*{}/'
    '''
    marks, regexes = [], []
    while True:
        m = re.search(r'(?<!\\)[/](?!\*).+?(?<!\\)[/]', line)
        if m and line[:line.find(m.group())].find('/*') == NOT_FOUND:
            mark   = str(uuid.uuid4())
            string = m.group()
            line   = line.replace(string, mark)
            marks.append(mark)
            regexes.append(string)
        else:
            return (line, marks, regexes)
            


def _remove_embeded_comments(line):
    '''
    remove the embedded comments contain in a code line 
    
    @line, code line 
    @return, modified line 

    >>> _remove_embeded_comments("abc//efg")
    'abc\\n'
    >>> _remove_embeded_comments("abc/*eft*/abc")
    'abcabc'
    >>> _remove_embeded_comments("abc//abcd\\n")
    'abc\\n'
    '''
    while True:
        m = re.search('/\*.*\*/', line)
        if m:
            line     = line.replace(m.group(), '')
            if re.match('\s*\n', line):
                line = ''
        else:
            break

    m = re.search('(.+)//.*', line)
    if m and m.group(1).strip():
        line = m.group(1) + '\n'
    return line

def _append2ret(ret, line, str_marks, strings, reg_marks, regexes):
    '''
    help method to append line, str_marks, strings, reg_marks, regexes to the list ret

    @ret, a list 
    @line, code line
    @str_marks, a GUID list 
    @strings, a original substring list which is replaced by str_mark
    @reg_marks, a GUID list 
    @regexes, a original regex expression list which is replaced by reg_mark
    
    '''
    iline, istr_mark, istring, ireg_mark, iregex = 0, 1, 2, 3, 4
    ret[iline].append(line)
    ret[istr_mark].append(str_marks)
    ret[istring].append(strings)
    ret[ireg_mark].append(reg_marks)
    ret[iregex].append(regexes)

def loadjs(path):
    '''
    load the js file from the given path and remove all the comments and replaces the strings and regexes 
    with GUID marks

    @path, the full path to the javascript file 
    @return, a tuple contain filtered code lines, string marks, original substrings for each code line, regex marks
    original regex expression for each code line

    >>> ct=loadjs('test-fixtures/test-comment.js')
    >>> import filecmp
    >>> open('test-fixtures/test-comment-output.js','w').writelines(ct[0])
    >>> filecmp.cmp('test-fixtures/test-comment-answer.js', 'test-fixtures/test-comment-output.js')
    True
    '''
    if os.path.isfile(path):
        lines = open(path, 'r').readlines()
        is_start_multi_lines_comment = False 
        ret = ([], [], [], [], []) #contain iline, istr_mark, istring, ireg_mark, iregex = 0, 1, 2, 3, 4
        
        for index, line in enumerate(lines):
            line, str_marks, strings = _replace_string(line)
            line, reg_marks, regexes = _replace_regex(line)
            if not is_start_multi_lines_comment:
                line = _remove_embeded_comments(line)

                m = re.match('(.*)(?<!/)/\*', line)
                if m:
                    is_start_multi_lines_comment = True
                    remain = m.group(1)
                    if remain.replace('\n', ''):
                        _append2ret(ret, remain, str_marks, strings, reg_marks, regexes)
                    continue

                if line and is_not_single_line_comment(line):
                    _append2ret(ret, line, str_marks, strings, reg_marks, regexes)
                else:
                    continue
            else:
                m = re.match('.*\*/(.*)', line)
                if m:
                    is_start_multi_lines_comment = False 
                    remain = m.group(1)
                    if remain.replace('\n', ''):
                        _append2ret(ret, remain, str_marks, strings, reg_marks, regexes)

        return ret



def is_not_single_line_comment(line):
    '''
    check if the given code line is a single line comment or not

    @line, a code line 
    @return, if it is not a comment line then return True, else return False

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
    '''
    insert a given substring into the specify index of the string s 
    '''
    return '%s%s%s' % (s[:i], sub, s[i:])

def find_pre_pos(line):
    '''
    find the pre insert position, which is the always behind the first character '{'

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
    find the post insert position, it will return the position in front of each return statements and
    before the last brace

    @line, the code line
    @brace_stack, the brace stack contain all the current function's '{', whenever the code line contain a 
    '{'. The '{' will be insert into the brace_stack, if encounter a '}' then will pop out a '{' from the stack
    @return, a tuple contain the post insert position, the first encountered '{' position and the additional move
    characters which will be to indicate current filtered character from the code line

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

        if find_func_index(filtered)[0] != NOT_FOUND:
            break
        
    return (NOT_FOUND, first_brace_pos, 0)

def is_contain_post_symbols(line):
    '''
    check if the given code line contain the post insert symbol such as '}' and return statement

    @line, code line 
    @return, if contain then return True else False
    '''

    result = line.find('}') != NOT_FOUND or re.search('[^a-zA-Z0-9_]*return[^a-zA-Z0-9_]*', line)
    return result

def find_func_index(line):
    '''
    check if there is a function definition contain in the given code line

    @line, a code line 
    @return, a tuple contain the function definition start index and function definition end index

    >>> find_func_index('function foo(){')
    (0, 12)
    >>> find_func_index('abc; function (){')
    (5, 14)
    '''
    m = re.search('[^a-zA-Z0-9_\s]*function[\s\(]*[a-zA-Z0-9_]*(?=\()', line)
    if m:
        finded = m.group()
        return (line.index(finded), line.index(finded) + len(finded))
    else:
        return (NOT_FOUND, NOT_FOUND)

def handle_func(lines, line_index, char_index, pre, post):
    '''
    handle a function scope from a given start line index till find the end of the function. During the handling 
    may encounter another function definition. Then the function handle_func will be call recursively by itself

    @lines, the code lines of a JavaScript file
    @line_index, the current handling line index of the JavaScript file 
    @char_index, the current handling char index of the current handling line 
    @pre, the hook code of the pre function call 
    @post, the hook code of the post function call
    @return, a tuple contain the current finished handling line index and char index
    '''

    brace_stack    = []
    is_handled_pre = False
    while True:
        unhandled_line = lines[line_index][char_index:]
        if not is_handled_pre:
            pre_start  = find_pre_pos(unhandled_line)
            if pre_start != NOT_FOUND:
                changed_line        = insert(unhandled_line, pre_start, pre)
                lines[line_index]   = lines[line_index][:char_index] + changed_line
                char_index += pre_start + len(pre)
                unhandled_line      = lines[line_index][char_index:]
                is_handled_pre      = True
                brace_stack.append('{')
        
        func_start, func_end = find_func_index(unhandled_line)
        if func_start != NOT_FOUND and not is_contain_post_symbols(unhandled_line[:func_start]):
            char_index += func_end
            line_index, char_index = handle_func(lines, line_index, char_index, pre, post)
            unhandled_line         = lines[line_index][char_index:]
            
        if is_handled_pre:
            while True:
                post_start, first_brace_pos, additional_step = find_post_pos(unhandled_line, brace_stack)
                if post_start != NOT_FOUND:
                    changed_line        = insert(unhandled_line, post_start, post)
                    lines[line_index]   = lines[line_index][:char_index] + changed_line
                    char_index += post_start + len(post) + additional_step
                    unhandled_line      = unhandled_line[first_brace_pos:]
                else:
                    if first_brace_pos != NOT_FOUND:
                        char_index += first_brace_pos

                    break

        if is_handled_pre and not brace_stack:
            return (line_index, char_index if char_index <= len(lines[line_index]) else 0)
        else:
            if find_func_index(unhandled_line)[0] == NOT_FOUND:
                line_index += 1
                char_index = 0
                

def add_hook(content, pre, post):
    '''
    add hook pre, post to a given content. 

    @content, is a tuple contain the code lines of a javascript file, line string marks, line strings values 
    , line regex marks and line regex expressions
    @pre, the hook code of the pre function call
    @post, the hook code of the post function call 
    @return, the hooked codes lines 

    >>> ct = loadjs('test-fixtures/test-fixture.js')
    >>> hooked = add_hook(ct, PRE_HOOK, POST_HOOK)
    >>> open('test-fixtures/test-output.js', 'w').writelines(hooked)
    >>> import filecmp
    >>> filecmp.cmp('test-fixtures/test-answer.js', 'test-fixtures/test-output.js')
    True
    '''
    lines, lines_string_marks, lines_strings, lines_regex_marks, lines_regexes = content
    line_index = 0
    char_index = 0
    for index, line in enumerate(lines):
        if index >= line_index:
            func_start, func_end = find_func_index(line)
            if func_start != NOT_FOUND:
                char_index = func_end
                line_index, char_index = handle_func(lines, index, char_index, pre, post)

            else:
                char_index = 0
                continue
    for index, line in enumerate(lines):
        for rindex, mark in enumerate(lines_regex_marks[index]):
            line = line.replace(mark, lines_regexes[index][rindex])

        for sindex, mark in enumerate(lines_string_marks[index]):
            line = line.replace(mark, lines_strings[index][sindex])
        lines[index] = line 
    return lines

if __name__ == '__main__':
    #error_list = []
    #for f in get_js_list(r'C:\Program Files (x86)\HP\LoadRunner\dat\TCChrome\Extension - Copy', 
    #                     ['en_US.js', 
    #                      '.*jquery.*', 
    #                      '.*galleria.*', 
    #                      '.*knockout.*',
    #                      'moment-with-langs.min.js'], #firefox 
    #                     ['libs', 
    #                      'rotate3Di-1.6', 
    #                      'TPS', 
    #                      'pdf', 
    #                      'JavaScriptEditor']):
    #    ct = loadjs(f)
    #    try:
    #        if ct:
    #            print(f)
    #            hooked = add_hook(ct, "console.log('start');", "console.log('end');")
    #            open(f, 'w').writelines (hooked)
    #    except Exception as e:
    #        error_list.append('%s %s\n' % (f, e))

    #open('error.log', 'w').writelines(error_list)


    f = r'C:\Program Files (x86)\HP\LoadRunner\dat\TCChrome\Extension - Copy\RRE\content\TPS\xpathjs.js'
    ct = loadjs(f)
    hooked = add_hook(ct, "console.log('start');", "console.log('end');")
    if hooked:
        open(f, 'w').writelines(hooked)

    #doctest.testmod()

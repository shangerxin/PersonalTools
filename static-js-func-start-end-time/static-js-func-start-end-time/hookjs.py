import os 
import re
import uuid
import doctest
import argparse

PRE_HOOK                = '''console.log('start');'''
POST_HOOK               = '''console.log('end');'''

NOT_FOUND               = -1
BRACE_TYPE, RETURN_TYPE = 1, len('return')


def _insert(s, i, sub):
    '''
    insert a given substring into the specify index of the string s
    >>> _insert('123', 1, 'x')
    '1x23'
    '''
    return '%s%s%s' % (s[:i], sub, s[i:])

def _is_contain_end_symbols(line):
    '''
    check if the given code line contain the post insert symbol such as '}' and return statement

    @line, code line 
    @return, if contain then return True else False
    '''

    result = re.search('[^a-zA-Z0-9_]*return[^a-zA-Z0-9_]*', line)
    return result

def _is_current_func_ended_before_found_new_func(file_path, func_start, brace_stack, char_index, end, line_index, lines, return_brace_stack, unhandled_line):
    end = _wrap_macro(end, file_path, line_index)
    for index, c in enumerate(unhandled_line[:func_start]):
        if c == '{':
            brace_stack.append('{')
            if return_brace_stack:
                return_brace_stack.append(c)
        elif c == '}':
            brace_stack.pop()
            if return_brace_stack:
                return_brace_stack.pop()
    
            if not brace_stack:
                changed_line        = _insert(unhandled_line, index, end)
                lines[line_index]   = lines[line_index][:char_index] + changed_line
                char_index += index + len(end) + 2
                return char_index, True 
    return char_index, False

def _is_follow_question_mark(lines, line_index, unhandled_line):
    if unhandled_line.find('?') != NOT_FOUND:
        return True
    else:
        for i in xrange(line_index+1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            else:
                if line[0] == '?':
                    return True
                else:
                    return False
        return False

def _is_not_single_line_comment(line):
    '''
    check if the given code line is a single line comment or not

    @line, a code line 
    @return, if it is not a comment line then return True, else return False
    >>> _is_not_single_line_comment('    //TC_NS.Event.dispatch("network/response/retcode", window, { url : details.url , retCode: "404" /*currently hard coded,*/});');
    False
    >>> _is_not_single_line_comment('   //abc')
    False
    >>> _is_not_single_line_comment('   /abe def')
    True
    >>> _is_not_single_line_comment('/* abcd */')
    False
    >>> _is_not_single_line_comment('/**/')
    False
    '''
    is_not = not (re.match('\s*//', line) or re.match('\s*/\*.*\*/', line))
    return is_not

def _is_single_line_return_cross_multi_lines(begin_end_pos, is_handled_start, is_not_empty_return_stack, is_require_handle_return, is_return_ternary_operator, line_index, lines, return_line, return_symbol_index, unhandled_line):
    return begin_end_pos == NOT_FOUND                                   and \
           return_line                                                  and \
           return_symbol_index < line_index                             and \
           is_handled_start                                             and \
           is_not_empty_return_stack == False                           and \
           is_return_ternary_operator == False                          and \
           is_require_handle_return                                     and \
           line_index > 0                                               and \
           not re.search('[,&\|\^%\[\+\-\*/\.\(=]\s*$', return_line)    and \
           not re.match('^\s*[,&\|\^%\[\+\-\*/\.=]', lines[line_index]) and \
           unhandled_line.strip()

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

def _find_start_pos(line):
    '''
    find the pre insert position, which is the always behind the first character '{'

    >>> _find_start_pos('(){')
    3
    '''
    brace_index = line.find('{')
    if brace_index != NOT_FOUND:
        return brace_index + 1
    else:
        return NOT_FOUND

def _find_end_pos(line, brace_stack, return_brace_stack):
    '''
    find the post insert position, it will return the position in front of each return statements and
    before the last brace

    @line, the code line
    @brace_stack, the brace stack contain all the current function's '{', whenever the code line contain a 
    '{'. The '{' will be insert into the brace_stack, if encounter a '}' then will pop out a '{' from the stack
    @return, a tuple contain the post insert position, the first encountered '}' position and the additional move
    characters which will be used to indicate current filtered character from the code line

    >>> _find_end_pos('#start #end}', ['{'], [])
    (11, 12, 1)
    >>> _find_end_pos('return;}', ['{'], [])
    (0, 6, 6)
    >>> _find_end_pos(';return;', ['}'], [])
    (1, 7, 6)
    >>> _find_end_pos('return', ['}'], [])
    (0, 6, 6)
    >>> _find_end_pos('returnAbc = 0;}', ['}'], [])
    (14, 15, 1)
    >>> _find_end_pos('Abcreturn = 0;}', ['}'], [])
    (14, 15, 1)
    >>> _find_end_pos('areturnb = 0;}', ['}'], [])
    (13, 14, 1)
    '''
    if not brace_stack:
        return (NOT_FOUND, 0, 0)

    first_brace_pos = NOT_FOUND
    for index, c in enumerate(line):
        next_index = index + 1
        if c == '{':
            brace_stack.append(c)
            if return_brace_stack:
                return_brace_stack.append(c)
        elif c == '}':
            if return_brace_stack:
                return_brace_stack.pop()
            if brace_stack:
                brace_stack.pop()
            first_brace_pos = index + 1 if first_brace_pos == NOT_FOUND else first_brace_pos
            if not brace_stack:
                return (index, next_index, BRACE_TYPE)

        filtered, rest = line[:next_index], line[next_index:]
        m = re.search('([^a-zA-Z0-9_]+|^)return([^a-zA-Z0-9_]|\Z)', filtered)
        if m and ((not rest) or (rest and (not re.search('[a-zA-Z0-9_]', rest[0])))):
            finded = m.group()
            return (filtered.find('return'), len(filtered), RETURN_TYPE)

        if _find_func_index(filtered)[0] != NOT_FOUND:
            break
     
    return (NOT_FOUND, first_brace_pos, 0)

def _find_func_index(line):
    '''
    check if there is a function definition contain in the given code line

    @line, a code line 
    @return, a tuple contain the function definition start index and function definition end index

    >>> _find_func_index('function foo (){')
    (0, 13)
    >>> _find_func_index('abc; function (){')
    (5, 14)
    >>> _find_func_index('get prop (){')
    (0, 9)
    >>> _find_func_index('set prop(v){')
    (0, 8)
    '''
    m  = re.search('[^a-zA-Z0-9_\s]*function[\s\(]*[a-zA-Z0-9_]*\s*(?=\()', line)
    pm = re.search(r'(?<![a-zA-Z0-9])(get|set)\s+[a-zA-Z0-9_]+\s*(?=\()', line)
    if m:
        finded = m.group()
        return (line.index(finded), line.index(finded) + len(finded))
    elif pm:
        finded = pm.group()
        return (line.index(finded), line.index(finded) + len(finded))
    else:
        return (NOT_FOUND, NOT_FOUND)

def _handle_func(file_path, lines, line_index, char_index, start, end):
    '''
    handle a function scope from a given start line index till find the end of the function. During the handling 
    may encounter another function definition. Then the function handle_func will be call recursively by itself

    @file, is the current file path
    @lines, the code lines of a JavaScript file
    @line_index, the current handling line index of the JavaScript file 
    @char_index, the current handling char index of the current handling line 
    @start, the hook code of the start function call 
    @end, the hook code of the end function call
    @return, a tuple contain the current finished handling line index and char index
    '''
    try:
        len_lines                  = len(lines)
        return_symbol_index        = len_lines
        brace_stack                = []
        is_handled_start           = False
        return_brace_stack         = []
        is_return_ternary_operator = False
        is_not_empty_return_stack  = False
        is_require_handle_return   = False
        begin_end_pos              = False
        return_line                = ''
        func_start                 = NOT_FOUND
        func_end                   = NOT_FOUND
        while True:
            unhandled_line = lines[line_index][char_index:]
            if not is_handled_start:
                begin_start_pos  = _find_start_pos(unhandled_line)
                if begin_start_pos != NOT_FOUND:
                    char_index, is_handled_start, unhandled_line = _handle_func_start(begin_start_pos, 
                                                                                      brace_stack, 
                                                                                      char_index,
                                                                                      file_path, 
                                                                                      line_index, 
                                                                                      lines, 
                                                                                      start, 
                                                                                      unhandled_line)
        
            func_start, func_end = _find_func_index(unhandled_line)
            if func_start != NOT_FOUND and not _is_contain_end_symbols(unhandled_line[:func_start]):
                char_index, is_cur_func_end = _is_current_func_ended_before_found_new_func(file_path,
                                                                                           func_start, 
                                                                                           brace_stack, 
                                                                                           char_index, 
                                                                                           end, 
                                                                                           line_index, lines, 
                                                                                           return_brace_stack, 
                                                                                           unhandled_line)
                if is_cur_func_end:
                    return (line_index, char_index if char_index <= len(lines[line_index]) else 0)

                char_index += func_end
                line_index, char_index = _handle_func(file_path, lines, line_index, char_index, start, end)
                unhandled_line         = lines[line_index][char_index:]
            
            if is_handled_start:
                while True:
                    is_not_empty_return_stack                            = not not return_brace_stack
                    begin_end_pos, first_brace_pos, additional_step_type = _find_end_pos(unhandled_line, brace_stack, return_brace_stack)
                    return_line, return_symbol_index                     = _update_cur_return_line(len_lines, 
                                                                                                   line_index, 
                                                                                                   lines, 
                                                                                                   return_symbol_index, 
                                                                                                   additional_step_type, 
                                                                                                   return_line)

                    if begin_end_pos != NOT_FOUND and is_require_handle_return:
                        begin_end_pos, char_index, is_require_handle_return, unhandled_line = _handle_pre_return_before_new_found_return_statement(begin_end_pos, 
                                                                                                                                                   char_index, 
                                                                                                                                                   line_index, 
                                                                                                                                                   lines, 
                                                                                                                                                   return_brace_stack, 
                                                                                                                                                   unhandled_line)

                    elif _is_single_line_return_cross_multi_lines(begin_end_pos, 
                                                                  is_handled_start, 
                                                                  is_not_empty_return_stack, 
                                                                  is_require_handle_return, 
                                                                  is_return_ternary_operator, 
                                                                  line_index, 
                                                                  lines, 
                                                                  return_line, 
                                                                  return_symbol_index, 
                                                                  unhandled_line):
                            lines[line_index]        = _insert(lines[line_index], 0, '}')
                            is_require_handle_return = False
                            char_index += 1

                    if begin_end_pos != NOT_FOUND:
                        if additional_step_type == RETURN_TYPE:
                            t_end = _wrap_macro(end, file_path, line_index)
                            is_return_ternary_operator = False
                            changed_line               = _insert(unhandled_line, begin_end_pos, '{' + t_end)
                            lines[line_index]          = lines[line_index][:char_index] + changed_line
                            char_index += begin_end_pos + len(t_end) + additional_step_type + 1
                            unhandled_line             = unhandled_line[first_brace_pos:]
                            is_handled                 = False
                            is_require_handle_return   = True
                            index = 0
                            index, char_index, index, is_handled, unhandled_line, is_return_ternary_operator, is_require_handle_return, func_start, func_end, changed_line, line_index = _handle_return_statement(file_path, 
                                                                                                                                                                                                                  index, 
                                                                                                                                                                                                                  brace_stack,
                                                                                                                                                                                                                  char_index, 
                                                                                                                                                                                                                  end,
                                                                                                                                                                                                                  is_handled, 
                                                                                                                                                                                                                  line_index, 
                                                                                                                                                                                                                  lines, 
                                                                                                                                                                                                                  return_brace_stack, 
                                                                                                                                                                                                                  start, 
                                                                                                                                                                                                                  unhandled_line, 
                                                                                                                                                                                                                  is_return_ternary_operator, 
                                                                                                                                                                                                                  is_require_handle_return, 
                                                                                                                                                                                                                  func_start, 
                                                                                                                                                                                                                  func_end, 
                                                                                                                                                                                                                  changed_line)

                            if not return_brace_stack and not is_handled:
                                if not _is_follow_question_mark(lines, line_index, unhandled_line):
                                    char_index += index + 1
                                    unhandled_line = unhandled_line[index+1:] 
                                else:
                                    is_return_ternary_operator = True
                            else:
                                break
                        else:
                            t_end = _wrap_macro(end, file_path, line_index)
                            changed_line        = _insert(unhandled_line, begin_end_pos, t_end)
                            lines[line_index]   = lines[line_index][:char_index] + changed_line
                            char_index += begin_end_pos + len(t_end) + additional_step_type
                            unhandled_line      = unhandled_line[first_brace_pos:]
                    elif return_brace_stack:
                        char_index, index, is_handled, unhandled_line, is_require_handle_return = _handle_return_object_cross_multiple_lines(brace_stack, 
                                                                                                                                             char_index, 
                                                                                                                                             end, 
                                                                                                                                             file_path,
                                                                                                                                             is_handled, 
                                                                                                                                             line_index, 
                                                                                                                                             lines, 
                                                                                                                                             return_brace_stack, 
                                                                                                                                             start, 
                                                                                                                                             unhandled_line, 
                                                                                                                                             is_require_handle_return, 
                                                                                                                                             first_brace_pos)

                        if not return_brace_stack and not is_handled:
                            char_index += index + 1
                            unhandled_line = unhandled_line[index+1:]
                        else:
                            break
                    elif is_return_ternary_operator and unhandled_line:
                        char_index, is_handled, unhandled_line, is_require_handle_return = _handle_return_with_ternary_operator(brace_stack, 
                                                                                                                                char_index, 
                                                                                                                                end, 
                                                                                                                                file_path,
                                                                                                                                is_handled, 
                                                                                                                                line_index, 
                                                                                                                                lines, 
                                                                                                                                return_brace_stack, 
                                                                                                                                unhandled_line, 
                                                                                                                                is_require_handle_return, 
                                                                                                                                first_brace_pos)

                    elif not return_brace_stack and is_not_empty_return_stack:
                        char_index, unhandled_line, is_require_handle_return = _handle_single_line_return(char_index, 
                                                                                                          line_index, 
                                                                                                          lines, 
                                                                                                          unhandled_line, 
                                                                                                          is_require_handle_return)
                    elif is_require_handle_return and unhandled_line:
                        char_index, is_handled, unhandled_line, is_return_ternary_operator, is_require_handle_return = _handle_return_cross_multi_lines_end(brace_stack, 
                                                                                                                                                            char_index, 
                                                                                                                                                            end, 
                                                                                                                                                            file_path,
                                                                                                                                                            is_handled, 
                                                                                                                                                            line_index, 
                                                                                                                                                            lines, 
                                                                                                                                                            return_brace_stack, 
                                                                                                                                                            unhandled_line,
                                                                                                                                                            is_return_ternary_operator, 
                                                                                                                                                            is_require_handle_return,
                                                                                                                                                            first_brace_pos)
                    else:
                        if first_brace_pos != NOT_FOUND:
                            char_index += first_brace_pos

                        break

            if is_handled_start and not brace_stack:
                return (line_index, char_index if char_index <= len(lines[line_index]) else 0)
            else:
                if _find_func_index(unhandled_line)[0] == NOT_FOUND:
                    line_index += 1
                    char_index = 0

    except Exception as e:
        e.line_index = line_index or -1
        raise e

def _handle_func_start(begin_start_pos, brace_stack, char_index, file_path, line_index, lines, start, unhandled_line):
    start = _wrap_macro(start, file_path, line_index)
    changed_line        = _insert(unhandled_line, begin_start_pos, start)
    lines[line_index]   = lines[line_index][:char_index] + changed_line
    char_index += begin_start_pos + len(start)
    unhandled_line      = lines[line_index][char_index:]
    is_handled_start    = True
    brace_stack.append('{')
    return char_index, is_handled_start, unhandled_line

def _handle_pre_return_before_new_found_return_statement(begin_end_pos, char_index, line_index, lines, return_brace_stack, unhandled_line):
    avaliable_insert_pos      = 0
    first_none_whitespace_pos = 0
    for index in xrange(begin_end_pos-1, -1, -1):
        c = unhandled_line[index]
        if first_none_whitespace_pos == 0 and c not in ' \t\n':
            first_none_whitespace_pos = index
        if c == ';':
            if not return_brace_stack:
                avaliable_insert_pos = index + 1
                break 
        elif c == '}':
            avaliable_insert_pos = index + 1
            break
    lines[line_index] = _insert(lines[line_index], avaliable_insert_pos, '}')
    char_index += avaliable_insert_pos + 1
    begin_end_pos -= avaliable_insert_pos
    unhandled_line = lines[line_index][char_index:] if avaliable_insert_pos != 0 else unhandled_line
    is_require_handle_return = False
    return begin_end_pos, char_index, is_require_handle_return, unhandled_line

def _handle_return_with_ternary_operator(brace_stack, char_index, end, file_path, is_handled, line_index, lines, return_brace_stack, unhandled_line, is_require_handle_return, first_brace_pos):
    end = _wrap_macro(end, file_path, line_index)
    index = 0
    while True:
        if index < len(unhandled_line):
            c = unhandled_line[index]
            if c == '{':
                brace_stack.append('{')
                return_brace_stack.append(c)
            elif c == '}':
                brace_stack.pop()
                if return_brace_stack:
                    return_brace_stack.pop()
                else:
                    if first_brace_pos != NOT_FOUND:
                        brace_stack.append('{')
                    if not is_handled:
                        changed_line               = _insert(unhandled_line, index, '}')
                        lines[line_index]          = lines[line_index][:char_index] + changed_line
                        char_index += index + 1
                        unhandled_line             = unhandled_line[index+1:] if brace_stack else unhandled_line[index:]
                        index                      = -1 if brace_stack else 0
                        is_return_ternary_operator = False
                        is_handled                 = True 
                        is_require_handle_return   = False
                    
                    if not brace_stack:
                        changed_line        = _insert(unhandled_line, index, end)
                        lines[line_index]   = lines[line_index][:char_index] + changed_line
                        char_index += index + len(end) + 2
                        unhandled_line      = unhandled_line[index+1:]
                        index = -1
                        break
    
            elif c == ';' and not is_handled:
                changed_line               = _insert(unhandled_line, index+1, '}')
                lines[line_index]          = lines[line_index][:char_index] + changed_line
                char_index += index + 2
                unhandled_line             = unhandled_line[index+1:]
                index                      = -1
                is_return_ternary_operator = False
                is_handled                 = True 
                is_require_handle_return   = False
    
            index +=1
        else:
            unhandled_line = unhandled_line[index:]
            break
    return char_index, is_handled, unhandled_line, is_require_handle_return

def _handle_return_object_cross_multiple_lines(brace_stack, char_index, end, file_path, is_handled, line_index, lines, return_brace_stack, start, unhandled_line, is_require_handle_return, first_brace_pos):
    end = _wrap_macro(end, file_path, line_index)
    index = 0
    while True:
        if index < len(unhandled_line):
            c = unhandled_line[index]
            if c == '{':
                brace_stack.append('{')
                return_brace_stack.append(c)
            elif c == '}':
                brace_stack.pop()
                if return_brace_stack:
                    return_brace_stack.pop()
                else:
                    if first_brace_pos != NOT_FOUND:
                        brace_stack.append('{')
                    if not is_handled:
                        changed_line               = _insert(unhandled_line, index, '}')
                        lines[line_index]          = lines[line_index][:char_index] + changed_line
                        char_index += index + 1
                        unhandled_line             = unhandled_line[index+1:] if brace_stack else unhandled_line[index:]
                        index                      = -1 if brace_stack else 0
                        is_return_ternary_operator = False
                        is_handled                 = True 
                        is_require_handle_return   = False
                    
                    if not brace_stack:
                        changed_line        = _insert(unhandled_line, index, end)
                        lines[line_index]   = lines[line_index][:char_index] + changed_line
                        char_index += index + len(end) + 2
                        unhandled_line      = unhandled_line[index+1:]
                        index = -1
                        break
    
            elif c == ';' and not is_handled:
                changed_line               = _insert(unhandled_line, index+1, '}')
                lines[line_index]          = lines[line_index][:char_index] + changed_line
                char_index += index + 2
                unhandled_line             = unhandled_line[index+1:]
                index                      = -1
                is_return_ternary_operator = False
                is_handled                 = True 
                is_require_handle_return   = False
            else:
                filtered                   = unhandled_line[:index+1]
                func_start, func_end       = _find_func_index(filtered)
                if func_start != NOT_FOUND:
                    char_index += func_end
                    line_index, char_index = _handle_func(file_path, lines, line_index, char_index, start, end)
                    unhandled_line         = lines[line_index][char_index:]
                    index                  = -1
                    
            index+=1
        else:
            break
    return char_index, index, is_handled, unhandled_line, is_require_handle_return

def _handle_single_line_return(char_index, line_index, lines, unhandled_line, is_require_handle_return):
    brace_pos                = unhandled_line.find('}')
    semicolon_pos            = unhandled_line.find(';')
    changed_line             = _insert(unhandled_line, brace_pos if semicolon_pos < brace_pos else semicolon_pos + 1, '}')
    lines[line_index]        = lines[line_index][:char_index] + changed_line
    char_index += brace_pos+1
    unhandled_line           = unhandled_line[brace_pos+1:]
    is_handled               = True 
    is_require_handle_return = False
    return char_index, unhandled_line, is_require_handle_return

def _handle_return_cross_multi_lines_end(brace_stack, char_index, end, file_path, is_handled, line_index, lines, return_brace_stack, unhandled_line, is_return_ternary_operator, is_require_handle_return, first_brace_pos):
    end = _wrap_macro(end, file_path, line_index)
    index = 0
    while True:
        if index < len(unhandled_line):
            c = unhandled_line[index]
            if c == '{':
                brace_stack.append('{')
                return_brace_stack.append(c)
            elif c == '}':
                brace_stack.pop()
                if return_brace_stack:
                    return_brace_stack.pop()
                else:
                    if first_brace_pos != NOT_FOUND:
                        brace_stack.append('{')
                    if not is_handled:
                        changed_line               = _insert(unhandled_line, index, '}')
                        lines[line_index]          = lines[line_index][:char_index] + changed_line
                        char_index += index + 1
                        unhandled_line             = unhandled_line[index+1:] if brace_stack else unhandled_line[index:]
                        index                      = -1 if brace_stack else 0
                        is_return_ternary_operator = False
                        is_handled                 = True 
                        is_require_handle_return   = False
                    
                    if not brace_stack:
                        changed_line        = _insert(unhandled_line, index, end)
                        lines[line_index]   = lines[line_index][:char_index] + changed_line
                        char_index += index + len(end) + 2
                        unhandled_line      = unhandled_line[index+1:]
                        index = -1
                        break
    
            elif c == ';' and not is_handled:
                changed_line               = _insert(unhandled_line, index+1, '}')
                lines[line_index]          = lines[line_index][:char_index] + changed_line
                char_index += index + 2
                unhandled_line             = unhandled_line[index+1:]
                index                      = -1
                is_return_ternary_operator = False
                is_handled                 = True 
                is_require_handle_return   = False
    
            index +=1
        else:
            unhandled_line = unhandled_line[index:]
            break
    return char_index, is_handled, unhandled_line, is_return_ternary_operator, is_require_handle_return

def _handle_return_statement(file_path, index, brace_stack, char_index, end, is_handled, line_index, lines, return_brace_stack, start, unhandled_line, is_return_ternary_operator, is_require_handle_return, func_start, func_end, changed_line):
    end = _wrap_macro(end, file_path, line_index)
    while True:
        if index < len(unhandled_line):
            c = unhandled_line[index]
            if c == '{':
                brace_stack.append('{')
                return_brace_stack.append(c)
            elif c == '}':
                brace_stack.pop()
                if return_brace_stack:
                    return_brace_stack.pop()
                else:
                    pre_index = index 
                    if not is_handled:
                        changed_line               = _insert(unhandled_line, index, '}')
                        lines[line_index]          = lines[line_index][:char_index] + changed_line
                        char_index += index + 1
                        unhandled_line             = unhandled_line[index:]
                        index                      = -1
                        is_return_ternary_operator = False
                        is_handled                 = True 
                        is_require_handle_return   = False
                    
                    if not brace_stack:
                        if pre_index < len(unhandled_line):
                            changed_line        = _insert(unhandled_line, pre_index, end)
                            lines[line_index]   = lines[line_index][:char_index] + changed_line
                            char_index += len(end) + 1 + pre_index
                            unhandled_line      = unhandled_line[pre_index+1:]
                        else:
                            changed_line        = _insert(unhandled_line, 0, end)
                            lines[line_index]   = lines[line_index][:char_index] + changed_line
                            char_index += len(end) + 1
                            unhandled_line      = unhandled_line[1:]
                        break
                    else:
                        unhandled_line = unhandled_line[1:] if unhandled_line else unhandled_line
    
            elif c == ';' and not is_handled:
                changed_line               = _insert(unhandled_line, index+1, '}')
                lines[line_index]          = lines[line_index][:char_index] + changed_line
                char_index += index + 2
                unhandled_line             = unhandled_line[index+1:]
                index                      = -1
                is_return_ternary_operator = False
                is_handled                 = True 
                is_require_handle_return   = False
                
            else:
                filtered = unhandled_line[:index+1]
                func_start, func_end = _find_func_index(filtered)
                if func_start != NOT_FOUND:
                    char_index += func_end
                    line_index, char_index = _handle_func(file_path, lines, line_index, char_index, start, end)
                    unhandled_line         = lines[line_index][char_index:]
                    index                  = -1
                    
            index+=1
        else:
            break
    return index, char_index, index, is_handled, unhandled_line, is_return_ternary_operator, is_require_handle_return, func_start, func_end, changed_line, line_index

def _parse_cmdline(arg_list=None):
    '''
    Parse the command parameters 

    @arg_list, the arguments list which is used for test purpose 
    @return, an arguments object which property contain the defined parameters 

    >>> args = _parse_cmdline("-s console.log('start'); -e console.log('end'); -p c:/dummy -f a b c d -d e f g".split()).args
    >>> args.start
    "console.log('start');"
    >>> args.end
    "console.log('end');"
    >>> args.black_files
    ['a', 'b', 'c', 'd']
    >>> args.black_dirs
    ['e', 'f', 'g']
    >>> args.path
    'c:/dummy'
    '''
    ps =argparse.ArgumentParser(description='A command line JavaScript hook tool for inject start, end codes into every JavaScript functions.' +
                               ' Currently only support uncompressed EMCScipt 5. Any errors will be output into the error.log file.' + 
                               ' Support macro __FILE__ and __LINE__ in the start, end code snippet', 
                                epilog='Created by Edwin, Shang(Shang, Erxin), License under GNU LGPLv3. Version 1.7.0')
    ps.add_argument('-p', '--path', help='The path to the JavaScript file or directory')
    ps.add_argument('-s', '--start', default='', help='The start code snippet which will be injected at the begin of each function, it also could be a js file')
    ps.add_argument('-e', '--end', default='', help='The end code snippet which will be injected at the end of each function,  it also could be a js file')
    ps.add_argument('-f', '--black-files', default=[], nargs='*', help='Use regex expression to define the black files list, the files will not be hooked')
    ps.add_argument('-d', '--black-dirs', default=[], nargs='*', help='Use regex expression to define the black dirs list, the directory and sub directory will not be searched')
    #ps.add_argument('-t', '--run-test', default=False, help='Run all the document test', action='store_true')
    ps.args = ps.parse_args(arg_list)
    return ps

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
        m = re.search(r'''(?<!\\)(?P<quote>['"]).*?(?<!\\)(?P=quote)''', line)
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
        m = re.search(r'(?<!\\|\/)[/](?!\*|\/).+?(?<!\\)[/]', line)
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
        codes = m.group(1)
        for i in xrange(len(codes)-1, -1, -1):
            c = codes[i]
            if c == '/':
                continue 
            else:
                i += 1
                break
        line = codes[:i] + '\n'
    return line

def _update_cur_return_line(len_lines, line_index, lines, return_symbol_index, additional_step_type, return_line):
    if additional_step_type == RETURN_TYPE:
        return_symbol_index = line_index
        return_line = lines[return_symbol_index]
    elif return_symbol_index != len_lines:
        return_symbol_index == len_lines
    return return_line, return_symbol_index

def _wrap_code(code):
    return ';%s;' % code 

def _wrap_macro(code, file_path, line_index):
    '''
    will replace the macro define in the start, end code snippet 
    '''
    return code.replace('__FILE__', file_path.replace('\\', '\\\\')).replace('__LINE__', str(line_index+1))

def _load_code_snippet(data):
    '''
    load code snippet from a given js file

    >>> _load_code_snippet('test-fixtures/test-load-code-snippet.js')
    'var a = 3; if (def){ gh; } else {}'
    '''
    if os.path.isfile(data):

        content = open(data, 'r').read()
        while True:
            ret = re.sub('[\s\n]+', ' ', content)
            if ret == content:
                return ret
            else:
                content = ret
    else:
        return data
        

def add_hook(content, file_path, start, end):
    '''
    add hook start, end to a given content. 

    @content, is a tuple contain the code lines of a javascript file, line string marks, line strings values 
    , line regex marks and line regex expressions
    @file_path, current file path of the script
    @start, the hook code of the start function call
    @end, the hook code of the end function call 
    @return, the hooked codes lines 

    >>> ct = loadjs('test-fixtures/test-fixture.js')
    >>> hooked = add_hook(ct, '', PRE_HOOK, POST_HOOK)
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
            func_start, func_end = _find_func_index(line)
            if func_start != NOT_FOUND:
                char_index = func_end
                line_index, char_index = _handle_func(file_path, lines, index, char_index, start, end)

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

                if line and _is_not_single_line_comment(line):
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
    else:
        print('Invalid path parameter');

if __name__ == '__main__':
    ps = _parse_cmdline()
    args = ps.args
    if 'run_test' in args and args.run_test:
        doctest.testmod()
    elif args.path:
        error_list = []
        for f in get_js_list(args.path, args.black_files, args.black_dirs):
            ct = loadjs(f)
            try:
                print(f)
                hooked = add_hook(ct, 
                                  f, 
                                  _wrap_code(_load_code_snippet(args.start)),
                                  _wrap_code(_load_code_snippet(args.end)))
                open(f, 'w').writelines(hooked)
            except Exception as e:
                error_list.append('%s, error info: %s, line:%s\n' % (f, e, e.line_index))
        if error_list:
            open('error.log', 'w').writelines(error_list)

    else:
        ps.print_help()
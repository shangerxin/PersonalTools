MARK_START = '#start'
MARK_END = '#end'
TEST_FIXTURE_PATH = 'test-fixtures/test-fixture.js'
TEST_ANSWER_PATH = 'test-fixtures/test-answer.js'

import hookjs

def to_answer(test_fixture_path, pre, post):
    lines, lines_string_marks, lines_strings, lines_regex_marks, lines_regexes = hookjs.loadjs(test_fixture_path)
    for i, line in enumerate(lines):
        if line.find('return') != -1:
            lines[i] = line.replace(MARK_START, pre+MARK_START).replace(MARK_END + ' return', '%s %sreturn'%(MARK_END, post))
        else:
            lines[i] = line.replace(MARK_START, pre+MARK_START).replace(MARK_END, MARK_END+post)

    for index, line in enumerate(lines):
        for rindex, mark in enumerate(lines_regex_marks[index]):
            line = line.replace(mark, lines_regexes[index][rindex])

        for sindex, mark in enumerate(lines_string_marks[index]):
            line = line.replace(mark, lines_strings[index][sindex])
        lines[index] = line 

    hf = open(TEST_ANSWER_PATH, 'w')
    hf.writelines(lines)
    hf.close()

if __name__ == '__main__':
    to_answer(TEST_FIXTURE_PATH, "console.log('start');", "console.log('end');")
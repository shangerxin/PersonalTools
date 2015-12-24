MARK_START = '#start'
MARK_END = '#end'
TEST_FIXTURE_PATH = 'test-fixtures/test-fixture.js'
TEST_ANSWER_PATH = 'test-fixtures/test-answer.js'

import hookjs

def to_answer(test_fixture_path, pre, post):
    ct = hookjs.loadjs(test_fixture_path)
    for i, line in enumerate(ct):
        if line.find('return') != -1:
            ct[i] = line.replace(MARK_START, pre+MARK_START).replace(MARK_END + ' return', '%s %sreturn'%(MARK_END, post))
        else:
            ct[i] = line.replace(MARK_START, pre+MARK_START).replace(MARK_END, MARK_END+post)

    hf = open(TEST_ANSWER_PATH, 'w')
    hf.writelines(ct)
    hf.close()

if __name__ == '__main__':
    to_answer(TEST_FIXTURE_PATH, "console.log('start');", "console.log('end');")
import os
import sys
import hashlib

truclientbrowser_root = r'E:\Shared\Firefox58-truclientbrowser-release'

def is_same_file(path0, path1):
	if os.path.isfile(path0) and os.path.isfile(path1):
		s0 = os.stat(path0)
		s1 = os.stat(path1)
		if s0.st_size == s1.st_size:
			m0 = hashlib.md5()
			m1 = hashlib.md5()
			m0.update(open(path0, 'rb').read())
			md5_0 = m0.digest()
			m1.update(open(path1, 'rb').read())
			md5_1 = m1.digest()
			return md5_0 == md5_1
	return False

def total_file_size(root, files):
	'''
	size is in mb
	'''
	size = 0
	for f in files:
		f = os.path.join(root, f)
		if os.path.isfile(f):
			size += os.stat(f).st_size
	return size / (1024 * 1024)

def get_all_files(path):
	all_files = []
	for root, dirs, files in os.walk(path):
		for f in files:
			file_path = os.path.join(root, f)
			all_files.append(file_path)
	return all_files

def convert2file2copy_lines(root, file_pathes):
	lines = []
	for file_path in file_pathes:
		relative_path = file_path.replace(root, '')
		relative_path = relative_path if relative_path[0] == '\\' else '\\' + relative_path
		lines.append('<FileRelativePathTARGETDIR Include="bin\\TruClientBrowser%s" />\n' % relative_path)
	return lines

def filter_difference(tcb_path0, tcb_path1):
	'''
	if only specify one path then list all the files
	if specify two pathes then filter out the different files between the two
	folders base on the first path
	'''
	files0 = [f[1:] if f[0] == '\\' else f for f in [f.replace(tcb_path0, '') for f in get_all_files(tcb_path0)]]
	files1 = [f[1:] if f[0] == '\\' else f for f in [f.replace(tcb_path1, '') for f in get_all_files(tcb_path1)]]

	same_files, diff_files = [], []
	files1 = set(files1)
	while files0:
		f = files0.pop()
		if f in files1:
			file0 = os.path.join(tcb_path0, f)
			file1 = os.path.join(tcb_path1, f)
			if is_same_file(file0, file1):
				same_files.append(f)
			else:
				diff_files.append(f)
	return same_files, diff_files

def save_tcb2file2copy(path):
	files = get_all_files(path)
	lines = convert2file2copy_lines(path, files)
	open('f:/files2copy.txt', 'w').writelines(lines)

if __name__ == '__main__':
	arg_length = len(sys.argv)
	if arg_length == 1:
		save_tcb2file2copy(truclientbrowser_root)
	elif arg_length == 3:
		path0, path1 = sys.argv[1], sys.argv[2]
		same_files, diff_files = filter_difference(path0, path1)
		lines = convert2file2copy_lines(path0, diff_files)
		lines.append('total file size %.2fMB' % total_file_size(path0, diff_files))
		open('f:/diff_files2copy.txt', 'w').writelines(lines)
		lines = convert2file2copy_lines(path0, same_files)
		lines.append('total file size %.2fMB' % total_file_size(path0, same_files))
		open('f:/same_files2copy.txt', 'w').writelines(lines)
	else:
		print('Incorrect argument numbers, recieve no or 2 path arguments to TruClientBrowser root')
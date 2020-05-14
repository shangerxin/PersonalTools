import re
import os
import sys
import xlwt
import argparse
from pprint import pprint as pp
from datetime import datetime

import textract

interested_field_bars = [
	('3. (Required) Disclosure Classification', '4. Project and Product Name(s)', 'Team'),
	('4. Project and Product Name(s)', '5. (Required) Invention Title', 'Product'),
	('5. (Required) Invention Title', '6. (Required) Short Title', 'Title'),
	(re.compile('[^\s]+@microfocus.com'), None, 'Inventors')
]

fields_title = ['Record Number',
				'Team',
				'Product',
				'Title',
				'Inventors']

def abstract_text(file_path):
	if os.path.isfile(file_path) and file_path.lower().endswith('pdf'):
		btext = textract.process(file_path)
		utext = btext.decode('utf-8', 'ignore')
		return utext

def get_fields(interested_field_bars, is_required_file_path, pdf):
	if os.path.isfile(pdf) and pdf.lower().endswith('pdf'):
		utext = abstract_text(pdf)
		fields = dict.fromkeys(fields_title, '')
		fields['Record Number'] = os.path.split(pdf)[1].split()[0]

		if is_required_file_path:
			fields['File'] = pdf

		for bar in interested_field_bars:
			begin, end, key = bar
			ibegin = utext.find(begin) + len(begin) if isinstance(begin, str) \
				else (-1 if not begin.search(utext) else utext.find(begin.search(utext).group(0)))
			iend = utext.find(end) if end else len(utext) - 1

			field = ' '.join(utext[ibegin:iend].split())
			#field remove team sub index number
			field = re.sub('[\d\.]+ -', '', field)

			#Remove inventor phone and inventor trail
			field = re.sub('\+ \d\d [\d ]+', '', field)
			fields[key] = field.replace('Inventor', '').strip()

		return fields

def get_all_pdfs(root_dir):
	pdf_files = []
	if os.path.isdir(root_dir):
		for root, dirs, files in os.walk(root_dir):
			for f in files:
				if f.lower().endswith('pdf'):
					pdf_files.append(os.path.join(root, f))
	elif os.path.isfile(root_dir) and root_dir.lower().endswith('pdf'):
		pdf_files.append(root_dir)
	return pdf_files

def parse_commandlines(args):
	p = argparse.ArgumentParser(description='Helper tool to retreive inventor information from disclosures')
	p.add_argument('pdf_root_dir', help='The root directory contains the disclosure PDFs', default=None)
	p.add_argument('-f', '--file', help='Output with the file path', action='store_true')
	p.add_argument('-e', '--excel', help='Output with an excel')

	if len(args) == 0:
		p.print_help()

	return p.parse_args(args)

def output_to_excel(inventor_info, excel_path):
	wb = xlwt.Workbook()
	dt = datetime.now()
	ws = wb.add_sheet('Disclosures %s' % dt.strftime("%d. %B %Y"))
	excel_path = excel_path.strip() + '.xls'
	#write title
	for c, title in enumerate(fields_title):
		ws.write(0, c, title)

	for r, info in enumerate(inventor_info):
		for c, title in enumerate(fields_title):
			value = int(info[title]) if info[title].isdigit() else info[title]
			ws.write(r+1, c, value)

	wb.save(excel_path)

if __name__ == '__main__':
	args = parse_commandlines(sys.argv[1:])
	if args.pdf_root_dir:
		pdfs = get_all_pdfs(args.pdf_root_dir)
		inventor_info = [get_fields(interested_field_bars, args.file, pdf) for pdf in pdfs]

		if inventor_info:
			inventor_info = sorted(inventor_info, key=lambda info:info['Team'])
			if args.excel:
				output_to_excel(inventor_info, args.excel)
			else:
				pp(inventor_info)
import re
import os
import sys
import xlwt
import argparse
from pprint import pprint as pp
from datetime import datetime

import textract

interested_field_bars = [
    ('3. (Required) Disclosure Classification',
     '4. Project and Product Name(s)', 'Team'),
    ('4. Project and Product Name(s)', '5. (Required) Invention Title', 'Product'),
    ('5. (Required) Invention Title', '6. (Required) Short Title', 'Title'),
    (re.compile('[^\s]+@microfocus.com'), None, 'Inventors')
]

fields_title = ['Record Number',
                'Team',
                'Product',
                'Title',
                'Inventors']

MAX_CELL_LEGAL_LENGTH = 32767
MF_EMAIL_EXTENSION = '@microfocus.com'


def abstract_text(file_path):
    if os.path.isfile(file_path) and file_path.lower().endswith('pdf'):
        try:
            btext = textract.process(file_path)
            utext = btext.decode('utf-8', 'ignore')
            return utext
        except Exception as e:
            print('Abstract text from pdf ', file_path, ' failed with error', e)
            return


def get_fields(interested_field_bars, is_required_file_path, pdf):
    if os.path.isfile(pdf) and pdf.lower().endswith('pdf'):
        utext = abstract_text(pdf)
        if not utext:
            return
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
            #      field remove team sub index number
            field = re.sub('[\d\.]+ -', '', field)

            #      Remove inventor phone and inventor trail
            field = re.sub('\+ \d\d [\d ]+', '', field)
            if key == 'Inventors':
                emails_prefix_info = field.split(MF_EMAIL_EXTENSION)[:-1]
                for i, prefix in enumerate(emails_prefix_info):
                    address_start_index = prefix.rfind(' ')
                    if address_start_index != -1:  # not found
                        emails_prefix_info[i] = emails_prefix_info[i][address_start_index:] + \
                            MF_EMAIL_EXTENSION
                    else:
                        emails_prefix_info[i] = emails_prefix_info[i] + \
                            MF_EMAIL_EXTENSION

                field = '\r\n'.join(emails_prefix_info)

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
    p = argparse.ArgumentParser(
        description='Helper tool to retreive inventor information from disclosures')
    p.add_argument(
        'pdf_root_dir', help='The root directory contains the disclosure PDFs', default=None)
    p.add_argument('-f', '--file', help='Output with the file path',
                   action='store_true')
    p.add_argument('-e', '--excel', help='Output with an excel')

    if len(args) == 0:
        p.print_help()

    return p.parse_args(args)


def output_to_excel(inventor_info, excel_path):
    wb = xlwt.Workbook()
    dt = datetime.now()
    ws = wb.add_sheet('Disclosures %s' % dt.strftime("%d. %B %Y"))
    if not excel_path.endswith('.xls'):
        excel_path = excel_path + '.xls'
    #      write title
    for c, title in enumerate(fields_title):
        ws.write(0, c, title)

    for r, info in enumerate(inventor_info):
        for c, title in enumerate(fields_title):
            value = int(info[title]) if info[title].isdigit() else info[title]
            if isinstance(value, str) and len(value) >= MAX_CELL_LEGAL_LENGTH:
                ws.write(r + 1, c, value[:MAX_CELL_LEGAL_LENGTH])
            else:
                ws.write(r + 1, c, value)

    wb.save(excel_path)


# textract internally called a pdftotext.exe which inside of mingwin\bin.
# the pdftotext.exe have to be added inside of the system search path!!!
if __name__ == '__main__':
    args = parse_commandlines(sys.argv[1:])
    if args.pdf_root_dir:
        pdfs = get_all_pdfs(args.pdf_root_dir)
        inventor_info = [fields for fields in (get_fields(
            interested_field_bars, args.file, pdf) for pdf in pdfs) if fields]

        if inventor_info:
            inventor_info = sorted(
                inventor_info, key=lambda info: info['Team'])
            if args.excel:
                output_to_excel(inventor_info, args.excel)
            else:
                pp(inventor_info)

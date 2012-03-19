#! /usr/bin/env python
from __future__ import print_function
from lxml import etree
import argparse
import platform
import urllib2
import string
import sys
import os
import re

RESOURCE_DICTS = [{'arg': 'pdfs',  'extension': 'pdf'},
                  {'arg': 'pptx',  'extension': 'pptx'},
                  {'arg': 'subs',  'extension': 'srt'},
                  {'arg': 'video', 'extension': 'mp4'}]

WIN_VALID_CHARS = "-_.() " + string.ascii_letters + string.digits
MAX_WIN_FILE_SIZE = 50
MAX_LINUX_FILE_SIZE = 140
IS_WINDOWS = platform.system() == 'Windows'

def make_valid_filename(filename):
    if IS_WINDOWS:
        return ''.join((c if c in WIN_VALID_CHARS else '_') for c in filename)[:MAX_WIN_FILE_SIZE]
    else:
        return filename.replace(os.sep, '_')[:MAX_LINUX_FILE_SIZE]

# Based in PabloG answer at http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
def download_to_file(url, file_name):
    open_url = urllib2.urlopen(url)
    with open(file_name, 'wb') as f:
        meta = open_url.info()
        length_headers = meta.getheaders('Content-Length')
        file_size = int(length_headers[0]) if length_headers else None
        print('Downloading: {}'.format(file_name))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buf = open_url.read(block_sz)
            if not buf:
                break

            file_size_dl += len(buf)
            f.write(buf)
            fsdmb = '{:d}'.format(file_size_dl / 1000000)
            fsdkb = '{:03d}'.format(file_size_dl / 1000 % 1000)
            fsd = '{}.{}'.format(fsdmb, fsdkb)
            if file_size:
                fsmb = '{:d}'.format(file_size / 1000000)
                fskb = '{:03d}'.format(file_size / 1000 % 1000)
                fs = '{}.{}'.format(fsmb, fskb)
                percentage = '{:.2f}'.format(file_size_dl * 100. / file_size)
                status = r'{:>8s}/{:s} Mb [{}%]'.format(fsd, fs, percentage)
            else:
                status = r'{:>8s} Mb'.format(fsd)
            status = status + chr(8) * (len(status) + 1)
            print(status, end='')


def clean_lecture_name(lecture_name):
    if '(' in lecture_name:
        lecture_name = lecture_name.rpartition('(')[0]
    return make_valid_filename(lecture_name.strip())

WEEK_RE = re.compile(r'(.*)\(week (\d+)\)$')
def take_week_from_section(section):
    week = 0
    match = WEEK_RE.match(section)
    if match:
        section, week = match.groups()
        section = section.strip()
        week = int(week)
    return section, week

def compare_sections(s1, s2):
    if (s1[1] != s2[1]):
        return s1[1] - s2[1]
    if (s1[2] != s2[2]):
        return s1[1] - s2[1]
    assert False


def main():
    parser = argparse.ArgumentParser(description='Gets lecture resources (videos by default) of an online Coursera course.')
    parser.add_argument('course_id', help='Course identifier (found in URL after www.coursera.org)')
    parser.add_argument('session_cookie', help='Valid session cookie for the course site. The cookie name is "session".')
    parser.add_argument('--pdfs', action='store_true', help='Get the pdfs for each lecture. Disabled by default.')
    parser.add_argument('--pptx', action='store_true', help='Get the pptx\'s for each lecture. Disabled by default.')
    parser.add_argument('--subs', action='store_true', help='Get the subtitles for each lecture. Disabled by default.')
    parser.add_argument('--no_video', dest='video', action='store_false', help='Do not download the videos. Use this if you only want other resources such as pdfs.')
    args = parser.parse_args()

    if not any(getattr(args, res_dict['arg']) for res_dict in RESOURCE_DICTS):
        print('You disabled video download but didn\'t enable any other resource for download.')
        sys.exit()

    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'session={}'.format(args.session_cookie)))
    urllib2.install_opener(opener)
    course_url = 'https://www.coursera.org/{}/lecture/index'.format(args.course_id)

    print('Trying to open lecture index page')
    try:
        doc = urllib2.urlopen(course_url).read()
    except urllib2.HTTPError:
        print('Failed to open lecture index page at {}'.format(course_url))
        print('Please make sure the course identifier you provided ({}) is correct.'.format(args.course_id))
        sys.exit()

    print('Done')
    tree = etree.HTML(doc)
    try:
        course_title = tree.xpath('//div[@id="course-logo-text"]/a/img/@alt')[0].strip()
    except IndexError:
        print('Failed to find course title.')
        print('This probably means the session cookie was incorrect and we failed to enter the lecture index page.')
        sys.exit()
    course_title = make_valid_filename(course_title)

    item_list = tree.xpath('//div[@class="item_list"]')[0]
    print('Starting downloads')
    sections = []
    for i in xrange(0, len(item_list)/2):
        section_el, lecture_list_el = item_list[2*i], item_list[2*i+1]
        section = section_el.xpath('./h3/text()')[0].strip()
        no_week_section, week = take_week_from_section(section)
        sections.append((no_week_section, week, i, lecture_list_el))
    sections = sorted(sections, compare_sections)

    for i, (no_week_section, week, _, lecture_list_el) in enumerate(sections, 1):
        section = '{} - {}'.format(i, no_week_section)
        if week:
            section += ' (week {})'.format(week)
        section = make_valid_filename(section)
        section_folder = os.path.join(course_title, section)
        if not os.path.exists(section_folder):
            os.makedirs(section_folder)
        lecture_names = lecture_list_el.xpath('./li/a/text()')
        clean_lecture_names = [clean_lecture_name(lecture_name) for lecture_name in lecture_names]
        final_lecture_names = [os.path.join(section_folder, '{}.{} - {}'.format(i, j, vn)) for j, vn in enumerate(clean_lecture_names, 1)]
        url_list = lecture_list_el.xpath('./li/div[@class="item_resource"]/a/@href')
        for j, url in enumerate(url_list):
            resource_dict = RESOURCE_DICTS[j%4]
            if getattr(args, resource_dict['arg']):
                file_name = final_lecture_names[j/4]
                full_file_name = '{}.{}'.format(file_name, resource_dict['extension'])
                if not os.path.exists(full_file_name):
                    download_to_file(url, full_file_name)
    print('All requested resources have been downloaded')

if __name__ == '__main__':
    main()

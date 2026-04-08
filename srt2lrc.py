# -*- coding: utf-8 -*-

import os
import re
import codecs


def fileopen(input_file):
    encodings = ["utf-32", "utf-16", "utf-8", "cp1252", "gb2312", "gbk", "big5"]
    srt_src = ''
    for enc in encodings:
        try:
            with codecs.open(input_file, mode="r", encoding=enc) as fd:
                srt_src = fd.read()
                break
        except:
            continue
    return [srt_src, enc]


def srt2lrc(input_file):
    if '.lrc' in input_file:
        return input_file

    if not os.path.isfile(input_file):
        print(input_file + ' not exist')
        return

    src = fileopen(input_file)
    srt_content = src[0]

    if u'\ufeff' in srt_content:
        srt_content = srt_content.replace(u'\ufeff', '')

    srt_content = srt_content.replace("\r", "")
    lines = [x.strip() for x in srt_content.split("\n") if x.strip()]

    lrc_lines = []
    lrc_time = None
    output_file = '.'.join(input_file.split('.')[:-1]) + '.lrc'

    for ln in range(len(lines)):
        line = lines[ln]
        if re.match(r'-?\d\d:\d\d:\d\d', line):
            # parse start time from "HH:MM:SS,mmm --> HH:MM:SS,mmm"
            time_part = line.split('-->')[0].strip().replace('-0', '0')
            match = re.match(r'(\d+):(\d{2}):(\d{2})[,.](\d{2,3})', time_part)
            if match:
                h, m, s, ms = match.groups()
                total_min = int(h) * 60 + int(m)
                cs = ms[:2]  # centiseconds (first 2 digits)
                lrc_time = f"[{total_min:02d}:{s}.{cs}]"
        elif line.isdigit():
            continue
        else:
            if lrc_time:
                lrc_lines.append(lrc_time + line)
                lrc_time = None

    output_str = '\n'.join(lrc_lines) + '\n'
    output_str = output_str.encode('utf8')

    with open(output_file, 'wb') as output:
        output.write(output_str)

    output_file = output_file.replace('\\', '\\\\')
    output_file = output_file.replace('/', '//')
    return output_file

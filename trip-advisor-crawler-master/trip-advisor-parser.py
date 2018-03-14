#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Andrea Esuli (andrea@esuli.it)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import csv
import fnmatch
import os
import re
import sys
import codecs

if sys.version_info[0] >= 3:
    import html


def get_review_filesnames(input_dir):
    for root, dirnames, filenames in os.walk(input_dir):
        for filename in fnmatch.filter(filenames, '*.html'):
            yield os.path.join(root, filename)


def cleanhtml(htmltext):
    cleanre = re.compile('<.*?>')
    cleantext = re.sub(cleanre, ' ', htmltext)
    return cleantext


summaryre = re.compile(r'innerBubble(.*?)reportProblem', re.M | re.S)
overallratingre = re.compile(r'class="sprite-rating_s_fill rating_s_fill s([0-9])0\"')
reviewtextre = re.compile(r'<div class="entry">(.*?)</div>', re.M | re.S)
aspectre = re.compile(r'recommend-answer(.*?)</li>', re.M | re.S)
aspectratingre = re.compile(r'sprite-rating_ss_fill rating_ss_fill ss([0-9])0')
aspectnamere = re.compile(r'span>(.*)$', re.M | re.S)
hotelnamere = re.compile(r'warLocName">(.*)?</div>')
idre = re.compile(r'id="review_([0-9]+)"')


def get_aspect_ratings(block):
    rates = list()
    for aspectrating in aspectre.findall(block):
        rating = aspectratingre.findall(aspectrating)[0]
        name = aspectnamere.findall(aspectrating)[0].strip()
        rates.append(':'.join([name, rating]))
    return u';'.join(rates)


def main():
    # sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)
    parser = argparse.ArgumentParser(
        description='TripAdvisor Hotel parser')
    parser.add_argument('-d', '--dir', help='Directory with the data for parsing', required=True)
    parser.add_argument('-o', '--outfile', help='Output file path for saving the reviews in csv format', required=True)

    args = parser.parse_args()

    reviews = set()

    with codecs.open(args.outfile, 'w', encoding='utf8') as out:
        writer = csv.writer(out, lineterminator='\n')
        for filepath in get_review_filesnames(args.dir):
            with codecs.open(filepath, mode='r', encoding='utf8') as file:
                htmlpage = file.read()
            print(filepath)
            hotelname = hotelnamere.findall(htmlpage)[0]
            for block in summaryre.findall(htmlpage):
                id_ = idre.findall(block)[0]
                if id_ in reviews:
                    continue
                reviews.add(id_)
                reviewtext = reviewtextre.findall(block)[0]
                overallrating = int(overallratingre.findall(block)[0])
                if overallrating >= 4:
                    binaryrating = 'positive'
                else:
                    binaryrating = 'negative'
                reviewtext = cleanhtml(reviewtext).strip()
                if sys.version_info[0] >= 3:
                    try:
                        reviewtext = html.unescape(reviewtext)
                    except Exception:
                        pass
                    review = [id_, filepath, hotelname, reviewtext, overallrating, binaryrating]
                else:
                    review = [id_, filepath,
                                    unicode.encode(hotelname, encoding='ascii', errors='ignore'),
                                    unicode.encode(reviewtext, encoding='ascii', errors='ignore'), overallrating,
                                    binaryrating]
                writer.writerow(review)


if __name__ == '__main__':
    main()

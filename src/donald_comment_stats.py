# -*- coding: utf-8 -*-
"""A file that runs through a reddit dump, creates a synopsis of it and saves a json of the average
   values for a number of comments per day."""

import json
from collections import defaultdict
from datetime import datetime
import pickle
import os
import argparse

VERSION = '1.2.0'


def generate_pickle_file(target_file, pickle_file_name):
    """Generate a pickle file and return some data about that the_donald's scores."""
    infile = open(target_file, 'r')

    year = defaultdict(list)
    for line in infile:
        if line.find('The_Donald') > -1:  # We assume this case
            item = json.loads(line)
            if item['subreddit'].lower() == 'the_donald':
                try:
                    day = datetime.fromtimestamp(float(item['created_utc'])).timetuple().tm_yday
                except Exception as e:
                    pass
                    print e
                day_dict = {
                    'score': item.get('score', 0),
                    'ups': item.get('ups', 0),
                    'controversiality': item.get('controversiality', 0),
                    'author': item.get('author', '')
                }
                year[day].append(day_dict)
    with file(pickle_file_name, 'w') as outfile:
        pickle.dump(year, outfile)
    return year


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some reddit dumps')
    parser.add_argument('file', type=str, help='a file to load')
    args = parser.parse_args()

    target_dump_file = args.file
    target_base = os.path.basename(target_dump_file)
    target_pickle_file = '../pickles/{}.{}.pickle'.format(target_base, VERSION)

    if not os.path.isfile(target_pickle_file):
        year = generate_pickle_file(target_dump_file, target_pickle_file)
    else:
        with file(target_pickle_file, 'r') as infile:
            year = pickle.load(infile)

    json_obj = {}
    for key, value in year.iteritems():
        num_comments = len(value)
        if num_comments > 0:
            json_obj[key] = {
                'avg_score': reduce(lambda x, y: x + y['score'], value, 0) / num_comments,
                'avg_ups': reduce(lambda x, y: x + y['ups'], value, 0) / num_comments,
                'avg_contro': reduce(lambda x, y: x + y['controversiality'], value, 0) / num_comments,
                'total_comments': num_comments,
                'num_authors': len(set([_['author'] for _ in value]))
            }

    with file('../output/{}.{}.synopsis.json'.format(target_base, VERSION), 'w') as outfile:
        json.dump(json_obj, outfile, indent=3)

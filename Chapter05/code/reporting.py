#!/usr/bin/env python
# reporting
# Create reports with Jinja2
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Dec 13 10:20:22 2013 -0500
#
# ID: reporting.py [] benjamin@bengfort.com $

"""
Create reports with Jinja2
"""

##########################################################################
## Imports
##########################################################################

import csv
import json

from datetime import datetime
from jinja2 import Environment, PackageLoader, FileSystemLoader

from itertools import groupby
from operator import itemgetter

##########################################################################
## Chapter Code
##########################################################################

def extract_years(data):
    for country in data:
        for value in country[1]:
            yield value[0]

def extract_series(data, years):
    for country, cdata in data:
        cdata  = dict(cdata)
        series = [cdata[year] if year in cdata else None for year in years]
        yield {
            'name': country,
            'data': series,
        }

def dataset(path):
    column  = 'Average income per tax unit'
    include = ("United States", "France", "Italy", "Germany", "South Africa", "New Zealand")
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        key = itemgetter('Country')
        for key, values in groupby(reader, key=key):
            if key in include:
                yield key, [(int(value['Year']), float(value[column]))
                            for value in values if value[column]]

def write(context):
    path = "report-%s.html" % datetime.now().strftime("%Y%m%d")
    #jinjaenv = Environment(loader=PackageLoader('reporting', 'templates'))
    # 'templates' should be the path to the templates folder
    # as written, it is assumed to be in the current directory
    jinjaenv = Environment(loader = FileSystemLoader('templates'))
    template = jinjaenv.get_template('report.html')
    template.stream(context).dump(path)

def main(source):
    data   = list(dataset(source))
    years  = set(extract_years(data))

    context = {
        'title': "Average Income per Family, %i - %i" % (min(years), max(years)),
        'years': json.dumps(list(years)),
        'countries': [v[0] for v in data],
        'series': json.dumps(list(extract_series(data, years))),
    }

    write(context)

##########################################################################
## Main method run
##########################################################################

if __name__ == "__main__":
    #Change the path value below to point to the location of the data file"
    source = "../data/income_dist.csv"
    main(source)

#!/usr/bin/env python
# trends
# Build charts to inspect trends in the World's Top Incomes dataset
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Dec 13 11:38:49 2013 -0500
#
# ID: trends.py [] benjamin@bengfort.com $

"""
Build charts to inspect trends in the World's Top Incomes dataset
"""

##########################################################################
## Imports
##########################################################################

import csv
import sys

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.font_manager import FontProperties

##########################################################################
## Helper functions
##########################################################################

def headers(path):
    """
    Print out the various headers in the dataset
    """
    with open(path, 'r') as data:
        reader = csv.DictReader(data)
        fields = reader.fieldnames

    fields.remove("Country")
    fields.remove("Year")
    return zip(["col%i" % (idx+1) for idx in xrange(len(fields))], fields)

def yrange(data):
    """
    Get the range of years from the dataset
    """
    years = set()
    for row in data:
        if row[0] not in years:
            yield row[0]
            years.add(row[0])

##########################################################################
## Chapter Code
##########################################################################


def dataset(path, country="United States"):
    """
    Extract the data for the country provided. Default is United States.
    """
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in filter(lambda row: row["Country"]==country, reader):
            yield row

def timeseries(data, column):
    """
    Creates a year based time series for the given column.
    """
    for row in filter(lambda row: row[column], data):
        yield (int(row["Year"]), row[column])

def normalize(data):
    """
    Normalizes the data set. Expects a timeseries output
    """
    data =  list(data)
    norm =  np.array(list(d[1] for d in data), dtype="f8")
    mean =  norm.mean()
    norm /= mean
    return zip(yrange(data), norm)

def delta(first, second):
    """
    Returns an array of deltas for the two arrays.
    """
    first  = list(first)
    years  = yrange(first)
    first  = np.array(list(d[1] for d in first), dtype="f8")
    second = np.array(list(d[1] for d in second), dtype="f8")

    # Not for use in writing
    if first.size != second.size:
        first = np.insert(first, [0,0,0,0], [None, None, None, None])

    diff   = first - second
    return zip(years, diff)

def linechart(series, **kwargs):
    fig = plt.figure()
    ax  = plt.subplot(111)
    for line in series:
        line  = list(line)
        xaxis = [v[0] for v in line]
        data  = [v[1] for v in line]
        ax.plot(xaxis, data)

    if 'ylabel' in kwargs:
        ax.set_ylabel(kwargs['ylabel'])
        #plt.subplots_adjust(left=0.15)

    if 'title' in kwargs:
        plt.title(kwargs['title'])

    if 'labels' in kwargs:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
        fontP = FontProperties()
        fontP.set_size('small')
        ax.legend(kwargs.get('labels'), loc='center left',
                  bbox_to_anchor=(1, 0.5), prop=fontP)

    return fig

def stackedarea(series, **kwargs):
    fig = plt.figure()
    axe = fig.add_subplot(111)

    fnx = lambda s: np.array(list(v[1] for v in s), dtype="f8")
    yax = np.row_stack(fnx(s) for s in series)
    xax = np.arange(1917, 2008)

    polys = axe.stackplot(xax, yax)
    axe.margins(0,0)

    if 'ylabel' in kwargs:
        axe.set_ylabel(kwargs['ylabel'])

    if 'labels' in kwargs:
        box = axe.get_position()
        axe.set_position([box.x0, box.y0, box.width * 0.9, box.height])
        fontP = FontProperties()
        fontP.set_size('small')

        legendProxies = []
        for poly in polys:
            legendProxies.append(plt.Rectangle((0, 0), 1, 1, fc=poly.get_facecolor()[0]))

        axe.legend(legendProxies, kwargs.get('labels'), loc='center left',
                  bbox_to_anchor=(1, 0.5), prop=fontP)

    if 'title' in kwargs:
        plt.title(kwargs['title'])

    return fig

SHARE_LABELS = (
    "Top 10%",
    "Top 5%",
    "Top 1%",
    "Top 0.5%",
    "Top 0.1%",
)

def percent_income_share(source):
    """
    Create Income Share chart
    """
    columns = (
        "Top 10% income share",
        "Top 5% income share",
        "Top 1% income share",
        "Top 0.5% income share",
        "Top 0.1% income share",
    )
    source  = list(dataset(source))

    return linechart([timeseries(source, col) for col in columns], labels=SHARE_LABELS, title="U.S. Percentage Income Share", ylabel="Percentage")

def mean_normalized_percent_income_share(source):
    """
    Create Income Share chart
    """
    columns = (
        "Top 10% income share",
        "Top 5% income share",
        "Top 1% income share",
        "Top 0.5% income share",
        "Top 0.1% income share",
    )
    source  = list(dataset(source))

    return linechart([normalize(timeseries(source, col)) for col in columns], labels=SHARE_LABELS, title="Mean Normalized U.S. Percentage Income Share", ylabel="Percentage")

def capital_gains_lift(source):
    """
    Computes capital gains lift in top income percentages over time chart
    """
    columns = (
        ("Top 10% income share-including capital gains", "Top 10% income share"),
        ("Top 5% income share-including capital gains", "Top 5% income share"),
        ("Top 1% income share-including capital gains", "Top 1% income share"),
        ("Top 0.5% income share-including capital gains", "Top 0.5% income share"),
        ("Top 0.1% income share-including capital gains", "Top 0.1% income share"),
        ("Top 0.05% income share-including capital gains", "Top 0.05% income share"),
    )

    source  = list(dataset(source))
    series  = [delta(timeseries(source, a), timeseries(source, b)) for a, b in columns]

    return linechart(series, labels=SHARE_LABELS, title="U.S. Capital Gains Income Lift", ylabel="Percentage Difference")



def average_incomes(source):
    """
    Compares percantage average incomes
    """
    columns = (
        "Top 10% average income",
        "Top 5% average income",
        "Top 1% average income",
        "Top 0.5% average income",
        "Top 0.1% average income",
        "Top 0.05% average income",
    )

    source  = list(dataset(source))

    series = [timeseries(source, col) for col in columns]

    return linechart(series, labels=SHARE_LABELS, title="U.S. Average Income",  ylabel="2008 US Dollars")

def average_top_income_lift(source):
    """
    Compares top percentage average income over total average
    """

    columns = (
        ("Top 10% average income", "Top 0.1% average income"),
        ("Top 5% average income", "Top 0.1% average income"),
        ("Top 1% average income", "Top 0.1% average income"),
        ("Top 0.5% average income", "Top 0.1% average income"),
        ("Top 0.1% average income", "Top 0.1% average income"),
    )

    source  = list(dataset(source))
    series  = [delta(timeseries(source, a), timeseries(source, b)) for a, b in columns]
    new_series = []
    for s in series:
        new_series.append(s)

    print series
    print ")))))))__________________________"
    print new_series

    return linechart(new_series, labels=SHARE_LABELS, title="U.S. Income Disparity", ylabel="2008 US Dollars")



def income_composition(source):
    """
    Compares income composition
    """

    columns = (
        "Top 10% income composition-Wages, salaries and pensions",
        #"Top 10% income composition-Non-wage income",
        #"Top 10% income composition-Professional income",
        #"Top 10% income composition-Business income",
        "Top 10% income composition-Dividends",
        "Top 10% income composition-Interest Income",
        #"Top 10% income composition-Investment income",
        #"Top 10% income composition-Farming income",
        #"Top 10% income composition-Business income (industry, commerce)",
        #"Top 10% income composition-Capital income",
        #"Top 10% income composition-Non-commercial business income",
        "Top 10% income composition-Rents",
        #"Top 10% income composition-Self-employment income",
        "Top 10% income composition-Entrepreneurial income",
        #"Top 10% income composition-Property income",
        #"Top 10% income composition-Other",
        #"Top 10% income composition-Capital gains",
    )

    source  = list(dataset(source))
    labels  = ("Salary", "Dividends", "Interest", "Rent", "Business")
    return stackedarea([timeseries(source, col) for col in columns], labels=labels, title="U.S. Top 10% Income Composition", ylabel="Percentage")

def main(args):

    #Make sure that this points to the correct location
    # of the income_dist.csv file.
    DATASOURCE = "../data/income_dist.csv"

    if args and "--headers" in args:
        for item in headers(DATASOURCE): print "%s:\t%s" % item
        sys.exit(0)

    #linechart([timeseries(dataset(DATASOURCE), "Average income per tax unit"), ])
    #print normalize(timeseries(dataset(DATASOURCE), "Average income per tax unit"))

    #percent_income_share(DATASOURCE)
    #plt.savefig('figure/percent_income_share.png')

    #mean_normalized_percent_income_share(DATASOURCE)
    #plt.savefig('figure/mean_normalized_percent_income_share.png')

    #capital_gains_lift(DATASOURCE)
    #plt.savefig('figure/capital_gains_lift.png')

    #average_incomes(DATASOURCE)
    #plt.savefig('./average_incomes_by_percent_test.png')

    #average_top_income_lift(DATASOURCE)
    #plt.savefig('./average_top_income_lift_test.png')

    #income_composition(DATASOURCE)
    #plt.savefig('figure/income_composition.png')

##########################################################################
## Main method run
##########################################################################

if __name__ == "__main__":
    main(sys.argv[1:])

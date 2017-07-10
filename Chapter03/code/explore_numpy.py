#!/usr/bin/env python
# explore_numpy
# Explore the World's Top Income with NumPy
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Dec 12 21:24:35 2013 -0500
#
# ID: explore_numpy.py [] benjamin@bengfort.com $

"""
Explore the World's Top Income with NumPy
"""

##########################################################################
## Imports
##########################################################################

import csv
import numpy as np
import numpy.ma as ma

##########################################################################
## Chapter Code
##########################################################################

def headers(path):
    with open(path, 'r') as data:
        reader = csv.DictReader(data)
        fields = reader.fieldnames

    fields.remove("Country")
    fields.remove("Year")
    return dict(zip(fields, ["col%i" % (idx+1) for idx in xrange(len(fields))]))

def dataset(path):

    names = ["country", "year",]
    names.extend(["col%i" % (idx+1) for idx in xrange(352)])
    dtype = ["S64","i4"]
    dtype.extend(["f18" for idx in xrange(352)])

    dtype = zip(names, dtype)

    return np.genfromtxt(path, delimiter=',', dtype=dtype, skip_header=1)

def mask_nan(array):
    return ma.masked_invalid(array)

def main(path):
    data = dataset(path)
    print data.size
    print data.shape
    print data.ndim
    print data.itemsize
    print data.nbytes

    #print data

##########################################################################
## Main method run
##########################################################################

if __name__ == "__main__":
    main("../data/income_dist.csv")

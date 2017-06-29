
import os
import csv
import heapq

from datetime import datetime
from collections import defaultdict
from operator import itemgetter

def relative_path(path):
    """
    Returns a path relative from this file
    """
    #dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(os.path.realpath('__file__'))
    path = os.path.join(dirname, path)
    return os.path.normpath(path)

def load_reviews(path, **kwargs):
    """
    Loads Movielens reviews
    """
    options = {
        'fieldnames': ('userid', 'movieid', 'rating', 'timestamp'),
        'delimiter': '\t',
    }
    options.update(kwargs)

    parse_date = lambda r,k: datetime.fromtimestamp(float(r[k]))
    parse_int  = lambda r,k: int(r[k])

    with open(path, 'rb') as reviews:
        reader = csv.DictReader(reviews, **options)
        for row in reader:
            row['movieid'] = parse_int(row, 'movieid')
            row['userid'] = parse_int(row, 'userid')
            row['rating'] = parse_int(row, 'rating')
            row['timestamp'] = parse_date(row, 'timestamp')
            yield row

def load_movies(path, **kwargs):
    """
    Loads Movielens movies
    """

    options = {
        'fieldnames': ('movieid', 'title', 'release', 'video', 'url'),
        'delimiter': '|',
        'restkey': 'genre',
    }
    options.update(kwargs)

    parse_int  = lambda r,k: int(r[k])
    parse_date = lambda r,k: datetime.strptime(r[k], '%d-%b-%Y') if r[k] else None

    with open(path, 'rb') as movies:
        reader = csv.DictReader(movies, **options)
        for row in reader:
            row['movieid'] = parse_int(row, 'movieid')
            row['release'] = parse_date(row, 'release')
            row['video']   = parse_date(row, 'video')
            yield row

class MovieLens(object):
    """
    Data structure to build our recommender model on.
    """

    def __init__(self, udata, uitem):
        """
        Instantiate with a path to u.data and u.item
        """
        self.udata   = udata
        self.uitem   = uitem
        self.movies  = {}
        self.reviews = defaultdict(dict)
        self.load_dataset()

    def load_dataset(self):
        """
        Loads the two datasets into memory, indexed on the ID.
        """
        for movie in load_movies(self.uitem):
            self.movies[movie['movieid']] = movie

        for review in load_reviews(self.udata):
            self.reviews[review['userid']][review['movieid']] = review

    def reviews_for_movie(self, movieid):
        """
        Yields the reviews for a given movie
        """
        for review in self.reviews.values():
            if movieid in review:
                yield review[movieid]

    def average_reviews(self):
        """
        Averages the star rating for all movies. Yields a tuple of movieid,
        the average rating, and the number of reviews.
        """
        for movieid in self.movies:
            reviews = list(r['rating'] for r in self.reviews_for_movie(movieid))
            average = sum(reviews) / float(len(reviews))
            yield (movieid, average, len(reviews))

    def bayesian_average(self, c=59, m=3):
        """
        Reports the Bayesian average with parameters c and m.
        """
        for movieid in self.movies:
            reviews = list(r['rating'] for r in self.reviews_for_movie(movieid))
            average = ((c * m) + sum(reviews)) / float(c + len(reviews))
            yield (movieid, average, len(reviews))

    def top_rated(self, n=10):
        """
        Yields the n top rated movies
        """
        return heapq.nlargest(n, self.bayesian_average(), key=itemgetter(1))

if __name__ == '__main__':
    data  = relative_path('../data/ml-100k/u.data')
    item  = relative_path('../data/ml-100k/u.item')
    model = MovieLens(data, item)

    for mid, avg, num in model.top_rated(10):
        title = model.movies[mid]['title']
        print "[%0.3f average rating (%i reviews)] %s" % (avg, num,title)

#    print float(sum(num for mid, avg, num in model.average_reviews())) / len(model.movies)

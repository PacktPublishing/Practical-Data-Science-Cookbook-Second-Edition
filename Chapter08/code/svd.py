
import os
import csv
import time
import heapq
import pickle
import numpy as np
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

    parse_int  = lambda r,k: int(r[k])

    with open(path, 'rb') as reviews:
        reader = csv.DictReader(reviews, **options)
        for row in reader:
            row['userid']  = parse_int(row, 'userid')
            row['movieid'] = parse_int(row, 'movieid')
            row['rating']  = parse_int(row, 'rating')
            yield row

def initialize(R, K):
    """
    Returns initial matrices for an N X M matrix, R and K features.

    :param R: the matrix to be factorized
    :param K: the number of latent features

    :returns: P, Q initial matrices of N x K and M x K sizes
    """
    N, M = R.shape
    P = np.random.rand(N,K)
    Q = np.random.rand(M,K)

    return P, Q

def factor(R, P=None, Q=None, K=2, steps=5000, alpha=0.0002, beta=0.02):
    """
    Performs matrix factorization on R with given parameters.

    :param R: A matrix to be factorized, dimension N x M
    :param P: an initial matrix of dimension N x K
    :param Q: an initial matrix of dimension M x K
    :param K: the number of latent features
    :param steps: the maximum number of iterations to optimize in
    :param alpha: the learning rate for gradient descent
    :param beta:  the regularization parameter

    :returns: final matrices P and Q
    """

    if not P or not Q:
        P, Q = initialize(R, K)
    Q = Q.T

    rows, cols = R.shape
    for step in xrange(steps):
        for i in xrange(rows):
            for j in xrange(cols):
                if R[i,j] > 0:
                    eij = R[i,j] - np.dot(P[i,:], Q[:,j])
                    for k in xrange(K):
                        P[i,k] = P[i,k] + alpha * (2 * eij * Q[k,j] - beta * P[i,k])
                        Q[k,j] = Q[k,j] + alpha * (2 * eij * P[i,k] - beta * Q[k,j])

        e  = 0
        for i in xrange(rows):
            for j in xrange(cols):
                if R[i,j] > 0:
                    e = e + pow(R[i,j] - np.dot(P[i,:], Q[:,j]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * (pow(P[i,k], 2) + pow(Q[k,j], 2))
        if e < 0.001:
            break

    return P, Q.T

def factor2(R, P=None, Q=None, K=2, steps=5000, alpha=0.0002, beta=0.02):
    """
    Performs matrix factorization on R with given parameters.

    :param R: A matrix to be factorized, dimension N x M
    :param P: an initial matrix of dimension N x K
    :param Q: an initial matrix of dimension M x K
    :param K: the number of latent features
    :param steps: the maximum number of iterations to optimize in
    :param alpha: the learning rate for gradient descent
    :param beta:  the regularization parameter

    :returns: final matrices P and Q
    """

    if not P or not Q:
        P, Q = initialize(R, K)
    Q = Q.T

    rows, cols = R.shape
    for step in xrange(steps):

        eR = np.dot(P, Q)   # Compute dot product only once

        for i in xrange(rows):
            for j in xrange(cols):
                if R[i,j] > 0:
                    eij = R[i,j] - eR[i,j]
                    for k in xrange(K):
                        P[i,k] = P[i,k] + alpha * (2 * eij * Q[k,j] - beta * P[i,k])
                        Q[k,j] = Q[k,j] + alpha * (2 * eij * P[i,k] - beta * Q[k,j])

        eR = np.dot(P, Q)   # Compute dot product only once
        e  = 0

        for i in xrange(rows):
            for j in xrange(cols):
                if R[i,j] > 0:
                    e = e + pow((R[i,j] - eR[i,j]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * (pow(P[i,k], 2) + pow(Q[k,j], 2))
        if e < 0.001:
            break

    return P, Q.T

class Recommender(object):

    @classmethod
    def load(klass, pickle_path):
        """
        Instantiates the class by deserializing the pickle. Note that the
        object returned may not be an exact match to the code in this
        class (if it was saved before updates).
        """
        with open(pickle_path, 'rb') as pkl:
            return pickle.load(pkl)

    def __init__(self, udata, description=None):
        self.udata   = udata
        self.users   = None
        self.movies  = None
        self.reviews = None

        # Descriptive properties
        self.build_start  = None
        self.build_finish = None
        self.description  = None

        # Model properties
        self.model        = None
        self.features     = 2
        self.steps        = 5000
        self.alpha        = 0.0002
        self.beta         = 0.02

        self.load_dataset()

    def load_dataset(self):
        """
        Loads an index of users and movies as a heap and a reviews table
        as a N x M array where N is the number of users and M is the number
        of movies. Note that order matters so that we can look up values
        outside of the matrix!
        """
        self.users  = set([])
        self.movies = set([])
        for review in load_reviews(self.udata):
            self.users.add(review['userid'])
            self.movies.add(review['movieid'])

        self.users  = sorted(self.users)
        self.movies = sorted(self.movies)

        self.reviews = np.zeros(shape=(len(self.users), len(self.movies)))
        for review in load_reviews(self.udata):
            uid = self.users.index(review['userid'])
            mid = self.movies.index(review['movieid'])
            self.reviews[uid, mid] = review['rating']

    def build(self, output=None, alternate=False):
        """
        Trains the model by employing matrix factorization on our training
        data set, the sparse reviews matrix. The model is the dot product
        of the P and Q decomposed matrices from the factorization.
        """
        options = {
            'K':     self.features,
            'steps': self.steps,
            'alpha': self.alpha,
            'beta':  self.beta,
        }

        self.build_start = time.time()
        nnmf = factor2 if alternate else factor
        self.P, self.Q = nnmf(self.reviews, **options)
        self.model = np.dot(self.P, self.Q.T)
        self.build_finish = time.time()

        if output:
            self.dump(output)

    def dump(self, pickle_path):
        """
        Dump the object into a serialized file using the pickle module.
        This will allow us to quickly reload our model in the future.
        """
        with open(pickle_path, 'wb') as pkl:
            pickle.dump(self, pkl)

    def sparsity(self):
        """
        Report the percent of elements that are zero in the array
        """
        return 1 - self.density()

    def density(self):
        """
        Return the percent of elements that are nonzero in the array
        """
        nonzero = float(np.count_nonzero(self.reviews))
        return nonzero / self.reviews.size

    def error_rate(self):
        """
        Compute the sum squared error of the trained model.
        """
        error = 0.0
        rows, cols = self.reviews.shape
        for idx in xrange(rows):
            for jdx in xrange(cols):
                if self.reviews[idx, jdx] > 0:
                    error += (self.model[idx, jdx] - self.reviews[idx, jdx]) ** 2
                    print error
        return error

    def predict_ranking(self, user, movie):
        uidx = self.users.index(user)
        midx = self.movies.index(movie)
        return self.model[uidx, midx]

    def top_rated(self, user, n=12):
        movies = [(mid, self.predict_ranking(user, mid)) for mid in self.movies]
        return heapq.nlargest(n, movies, key=itemgetter(1))

def main(*args):
    """
    Quick helper to build recommendation models
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('data', type=str, nargs=1, help='location of training data')
    parser.add_argument('-a', '--alternate', action='store_true', default=False, help='use alternate algorithm for factorization')
    parser.add_argument('-o', '--outpath', type=str, default=None, required=True, help='where to write pickle to.')
    args = parser.parse_args()


    data  = relative_path(args.data[0])
    model = Recommender(data)
    model.build(output=args.outpath, alternate=args.alternate)

    delta = model.build_finish - model.build_start
    print "Took %0.3f seconds to build" % delta
    print "Saved the pickle to: %s" % args.outpath
    print "Used the %s factorization function" % ('alternate' if args.alternate else 'standard')


if __name__ == '__main__':
    #main()
    rec = Recommender.load('reccod.pickle')
    for item in rec.top_rated(234):
        print "%i: %0.3f" % item

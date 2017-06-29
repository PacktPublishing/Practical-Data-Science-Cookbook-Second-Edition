
import heapq
import os

from math import sqrt
from model import MovieLens as ModelBase
from model import relative_path
from operator import itemgetter


def relative_path(path):
    """
    Returns a path relative from this file
    """
    #dirname = os.path.dirname(__file__)
    dirname = os.path.dirname(os.path.realpath('__file__'))
    path = os.path.join(dirname, path)
    return os.path.normpath(path)

class MovieLens(ModelBase):

    def shared_preferences(self, criticA, criticB):
        """
        Returns the intersection of ratings for two critics, A and B.
        """
        if criticA not in self.reviews:
            raise KeyError("Couldn't find critic '%s' in data" % criticA)
        if criticB not in self.reviews:
            raise KeyError("Couldn't find critic '%s' in data" % criticB)

        moviesA = set(self.reviews[criticA].keys())
        moviesB = set(self.reviews[criticB].keys())
        shared   = moviesA & moviesB # Intersection operator

        # Create a reviews dictionary to return
        reviews  = {}
        for movieid in shared:
            reviews[movieid] = (
                self.reviews[criticA][movieid]['rating'],
                self.reviews[criticB][movieid]['rating'],
            )
        return reviews

    def shared_critics(self, movieA, movieB):
        """
        Returns the intersection of critics for two items, A and B
        """

        if movieA not in self.movies:
            raise KeyError("Couldn't find movie '%s' in data" % movieA)
        if movieB not in self.movies:
            raise KeyError("Couldn't find movie '%s' in data" % movieB)

        criticsA = set(critic for critic in self.reviews if movieA in self.reviews[critic])
        criticsB = set(critic for critic in self.reviews if movieB in self.reviews[critic])
        shared   = criticsA & criticsB # Intersection operator

        # Create the reviews dictionary to return
        reviews  = {}
        for critic in shared:
            reviews[critic] = (
                self.reviews[critic][movieA]['rating'],
                self.reviews[critic][movieB]['rating'],
            )
        return reviews

    def euclidean_distance(self, criticA, criticB, prefs='users'):
        """
        Reports the Euclidean distance of two critics, A and B by
        performing a J-dimensional Euclidean calculation of each of their
        preference vectors for the intersection of books the critics have
        rated.
        """

        # Get the intersection of the rated titles in the data.

        if prefs == 'users':
            preferences = self.shared_preferences(criticA, criticB)
        elif prefs == 'movies':
            preferences = self.shared_critics(criticA, criticB)
        else:
            raise Exception("No preferences of type '%s'." % prefs)

        # If they have no rankings in common, return 0.
        if len(preferences) == 0: return 0

        # Sum the squares of the differences
        sum_of_squares = sum([pow(a-b, 2) for a, b in preferences.values()])

        # Return the inverse of the distance to give a higher score to
        # folks who are more similar (e.g. less distance) add 1 to prevent
        # division by zero errors and normalize ranks in [0, 1]
        return 1 / (1 + sqrt(sum_of_squares))

    def pearson_correlation(self, criticA, criticB, prefs='users'):
        """
        Returns the Pearson Correlation of two critics, A and B by
        performing the PPMC calculation on the scatter plot of (a, b)
        ratings on the shared set of critiqued titles.
        """

        # Get the set of mutually rated items
        if prefs == 'users':
            preferences = self.shared_preferences(criticA, criticB)
        elif prefs == 'movies':
            preferences = self.shared_critics(criticA, criticB)
        else:
            raise Exception("No preferences of type '%s'." % prefs)

        # Store the length to save traversals of the len computation.
        # If they have no rankings in common, return 0.
        length = len(preferences)
        if length == 0: return 0

        # Loop through the preferences of each critic once and compute the
        # various summations that are required for our final calculation.
        sumA = sumB = sumSquareA = sumSquareB = sumProducts = 0
        for a, b in preferences.values():
            sumA += a
            sumB += b
            sumSquareA  += pow(a, 2)
            sumSquareB  += pow(b, 2)
            sumProducts += a*b

        # Calculate Pearson Score
        numerator   = (sumProducts*length) - (sumA*sumB)
        denominator = sqrt(((sumSquareA*length) - pow(sumA, 2))
                            * ((sumSquareB*length) - pow(sumB, 2)))

        # Prevent division by zero.
        if denominator == 0: return 0

        return abs(numerator / denominator)

    def similar_critics(self, user, metric='euclidean', n=None):
        """
        Finds and ranks similar critics for the user according to the
        specified distance metric. Returns the top n similar critics.
        """

        # Metric jump table
        metrics  = {
            'euclidean': self.euclidean_distance,
            'pearson':   self.pearson_correlation,
        }

        distance = metrics.get(metric, None)

        # Handle problems that might occur
        if user not in self.reviews:
            raise KeyError("Unknown user, '%s'." % user)
        if not distance or not callable(distance):
            raise KeyError("Unknown or unprogrammed distance metric '%s'." % metric)

        # Compute user to critic similarities for all critics
        critics = {}
        for critic in self.reviews:
            # Don't compare against yourself!
            if critic == user:
                continue

            critics[critic] = distance(user, critic)

        if n:
            return heapq.nlargest(n, critics.items(), key=itemgetter(1))
        return critics

    def similar_items(self, movie, metric='euclidean', n=None):
        # Metric jump table
        metrics  = {
            'euclidean': self.euclidean_distance,
            'pearson':   self.pearson_correlation,
        }

        distance = metrics.get(metric, None)

        # Handle problems that might occur
        if movie not in self.reviews:
            raise KeyError("Unknown movie, '%s'." % movie)
        if not distance or not callable(distance):
            raise KeyError("Unknown or unprogrammed distance metric '%s'." % metric)

        items = {}
        for item in self.movies:
            if item == movie:
                continue

            items[item] = distance(item, movie, prefs='movies')

        if n:
            return heapq.nlargest(n, items.items(), key=itemgetter(1))
        return items

    def predict_ranking(self, user, movie, metric='euclidean', critics=None):
        """
        Predicts the ranking a user might give a movie according to the
        weighted average of the critics that are similar to the that user.
        """

        critics = critics or self.similar_critics(user, metric=metric)
        total   = 0.0
        simsum  = 0.0

        for critic, similarity in critics.items():
            if movie in self.reviews[critic]:
                total  += similarity * self.reviews[critic][movie]['rating']
                simsum += similarity

        if simsum == 0.0: return 0.0
        return total / simsum

    def predict_all_rankings(self, user, metric='euclidean', n=None):
        """
        Predicts all rankings for all movies, if n is specified returns
        the top n movies and their predicted ranking.
        """
        critics = self.similar_critics(user, metric=metric)
        movies = {
            movie: self.predict_ranking(user, movie, metric, critics)
            for movie in self.movies
        }

        if n:
            return heapq.nlargest(n, movies.items(), key=itemgetter(1))
        return movies

    def predict_items_recommendation(self, user, movie, metric='euclidean'):
        movies = self.similar_items(movie, metric=metric)
        total  = 0.0
        simsum = 0.0

        for relmovie, similarity in movies.items():
            # Ignore movies already reviewed by user
            if relmovie in self.reviews[user]:
                total  += similarity * self.reviews[user][relmovie]['rating']
                simsum += similarity

        if simsum == 0.0: return 0.0
        return total / simsum


if __name__ == '__main__':
    data  = relative_path('../data/ml-100k/u.data')
    item  = relative_path('../data/ml-100k/u.item')
    model = MovieLens(data, item)

    #for uid in model.reviews.keys():
    #    ratings = sum([r for m,r in model.predict_all_rankings(uid, 'pearson', 10)])
    #    if ratings < 50.0:
    #        print uid

    #for mid, rating in model.predict_all_rankings(578, 'pearson', 10):
    #    print "%0.3f: %s" % (rating, model.movies[mid]['title'])

    movie = 631
    user  = 422
    #print model.predict_ranking(user, movie, 'euclidean')
    #print model.predict_ranking(user, movie, 'pearson')

    #print model.reviews[user][movie]

    #print "Similar to %s" % model.movies[movie]['title']
    #for other_movie, similarity in model.similar_items(movie, 'pearson').items():
    #    print "%0.3f: %s" % (similarity, model.movies[other_movie]['title'])

    #print model.predict_items_recommendation(232, 52, 'pearson')
    print model.similar_items(movie, n=10)

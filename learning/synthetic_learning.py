import sys
sys.path.insert(0, 'paper/')
from learning_utils import viewed_matrix
from learning_utils import filter_unseen_movies
from aspect_importance import dict_movie_aspect
from aspect_importance import users_movie_aspect_preferences
from simple_similarity import sample_users
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from scipy import spatial
from paper import ids
import pickle
import numpy as np
import pandas as pd
import pprint as pp
import time

THREADS = cpu_count() - 1


def map_similarity(x):
	a, b = x
	user_id1, user_genre_prefs1 = a
	user_id2, user_genre_prefs2 = b
	sim = (1 - spatial.distance.cosine(list(user_genre_prefs1.values()), list(user_genre_prefs2.values())))
	return user_id1, user_id2, sim


def user_genre_similarity(users_genres_prefs):
	user_genre_similarity_dict = dict()
	for user in list(users_genres_prefs.keys()):
		user_genre_similarity_dict[user] = dict()

	pairwise_user_profiles = []

	items = list(users_genres_prefs.items())
	for idx1 in range(len(items)):
		for idx2 in range(idx1+1, len(items)):
			pairwise_user_profiles.append((items[idx1], items[idx2]))

	with ProcessPoolExecutor(max_workers=THREADS) as executor:
		results = executor.map(map_similarity, pairwise_user_profiles)
	for user_id1, user_id2, sim in results:
		user_genre_similarity_dict[user_id1][user_id2] = sim
		user_genre_similarity_dict[user_id2][user_id1] = sim

	return user_genre_similarity_dict


def user_prefs(movies_watched, movies_aspects, users, aspect_type, normalized, rating_to_like=False):
	movies_aspects = filter_unseen_movies(movies_aspects, movies_watched)
	movies_aspects = pd.DataFrame.from_dict(movies_aspects, dtype='int64', orient='index')
	movies_aspects = movies_aspects.replace(np.nan, 0)

	# print ("\nMOVIES-ASPECTS %s %r" % (aspect_type, rating_to_like))
	# print (movies_aspects.to_string())

	users_aspects_prefs = users_movie_aspect_preferences(movies_aspects, movies_watched, users, normalized)

	# print ("\nUSER %s PREF RATING_TO_LIKE %r" % (aspect_type, rating_to_like))
	# print (pd.DataFrame.from_dict(users_aspects_prefs, orient='index').to_string())

	# file_name = "preference_%s_%r.pkl" % (aspect_type, rating_to_like)
	# afile = open(file_name, "wb")
	# pickle.dump(users_aspects_prefs, afile)
	# afile.close()

	return users_aspects_prefs


def user_sim(users_genres_prefs, rating_to_like=False):
	user_genre_similarity_dict = user_genre_similarity(users_genres_prefs)

	# print ("\nSIMILARITY USER GENRE PREF RATING_TO_LIKE %r" % rating_to_like)
	# print (pd.DataFrame.from_dict(user_genre_similarity_dict).to_string())

	# file_name = "similarity_%r.pkl" % rating_to_like
	# afile = open(file_name, "wb")
	# pickle.dump(user_genre_similarity_dict, afile)
	# afile.close()


if __name__ == "__main__":
	start = time.time()
	paper_ratings = pickle.load(open("db/paper_ratings.pkl", "rb"))
	paper_films = pickle.load(open("db/paper_films.pkl","rb"))
	movies_watched = viewed_matrix(paper_ratings, paper_films, sample_users)

	# print ("\nFILMS \n%s\n" % paper_films)
	# print ("\nFILMS WATCHED BY USERS RATING_TO_LIKE %r \n%s\n" % (False, movies_watched))

	normalized = True

	movies_actors = dict_movie_aspect(paper_films, "actors")
	users_actors_prefs = user_prefs(movies_watched, movies_actors, sample_users, "actors", normalized)

	movies_directors = dict_movie_aspect(paper_films, "director")
	users_diretors_prefs = user_prefs(movies_watched, movies_directors, sample_users, "director", normalized)

	movies_genres = dict_movie_aspect(paper_films, "genre")
	users_genres_prefs = user_prefs(movies_watched, movies_genres, sample_users, "genre", normalized)



	user_sim(users_genres_prefs)

	end = time.time()
	print (end - start)


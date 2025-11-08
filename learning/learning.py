from aspect_importance import dict_movie_aspect
from learning_utils import viewed_matrix
from synthetic_learning import user_prefs
from synthetic_learning import user_sim
from collections import Counter
import time
import pickle


def get_users_with_some_movies_rated(ratings, threshold):
	ids = []
	for k, x in ratings.items():
		ids.extend(x)

	uids = [x["user_id"] for x in ids]
	counter = Counter(uids)

	unique_ids = {x : counter[x] for x in counter if counter[x] >= threshold}

	# print (unique_ids)
	# print ("#counter users %d: %d" % (threshold, len(unique_ids)))
	return unique_ids


if __name__ == "__main__":
	start = time.time()
	ratings = pickle.load(open("db/movie_ratings_500_id.pkl","rb"))
	films = pickle.load(open("db/movie_metadata.pkl","rb"))

	users = get_users_with_some_movies_rated(ratings, 10)
	movies_watched = viewed_matrix(ratings, films, users)


	normalized = True

	movies_actors = dict_movie_aspect(films, "actors")
	users_actors_prefs = user_prefs(movies_watched, movies_actors, users, "actors", normalized)

	movies_directors = dict_movie_aspect(films, "director")
	users_diretors_prefs = user_prefs(movies_watched, movies_directors, users, "director", normalized)

	movies_genres = dict_movie_aspect(films, "genre")
	users_genres_prefs = user_prefs(movies_watched, movies_genres, users, "genre", normalized)


	user_sim(users_genres_prefs)

	end = time.time()
	print (end - start)


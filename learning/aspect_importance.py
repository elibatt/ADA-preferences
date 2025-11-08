from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
import pandas as pd
import numpy as np

THREADS = cpu_count() - 1



def map_aspect_values_to_movies(x):
	#associa a ogni (film,meta), "aspect" --> l'aspect, quindi genre per esempio
	(film, meta), aspect = x
	aspects = dict()
	if aspect == "director":
		aspects[meta[aspect]] = 1
	else:
		for g in meta[aspect]:
			aspects[g] = 1
	return film, meta, aspects


def dict_movie_aspect(paper_films, aspect):
	#crea coppie (film, aspect)
	print("sono in dict_movie_aspect")
	paper_films_aspect_prepended = map(lambda e: (e, aspect), list(paper_films.items()))

	aspect_dict = dict()

	results = list()
	with ProcessPoolExecutor(max_workers=THREADS) as executor:
		results = executor.map(map_aspect_values_to_movies, paper_films_aspect_prepended)
	

	for film, meta, aspects in results:
		#nel dizionario aspect_dict, quindi ad es genre_dict, ho indicizzato per
		# idfilm_titolo, quindi ho corrispondenza film/suoi generi o suo genere
		aspect_dict[film + "_" + meta["title"]] = aspects

	return aspect_dict





def map_user_profile_unnormalized(x):
	df, user, movies_aspect_values = x
	user_movies = df.loc[:, user]

	return user, user_movies.dot(movies_aspect_values).to_dict()


def map_user_profile_normalized(x):
	df, user, movies_aspect_values = x
	user_movies = df.loc[:, user]

	profile = user_movies.dot(movies_aspect_values)

	for name in list(movies_aspect_values.columns):
		mav = movies_aspect_values.loc[:, name]
		assert len(mav) == len(user_movies)
		seen = 0
		for i in range(len(mav)):
			if mav[i] != 0 and user_movies[i] != 0:
				seen += 1

		if seen != 0:
			profile[name] /= seen

	return user, profile.to_dict()


def users_movie_aspect_preferences(movies_aspect_values, movies_watched, users, normalized):
	df = pd.DataFrame.from_dict(movies_watched, orient='index')
	df = df.replace(np.nan, 0)
	# print ("\nMOVIES WATCHED BY USERS \n%s\n" % df.to_string())

	users_aspects_prefs = dict()

	with ProcessPoolExecutor(max_workers=THREADS) as executor:
		if normalized:
			results = executor.map(map_user_profile_normalized, [(df, user, movies_aspect_values) for user in users])
		else:
			results = executor.map(map_user_profile_unnormalized, [(df, user, movies_aspect_values) for user in users])
	for user, user_profile in results:
		users_aspects_prefs[user] = user_profile

	return users_aspects_prefs
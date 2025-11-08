from load_movies import get_all_movies
from load_movies import uniquify_movies
import urllib2
import json
import pickle


def call_api(movie, year):
	movie_title = movie.lower().replace(" ", "+")
	movie_year = year

	url = "http://www.omdbapi.com/?t=%s&y=%s&apikey=%s" % (movie_title, movie_year, API_KEY)

	response = urllib2.urlopen(url)
	data = json.load(response)

	return data


def get_movies_info(movies):
	movies_data = []
	for (movie, year) in movies:
		try:
			movies_data.append(call_api(movie, year))
		except Exception:
			continue
	afile = open("movies.pkl", "wb")
	pickle.dump(movies_data, afile)
	afile.close()


if __name__ == "__main__":
	movies = get_all_movies()
	movies = uniquify_movies(movies)
	movies = pickle.load(open("db/movies.pkl", "r"))
	print len(movies)

	



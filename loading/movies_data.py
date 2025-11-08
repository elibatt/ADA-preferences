from load_movies import get_all_movies
from load_movies import uniquify_movies
import pickle
import json
import re

YEAR_KEY = "Year"
TITLE_KEY = "Title"


def load_data_from_file(file_name):
	movies = []
	with open(file_name) as f:
	    content = f.readlines()
	content = [x.strip() for x in content] 

	for line in content:
		line_splitted = line.split(',', 1)
		uid = line_splitted[0]
		year = line_splitted[1][:4]
		title = line_splitted[1][5:]
		movies.append((uid, year, title))

	return movies


def get_netflix_selected_movies(movies):
	netflix_movies = load_data_from_file("files/movie_titles.txt")
	omdb_movies = pickle.load(open("db/movies.pkl","r"))

	movies_data = []

	for (movie, year) in movies:
		for (netflix_uid, netflix_year, netflix_title) in netflix_movies:

			# some names have ! in one db but not in the other...
			movie_simple = movie.lower().encode('ascii','ignore').replace(":", " ").replace("-", " ").replace(".", "").replace("?", "").replace("!", "")
			netflix_simple = netflix_title.lower().replace(":", " ").replace("-", " ").replace(".", "").replace("?", "").replace("!", "")
			movie_simple = re.sub(' +',' ',movie_simple)
			netflix_simple = re.sub(' +',' ',netflix_simple)
			movie_simple = movie_simple.strip()
			netflix_simple = netflix_simple.strip()

			if netflix_year == year and movie_simple == netflix_simple or netflix_year != "NULL" and movie_simple == netflix_simple and abs(int(netflix_year)-int(year)) == 1:
				f = open("ratings/mv_"+str(netflix_uid).zfill(7)+".txt",'r')
				lines = f.readlines()[1:501]
				f.close()

				md = dict()

				# OMDB data
				# md["movie"] = movie
				# md["year"] = year
				for film in omdb_movies:
					film_keys = film.keys()
					if YEAR_KEY in film_keys and TITLE_KEY in film_keys and film["Year"] == year and film["Title"] == movie:
						for key in film_keys:
							md[key] = film[key]

						# NETFLIX data

						md["netflix_uid"] = netflix_uid
						md["netflix_year"] = netflix_year
						md["netflix_title"] = netflix_title

						md["ratings"] = []

						for line in lines:
							[user_id, user_rating, user_rating_date] = line.strip().split(",")

							rating = dict()
							rating["user_id"] = user_id
							rating["user_rating"] = user_rating
							rating["user_rating_date"] = user_rating_date

							md["ratings"].append(rating)

				if md:
					movies_data.append(md)

	afile = open("movies_db.pkl", "wb")
	pickle.dump(movies_data, afile)
	afile.close()

	return movies_data


def jsonify_data():
	data = pickle.load(open("movies_db.pkl", "r"))
	with open('movies_db.json', 'w') as outfile:
		json.dump(data, outfile)


if __name__ == "__main__":
	movies = get_all_movies()
	movies = uniquify_movies(movies)
	
	netflix_selected_movies = get_netflix_selected_movies(movies)

	# jsonify_data()

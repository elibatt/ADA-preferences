from load_movies import get_all_actors

import json
import pickle


def call_api(imdb_id):
	url = "http://www.theimdbapi.org/api/movie?movie_id=%s" % (imdb_id)

	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

	url = urllib.request(url, headers=hdr)
	response = urllib.urlopen(url)
	data = json.load(response)

	return data


def get_star_actors(movies):
	imdb_movies_data = []
	for idx, movie in enumerate(movies):
		imdb_movie_data = call_api(movie["imdbID"])
		metadata = dict()
		metadata["imdbID"] = movie["imdbID"]
		metadata["director"] = imdb_movie_data["director"]
		metadata["title"] = imdb_movie_data["title"]
		metadata["genre"] = imdb_movie_data["genre"]

		metadata["cast"] = []
		for cast in imdb_movie_data["cast"]:
			metadata["cast"].append(cast["name"])

		metadata["stars"] = imdb_movie_data["stars"]

		imdb_movies_data.append(metadata)
		print(idx)

	afile = open('imdb_movies_actors.pkl', 'wb')
	pickle.dump(imdb_movies_data, afile)
	afile.close()

	return imdb_movies_data


if __name__ == "__main__":
	movies = pickle.load(open("db/movies_db_500.pkl", "r"))
	actors = get_all_actors()
	star_actors = get_star_actors(movies)

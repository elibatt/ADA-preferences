import sys
sys.path.insert(0, 'loading/')
from load_movies import get_all_actors
import pickle
import json

ACTOR_COLOUR = "yellow"
DIRECTOR_COLOUR = "green"
GENRE_COLOUR = "blue"
TITLE_COLOUR = "red"

ids = ['tt0289992','tt0338013','tt0308644','tt0162222','tt0362227','tt0203009','tt0373926','tt0264464','tt0315733','tt0327056']
paper_ids = ['tt0264464', 'tt0203009']



def paper_minimal():
	data = pickle.load(open("db/movie_metadata.pkl","r"))

	films = dict()
	for uid in ids:
		films[uid] = data[uid]

	afile = open('paper_films.pkl', 'wb')
	pickle.dump(films, afile)
	afile.close()


def paper_minimal_json():
	data = pickle.load(open("db/paper_films.pkl", "r"))
	ids = []
	graph = dict()
	graph["nodes"] = []
	graph["links"] = []

	for k, v in data.iteritems():
		if k in paper_ids:
			movie_root = v["title"] + "-" + k
			root_node = dict()
			root_node["id"] = movie_root
			root_node["colour"] = TITLE_COLOUR
			graph["nodes"].append(root_node)
			ids.append(movie_root)

			if v["director"] not in ids:
				ids.append(v["director"])
				director_node = dict()
				director_node["id"] = v["director"]
				director_node["colour"] = DIRECTOR_COLOUR
				graph["nodes"].append(director_node)
			director_link = dict()
			director_link["source"] = movie_root
			director_link["target"] = v["director"]
			graph["links"].append(director_link)

			for a in v["actors"]:
				if a not in ids:
					ids.append(a)
					actor_node = dict()
					actor_node["id"] = a
					actor_node["colour"] = ACTOR_COLOUR
					graph["nodes"].append(actor_node)
				actor_link = dict()
				actor_link["source"] = movie_root
				actor_link["target"] = a
				graph["links"].append(actor_link)

			for g in v["genre"]:
				if g not in ids:
					ids.append(g)
					genre_node = dict()
					genre_node["id"] = g
					genre_node["colour"] = GENRE_COLOUR
					graph["nodes"].append(genre_node)
				genre_link = dict()
				genre_link["source"] = movie_root
				genre_link["target"] = g
				graph["links"].append(genre_link)


	with open("paper_graph.json", "w") as outfile:
		json.dump(graph, outfile)


def get_popular_actors(actor_data, actors):
	popular_actors = actors
	for x in actor_data:
		for actor in x["stars"]:
			if actor not in popular_actors:
				popular_actors.append(actor)
	return popular_actors


def create_paper_metadata(movie_data, actor_data, popular_actors):
	movie_ratings = dict()

	for movie in movie_data:
		assert len(movie["ratings"]) <= 500
		movie_ratings[movie["imdbID"]] = movie["ratings"]

	afile = open("movie_ratings_500_id.pkl", "wb")
	pickle.dump(movie_ratings, afile)
	afile.close()


	movie_metadata = dict()
	for ad in actor_data:
		movie_metadata[ad["imdbID"]] = dict()
		movie_metadata[ad["imdbID"]]["title"] = ad["title"]
		movie_metadata[ad["imdbID"]]["director"] = ad["director"]
		movie_metadata[ad["imdbID"]]["genre"] = ad["genre"]

		actors = []
		for actor in ad["stars"]:
			actors.append(actor)

		for actor in ad["cast"]:
			if actor not in actors and actor in popular_actors:
				actors.append(actor)
		movie_metadata[ad["imdbID"]]["actors"] = actors


	afile = open("movie_metadata.pkl", "wb")
	pickle.dump(movie_metadata, afile)
	afile.close()


def paper_db():
	actors = get_all_actors()
	movie_data = pickle.load(open("db/movies_db_500.pkl","r"))
	actor_data = pickle.load(open("db/imdb_movies_actors.pkl","r"))
	assert len(movie_data) == len(actor_data)

	actors = get_popular_actors(actor_data, actors)
	create_paper_metadata(movie_data, actor_data, actors)


if __name__ == "__main__":
	# paper_db()
	paper_minimal_json()

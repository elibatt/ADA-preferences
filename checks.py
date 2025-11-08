from collections import Counter
import pickle

def check_all_db():
	movie_data_with_ratings = pickle.load(open("db/movies_db_500.pkl","rb"))
	movie_data_with_actors = pickle.load(open("db/imdb_movies_actors.pkl","rb"))

	ids = []

	for x in movie_data_with_ratings:
		ids.extend(x["ratings"])

	uids = [x["user_id"] for x in ids]
	counter = Counter(uids).items()
	counter = sorted(counter, key = lambda item: item[1])

	print(counter)

	ratings = []
	for x in movie_data_with_ratings:
		ratings.extend(x["ratings"])
	print ("#ratings %d" % len(ratings))

	print ("#movies %d" % len(movie_data_with_ratings))

	assert len(movie_data_with_ratings) == len(movie_data_with_actors)


def check_all_paper():
	ratings = pickle.load(open("db/movie_ratings_500_id.pkl","rb"))
	movie_metadata = pickle.load(open("db/movie_metadata.pkl","rb"))
	assert len(ratings) == len(movie_metadata)

	ids = []
	for k, x in ratings.items():
		ids.extend(x)

	uids = [x["user_id"] for x in ids]
	counter = Counter(uids)
	counter_items = counter.items()
	counter_items = sorted(counter_items, key = lambda item: item[1])

	print (counter_items)

	udirectors = []
	ugenres = []
	uactors = []

	for movie_id, movie_meta in movie_metadata.items():
		udirectors.append(movie_meta["director"])
		ugenres.extend(movie_meta["genre"])
		uactors.extend(movie_meta["actors"])

	udirectors = set(udirectors)
	ugenres = set(ugenres)
	uactors = set(uactors)

	print (udirectors)
	print (uactors)
	print (ugenres)

	print ("#movies %d" % len(movie_metadata))
	print ("#directors %d" % len(udirectors))
	print ("#actors %d" % len(uactors))
	print ("#genres %d" % len(ugenres))
	print ("#user votes %d" % len(uids))
	print ("#unique users %d" % len(set(uids)))

	print ("#counter users %d" % sum(list(counter.values())))

	# counter_above_threshold = {x : counter[x] for x in counter if counter[x] >= 5}
	# print ("#counter users %d" % sum(counter_above_threshold.values()))

	print ("#counter users 3 %d" % len({x : counter[x] for x in counter if counter[x] >= 3}))
	print ("#counter users 3 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 3}.values()))
	print ("#counter users 5 %d" % len({x : counter[x] for x in counter if counter[x] >= 5}))
	print ("#counter users 5 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 5}.values()))
	print ("#counter users 10 %d" % len({x : counter[x] for x in counter if counter[x] >= 10}))
	print ("#counter users 10 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 10}.values()))
	print ("#counter users 16 %d" % len({x : counter[x] for x in counter if counter[x] >= 16}))
	print ("#counter users 16 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 16}.values()))
	print ("#counter users 20 %d" % len({x : counter[x] for x in counter if counter[x] >= 20}))
	print ("#counter users 20 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 20}.values()))
	print ("#counter users 50 %d" % len({x : counter[x] for x in counter if counter[x] >= 50}))
	print ("#counter users 50 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 50}.values()))
	print ("#counter users 70 %d" % len({x : counter[x] for x in counter if counter[x] >= 70}))
	print ("#counter users 70 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 70}.values()))
	print ("#counter users 100 %d" % len({x : counter[x] for x in counter if counter[x] >= 100}))
	print ("#counter users 100 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 100}.values()))
	print ("#counter users 250 %d" % len({x : counter[x] for x in counter if counter[x] >= 250}))
	print ("#counter users 250 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 250}.values()))
	print ("#counter users 0 %d" % len({x : counter[x] for x in counter if counter[x] >= 0}))
	print ("#counter users 0 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 0}.values()))




check_all_paper()
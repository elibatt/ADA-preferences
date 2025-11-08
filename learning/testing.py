from collections import Counter
from surprise import Dataset
from surprise import Reader
from surprise import KNNBasic
from surprise import KNNWithZScore
from surprise import SVD
from surprise import NMF
from surprise import SlopeOne
from surprise import CoClustering
import pandas as pd
import pickle


def checks(counter):
	print ("#counter users 5 %d" % len({x : counter[x] for x in counter if counter[x] >= 5}))
	print ("#counter users 5 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 5}.values()))
	print ("#counter users 10 %d" % len({x : counter[x] for x in counter if counter[x] >= 10}))
	print ("#counter users 10 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 10}.values()))
	print ("#counter users 20 %d" % len({x : counter[x] for x in counter if counter[x] >= 20}))
	print ("#counter users 20 ratings %d" % sum({x : counter[x] for x in counter if counter[x] >= 20}.values()))

	print ("#counter users 5 < 10 %d" % len({x : counter[x] for x in counter if counter[x] < 10 and counter[x] >= 5}))
	print ("#counter users 5 < 10 ratings %d" % sum({x : counter[x] for x in counter if counter[x] < 10 and counter[x] >= 5}.values()))
	print ("#counter users 5 < 20 %d" % len({x : counter[x] for x in counter if counter[x] < 20 and counter[x] >= 5}))
	print ("#counter users 5 < 20 ratings %d" % sum({x : counter[x] for x in counter if counter[x] < 20 and counter[x] >= 5}.values()))


# based on check_all_paper from checks
def get_training_testing_user_ids(min_nr_movies_train, min_nr_movies_test, ratings, movie_metadata):
	assert len(ratings) == len(movie_metadata)

	ids = []
	for k, x in ratings.items():
		ids.extend(x)

	uids = [x["user_id"] for x in ids]
	counter = Counter(uids)
	counter_items = counter.items()
	counter_items = sorted(counter_items, key = lambda item: item[1])

	checks(counter)

	print ("\nNumber of users who rated less that min_nr_movies_test: %d" % len({x : counter[x] for x in counter if counter[x] < min_nr_movies_test}))

	return {x : counter[x] for x in counter if counter[x] >= min_nr_movies_train}, {x : counter[x] for x in counter if counter[x] < min_nr_movies_train and counter[x] >= min_nr_movies_test}


def get_data(uids, ratings):
	ratings_dict = dict()
	ratings_dict["itemID"] = []
	ratings_dict["userID"] = []
	ratings_dict["rating"] = []
	for film_id in ratings.keys():
		ratings_data = ratings[film_id]
		for rd in ratings_data:
			if rd["user_id"] in uids:
				ratings_dict["itemID"].append(film_id)
				ratings_dict["userID"].append(rd["user_id"])
				ratings_dict["rating"].append(rd["user_rating"])
	assert len(ratings_dict["itemID"]) == len(ratings_dict["userID"]) == len(ratings_dict["rating"])
	return ratings_dict


def add_first_X_movies_rated_for_users(train_ratings_dict, test_ratings_dict, X):
	compressed_test_ratings_dict = dict()
	for idx in range(len(test_ratings_dict["userID"])):
		user_id = test_ratings_dict["userID"][idx]
		if user_id not in compressed_test_ratings_dict.keys():
			compressed_test_ratings_dict[user_id] = []
		compressed_test_ratings_dict[user_id].append((test_ratings_dict["itemID"][idx], test_ratings_dict["rating"][idx]))
	
	for user_id in compressed_test_ratings_dict.keys():
		nr_moved_data = min(X, len(compressed_test_ratings_dict[user_id]))
		for i in range(nr_moved_data):
			train_ratings_dict["userID"].append(user_id)
			train_ratings_dict["itemID"].append(compressed_test_ratings_dict[user_id][i][0])
			train_ratings_dict["rating"].append(compressed_test_ratings_dict[user_id][i][1])
		compressed_test_ratings_dict[user_id] = compressed_test_ratings_dict[user_id][nr_moved_data:]

	assert len(train_ratings_dict["itemID"]) == len(train_ratings_dict["userID"]) == len(train_ratings_dict["rating"])	
	return compressed_test_ratings_dict, train_ratings_dict



def testing(min_nr_movies_train, min_nr_movies_test, alg):
	ratings = pickle.load(open("db/movie_ratings_500_id.pkl","rb"))
	train_ids, test_ids = get_training_testing_user_ids(min_nr_movies_train, min_nr_movies_test)
	train_ratings_dict = get_data(train_ids, ratings)
	test_ratings_dict = get_data(test_ids, ratings)

	compressed_test_ratings_dict, train_ratings_dict = add_first_X_movies_rated_for_users(train_ratings_dict, test_ratings_dict, min_nr_movies_test)
	
	train_df = pd.DataFrame(train_ratings_dict)
	train_reader = Reader(rating_scale=(1, 5))
	train_data = Dataset.load_from_df(train_df[['userID', 'itemID', 'rating']], train_reader) # columns must correspond to userID, itemID and ratings (in that order)

	trainset = train_data.build_full_trainset()
	if alg == "KNNBasic":
		algo = KNNBasic()
	if alg == "KNNWithZScore":
		algo = KNNWithZScore()
	if alg == "SVD":
		algo = SVD()
	if alg == "NMF":
		algo = NMF()
	if alg == "SlopeOne":
		algo = SlopeOne()
	if alg == "CoClustering":
		algo = CoClustering()

	algo.train(trainset)
	testset = trainset.build_anti_testset()
	predictions = algo.test(testset)

	rating_predictions = []
	for pred in predictions:
		try:
			if pred.uid in compressed_test_ratings_dict.keys():
				true_rating = [(item, rat) for (item, rat) in compressed_test_ratings_dict[pred.uid] if item == pred.iid]
				assert len(true_rating) == 1
				if true_rating:
					rating_predictions.append((pred.uid, true_rating[0][0], true_rating[0][1], pred.r_ui, pred.est))
		except Exception:
			continue

	afile = open(str(min_nr_movies_train) + "_" + str(min_nr_movies_test) + "_" + alg + ".pkl", "wb")
	pickle.dump(rating_predictions, afile)
	afile.close()


if __name__ == "__main__":

	testing(10, 5, "KNNBasic")
	testing(10, 5, "KNNWithZScore")
	testing(10, 5, "SVD")
	testing(10, 5, "NMF")
	testing(10, 5, "SlopeOne")
	testing(10, 5, "CoClustering")

	testing(20, 10, "KNNBasic")
	testing(20, 10, "KNNWithZScore")
	testing(20, 10, "SVD")
	testing(20, 10, "NMF")
	testing(20, 10, "SlopeOne")
	testing(20, 10, "CoClustering")

	testing(20, 13, "KNNBasic")
	testing(20, 13, "KNNWithZScore")
	testing(20, 13, "SVD")
	testing(20, 13, "NMF")
	testing(20, 13, "SlopeOne")
	testing(20, 13, "CoClustering")

	testing(20, 15, "KNNBasic")
	testing(20, 15, "KNNWithZScore")
	testing(20, 15, "SVD")
	testing(20, 15, "NMF")
	testing(20, 15, "SlopeOne")
	testing(20, 15, "CoClustering")

	testing(20, 5, "KNNBasic")
	testing(20, 5, "KNNWithZScore")
	testing(20, 5, "SVD")
	testing(20, 5, "NMF")
	testing(20, 5, "SlopeOne")
	testing(20, 5, "CoClustering")

	testing(20, 7, "KNNBasic")
	testing(20, 7, "KNNWithZScore")
	testing(20, 7, "SVD")
	testing(20, 7, "NMF")
	testing(20, 7, "SlopeOne")
	testing(20, 7, "CoClustering")


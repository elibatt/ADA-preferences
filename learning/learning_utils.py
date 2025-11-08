def viewed_matrix(paper_ratings, data, users=None, rating_to_like=False):
	movie_ids = data.keys()

	movies_watched = dict()

	for uid in movie_ids:
		movie_ratings = paper_ratings[uid]
		viewed = dict()
		for rat in movie_ratings:
			if users is not None:
			 	if rat["user_id"] in users:
			 		if rating_to_like:
			 			viewed[rat["user_id"]] = 1 if int(rat["user_rating"]) >= 3 else -1
			 		else:
			 			viewed[rat["user_id"]] = int(rat["user_rating"])
			else:
				if rating_to_like:
					viewed[rat["user_id"]] = 1 if int(rat["user_rating"]) >= 3 else -1
				else:
					viewed[rat["user_id"]] = int(rat["user_rating"])
		movies_watched[uid + "_" + data[uid]["title"]] = viewed

	return movies_watched


def all_unique_users(paper_ratings):
	ids = []
	for k, x in paper_ratings.items():
		ids.extend(x)

	uids = [x["user_id"] for x in ids]
	return list(set(uids))


def filter_unseen_movies(movies_genres, movies_watched):
	seen_movie_genres = dict()
	for k, v in movies_watched.items():
		if movies_watched[k]:
			seen_movie_genres[k] = movies_genres[k]
	return seen_movie_genres


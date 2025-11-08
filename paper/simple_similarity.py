import sys
sys.path.insert(0, 'learning/')
from learning_utils import viewed_matrix
from scipy import spatial
from collections import Counter
import operator
import numpy as np
import pandas as pd
import pickle
import pprint as pp

sample_users = ['1824033', '1409354', '2435946', '553658', '608915', '1753259', '2615678', '1443524', '771174']

def counter_paper_minimal():
	data = pickle.load(open("db/paper_films.pkl","rb"))
	movie_ratings = pickle.load(open("db/movie_ratings_500_id.pkl", "rb"))
	
	ratings = dict()
	for uid in data.keys():
		ratings[uid] = movie_ratings[uid]

	# afile = open('paper_ratings.pkl', 'wb')
	# pickle.dump(ratings, afile)
	# afile.close()

	ids = []
	for k, x in ratings.iteritems():
		ids.extend(x)

	uids = [x["user_id"] for x in ids]
	counter = Counter(uids).items()
	counter.sort(key = lambda item: item[1])

	print (counter)


def user_similarity_cosine_common(df, users):
	users_similarity = dict()
	for i in range(len(users)):
		users_similarity[users[i]] = []
		for j in range(len(users)):
			if i != j:
				user1_vals = [int(x) for x in df[users[i]].values.tolist()]
				user2_vals = [int(x) for x in df[users[j]].values.tolist()]
				
				assert len(user1_vals) == len(user2_vals)
				user1_common = []
				user2_common = []

				for k in range(len(user1_vals)):
					if user1_vals[k] != 0 and user2_vals[k] != 0:
						user1_common.append(user1_vals[k])
						user2_common.append(user2_vals[k])

				assert len(user1_common) == len(user2_common)

				if not user1_common or len(user1_common) == 1:
					sim = 0
				else:
					sim = (1 - spatial.distance.cosine(user1_common, user2_common))

				users_similarity[users[i]].append((users[j], sim))
		users_similarity[users[i]].sort(key=operator.itemgetter(1), reverse=True)

	return users_similarity


if __name__ == "__main__":
	paper_ratings = pickle.load(open("db/paper_ratings.pkl", "rb"))
	data = pickle.load(open("db/paper_films.pkl","rb"))
	movies_watched = viewed_matrix(paper_ratings, data, sample_users)
	print (pd.DataFrame.from_dict(movies_watched, orient='index').to_string())

	df = pd.DataFrame.from_dict(movies_watched, orient='index')
	df = df.replace(np.nan, 0)
	print (df.to_string())

	users_similarity = user_similarity_cosine_common(df, sample_users)
	pp.pprint(users_similarity)
	

	




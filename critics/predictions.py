from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from films_and_themes import films
from rt_films import threshold_af


from rt_data import rt_top_critics_reviews_tomatoes
from rt_data import rt_top_critics_score
from rt_scraping import rt_box_office
from rt_scraping import rt_top_movies
from sentiment import polarity_subjectivity
from semantics_dfquad import strengths_dfquad
from semantics_quad import strengths_quad
from semantics_dfquad import strengths_dfquad
from semantics_euler import strengths_euler
from compute_score import augment
from compute_score import unique_critics_score
from nlp_dl import process_af
from themes import get_sentences
from themes import film_entities
from themes import ngrams_themes
from themes import themes
from themes import fixed_entities
from spacy.lang.en import English
import en_core_web_sm
from keras.models import load_model
from itertools import chain
import os
import pickle
import json
import jsonlines
import re

THREADS = cpu_count() - 2


def compute(topic_entities_dict, film_title, rt_score, nr_critics):
	if len(topic_entities_dict["film"]["unique_args"]) < nr_critics/3:
			return None

	print ('FILM TITLE %s' % film_title)
	print ('RT SCORE %d' % rt_score)

	if semantics == "dfquad":
		film_score = strengths_dfquad(topic_entities_dict, nr_critics)
	elif semantics == "quad":
		film_score = strengths_quad(topic_entities_dict, nr_critics)
	elif semantics == "euler":
		film_score = strengths_euler(topic_entities_dict, nr_critics)

	print ('AF SCORE %f' % film_score)

	return (rt_score, film_score, film_title)


def process_url(url):
	film_title = url.split("m/")[2].split("/")[0].replace("_", " ")
	original_af_file = "RT/af/original/"+film_title+".json"

	if os.path.isfile(original_af_file):
		top_critics_reviews_tomatoes = rt_top_critics_reviews_tomatoes(url)
		nr_critics = len(top_critics_reviews_tomatoes)
		rt_score = rt_top_critics_score(url.split("reviews")[0])

		if not rt_score:
			return None

		topic_entities_dict = json.loads(open(original_af_file).read())
		topic_entities_dict = unique_critics_score(topic_entities_dict)
		topic_entities_dict = threshold_af(topic_entities_dict)
		topic_entities_dict = augment(topic_entities_dict, nr_critics)

		return compute(topic_entities_dict, film_title, rt_score, nr_critics)
	else:
		return None


def process_url_nlp(url, model, tokenizer):
	#model = load_model("critics/nlp/concat_False_lstm_dropout_after_lstm.h5")
	#tokenizer = pickle.load(open("critics/nlp/deep_tokenizer.pkl", "rb"))
	film_title = url.split("m/")[2].split("/")[0].replace("_", " ")
	original_af_file = "RT/af/original/"+film_title+".json"

	if os.path.isfile(original_af_file):
		top_critics_reviews_tomatoes = rt_top_critics_reviews_tomatoes(url)
		nr_critics = len(top_critics_reviews_tomatoes)
		rt_score = rt_top_critics_score(url.split("reviews")[0])

		if not rt_score:
			return None

		movie_af = json.loads(open(original_af_file).read())
		topic_entities_dict = process_af(movie_af, tokenizer, model)
		topic_entities_dict = unique_critics_score(topic_entities_dict)
		topic_entities_dict = threshold_af(topic_entities_dict)
		topic_entities_dict = augment(topic_entities_dict, nr_critics)
	
		return compute(topic_entities_dict, film_title, rt_score, nr_critics)
	else:
		return None


# uses original fetched AFs with sentiment/polarity
if __name__ == "__main__":

	semantics = input("semantics? dfquad/quad/euler ")
	with_themes = input("with themes? y/n ")
	method = input("sent/nlp? ")

	films = pickle.load(open("rt_bo_films.pkl", "rb"))

	#with ProcessPoolExecutor(max_workers=THREADS) as executor:
	#	if method == "sent":
	#		results = executor.map(process_url, [url for url in films])
	#	elif method == "nlp":
	#		results = executor.map(process_url_nlp, [url for url in films])

	model = load_model("critics/nlp/concat_False_lstm_dropout_after_lstm.h5")
	tokenizer = pickle.load(open("critics/nlp/deep_tokenizer.pkl", "rb"))
	results = []
	for idx, url in enumerate(films):
		print ("%d/%d" % (idx, len(films)))
		if method == "sent":
			results.append(process_url(url))
		elif method == "nlp":
			results.append(process_url_nlp(url, model, tokenizer))

	with jsonlines.open(('all_%s_%s_sent.jsonl' % (method, semantics)), mode='w') as writer:
		for x in results:
			if x != None:
				writer.write(x)

import sys
sys.path.insert(0, 'critics/nlp/')
from nlp.train_model import NEITHER_CLASS
from nlp.train_model import SUPPORT_CLASS
from nlp.train_model import ATTACK_CLASS
from nlp.deep_utils import MAX_SEQUENCE_LENGTH
from nlp.deep_utils import NR_CLASSES
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import numpy as np
import pickle
import json


def evaluate(parent_arg, child_arg, tokenizer, model):
	parent_sequence = tokenizer.texts_to_sequences([parent_arg])
	child_sequence = tokenizer.texts_to_sequences([child_arg])

	parent_tensor = pad_sequences(parent_sequence, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')[0]
	child_tensor = pad_sequences(child_sequence, maxlen=MAX_SEQUENCE_LENGTH, padding='post', truncating='post')[0]

	predicted_class = model.predict([np.array([parent_tensor]), np.array([child_tensor])], verbose=0)[0]
	predicted_class = np.argmax(predicted_class)

	if predicted_class == ATTACK_CLASS:
		return -1
	elif predicted_class == SUPPORT_CLASS:
		return 1
	elif predicted_class == NEITHER_CLASS:
		return 0


def process_af(film_af, tokenizer, model):
	film_af_am = dict()
	for attribute in film_af.keys():
		attribute_args = film_af[attribute]["args"]
		film_af_am[attribute] = dict()
		film_af_am[attribute]["args"] = []

		for (arg, polarity) in attribute_args:
			if arg.split("_"):
				relation = evaluate(str("%s is good" % (attribute)), str(arg.split("_")[1]), tokenizer, model)
				if relation != 0:
					film_af_am[attribute]["args"].append((arg, polarity))

		if "entities" in film_af[attribute].keys():
			film_af_am[attribute]["entities"] = dict()
			attribute_entities = film_af[attribute]["entities"]
			for ent in attribute_entities.keys():
				ent_args = attribute_entities[ent]["args"]

				film_af_am[attribute]["entities"][ent] = dict()
				film_af_am[attribute]["entities"][ent]["args"] = []

				for (ent_arg, ent_polarity) in ent_args:
					if ent_arg.split("_"):
						ent_relation = evaluate(str("%s is good" % (ent)), str(ent_arg.split("_")[1]), tokenizer, model)
						if ent_relation != 0:
							film_af_am[attribute]["entities"][ent]["args"].append((ent_arg, ent_polarity))

	return film_af_am



if __name__ == "__main__":
	model = load_model("critics/nlp/concat_False_lstm_dropout_after_lstm.h5")
	tokenizer = pickle.load(open("critics/nlp/deep_tokenizer.pkl", "rb"))

	movie_af = json.loads(open("RT/af/all_sent/inception_af.json").read())
	print (process_af(movie_af, tokenizer, model))

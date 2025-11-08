from rt_data import rt_writers_actors_directors

from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk import ngrams
from spacy.lang.en import English
import en_core_web_md
import string
import requests
import time
import re


# filter some grams
stop_grams = set(["-PRON-", "the", "that", "about", "and", "or", "a", "an", "this", "there", "where", "whatever", "whether", "however", "be", "with", "'d", "'ll", "'re", "'s", "'t", "'ve", "n't", "i", "other", "own", "who", "than", "both", "nothing", "else", "what", "stars", "anyone", "everybody", "may", "might", "should", "anything"])
fixed_entities = ["director", "character", "portrayal", "award", "acting", "actor", "actress", "performance", "writer", "writing", "film", "movie", "gem", "screenplay", "script", "screen", "play", "screenwriter", "screenwriting", "story", "line", "storyline", "cast", "debut", "view", "work", "star", "oscar", "comedy", "drama", "thriller", "action", "horror", "face", "head", "jaw", "scene", "view", "fact", "appearance", "time", "emotion", "art", "music", "disappointment", "sense", "heart", "idea"]
separators = ["but", "although", "though", "otherwise", "however", "unless", "whereas", "despite"]

#viene utilizzato conceptnet per trovare i concetti simili/in relazione al term passato
def related_terms(term):
	query = "http://api.conceptnet.io/c/en/%s?offset=0&limit=100" % term
	obj = requests.get(query).json()

	terms = []
	for x in obj["edges"]:
		if x["rel"]["label"] == "RelatedTo" and x["end"]["language"] == "en" and x["start"]["label"] == term.replace("_", " "):
			terms.append(x["end"]["label"])
	#print(terms)
	#viene tornata una lista formata dai vari related terms trovati, un array per ogni term passato
	return list(set(terms))


def parse_separator(sentences, separator):
	phrases = []
	string = "%s.*," % separator
	prog = re.compile(string)
	for sent in sentences:
		if re.match(prog, sent):
			phrases.append(re.search(prog, sent).group(0))
			phrases.append(re.split(prog, sent)[1])
		else:
			phrases.extend(sent.split(separator))
	return phrases


def get_phrases_from_sentences(sentences):
	phrases = []
	for sent in sentences:
		phrases.extend(sent.split(";"))

	for separator in separators:
		phrases = parse_separator(phrases, separator)

	return phrases


def get_sentences(reviews):
	print("Sentences extraction")
	lower_case_reviews_sents = []
	tomatoes = []
	# this nlp is to process and analyze text using spaCy's functionalities (easier to analyze).
	nlp = en_core_web_md.load()

	for idx, (review, tomato) in enumerate(reviews):
		doc = nlp(review)
		sentences = [sent.text.lower().strip() for sent in doc.sents]
		#da sentences a phrases usando come splitter ; oppure i separators scritti sopra
		sentences = get_phrases_from_sentences(sentences)
		#salvo ogni frase come idx recensione dalla quale viene _ frase stessa
		sentences = [str(idx) + "_" + sent for sent in sentences]
		lower_case_reviews_sents.append(sentences)

		tomatoes.append(tomato)

	return lower_case_reviews_sents, tomatoes


def film_entities(reviews_url):
	film = reviews_url.split("m/")[2].split("/")[0].replace("_", " ")
	url = reviews_url.split("/reviews")[0]
	print("Extraction: direttore, writer, attori, entities varie")
	#print(url)
	#le entities sono i token formati dalle parole del film, dai nomi e cognomi di writer attori direttori
	
	listeveryone=rt_writers_actors_directors(url)
	#listeveryone = [directors[0],screenwriters[0],actors]
	director = listeveryone[0]
	writer = listeveryone[1]
	actors = listeveryone[2]


	entities = []
	film_tokens = film.lower().split()
	print("film tokens: %s" % film_tokens)
	#appendo a entities (vuoto) i film tokens
	entities.extend(film_tokens)
	print("sono dopo primo extend")
	#e appendo anche ogni entity direttore/writer/actor
	
	entities.extend(director.lower().split())
	entities.extend(writer.lower().split())
	print("sono prima del for")
	for x in actors:
		entities.extend(x.lower().split())

	print("sono dopo il for")
	#print(" ritorno entities, director, writer, actors")
	#print(entities)
	return set(entities), director, writer, actors


def ngrams_themes(lower_case_reviews_sents, entities):
	nlp = en_core_web_md.load()
	grams = []
	nouns = []

	for review in lower_case_reviews_sents:
		for sent in review:
			doc = nlp(sent)
			doc = [token for token in doc if not token.is_punct]
			
			lemmatized_doc = []

			for token in doc:
				if token.text not in entities:
					if token.pos_ == "NOUN":
						nouns.append(token.lemma_)
				lemmatized_doc.append(token.lemma_)

			grams.extend(list(ngrams(lemmatized_doc, 1)))
			grams.extend(list(ngrams(lemmatized_doc, 2)))
			grams.extend(list(ngrams(lemmatized_doc, 3)))


	free_grams = []
	for ngram in grams:
		if len(set(ngram).intersection(stop_grams)) == 0 and len(set(ngram).intersection(entities)) == 0:
			free_grams.append(ngram)

	selected_ngrams = []

	for noun in nouns:
		for ngram in free_grams:
			if noun in [x for x in ngram]:
				selected_ngrams.append(ngram)

	selected_ngrams = list(set(selected_ngrams))
	return selected_ngrams


def themes(selected_ngrams, entities):
	nlp = en_core_web_md.load()
	# ps = PorterStemmer()

	concepts_dict = dict()
	for ngram in selected_ngrams:
		concept = "_".join(ngram)
		terms = related_terms(concept)
		time.sleep(0.5)

		for term in terms:
			doc = nlp(term)

			if doc[0].pos_ == "NOUN" and term not in entities:
				if term not in concepts_dict.keys():
					concepts_dict[term] = []
				concepts_dict[term].append(ngram)

	return concepts_dict


if __name__ == "__main__":
	#print(related_terms("sun"))
	print (related_terms("coming_of_age"))
	#print (related_terms("island"))
	#print (related_terms("conformist"))



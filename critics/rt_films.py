from concurrent.futures import ProcessPoolExecutor
import requests
import math
from multiprocessing import cpu_count
from films_and_themes import films
from films_and_themes import movie_selected_themes
from rt_data import rt_top_critics_reviews_tomatoes
from rt_data import rt_top_critics_score
from rt_scraping import rt_box_office
from rt_scraping import rt_top_movies
from sentiment import polarity_subjectivity
from semantics_dfquad import strengths_dfquad
from semantics_energy_gen import strengths_energy_unique
from semantics_energy_pref import strengths_energy_weights_extended
from semantics_energy_pref import strengths_energy_attacks_extended
from semantics_dfquad_gen import strengths_dfquad_unique
from semantics_dfquad_pref import strengths_dfquad_weights_extended
from semantics_dfquad_pref import strengths_dfquad_attacks_extended
from semantics_quad import strengths_quad
from semantics_quad_gen import strengths_quad_unique
from semantics_quad_pref import strengths_quad_weights_extended
from semantics_quad_pref import strengths_quad_attacks_extended
from semantics_euler import strengths_euler
from semantics_euler_gen import strengths_euler_unique
from semantics_euler_pref import strengths_euler_weights_extended
from semantics_euler_pref import strengths_euler_attacks_extended
from compute_score import augment
from compute_score import unique_critics_score
from comparison_preferences import comparison_strengths
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
import copy
THREADS = cpu_count() - 2

main_topics = dict()
main_topics["film"] = ["film", "movie", "work"]
main_topics["director"] = ["director"]
main_topics["writer"] = ["writer", "writing", "screenwriter", "screenplay", "screenwriting", "storyline", "script", "character"]
main_topics["acting"] = ["acting", "cast", "portrayal", "performance"]
main_topics["themes"] = []




def extract_sentences_for_themes(film_title, topic_entities_dict, sent, polarity):
	for tuple_theme in movie_selected_themes[film_title]:
		value = tuple_theme[1]
		if find_whole_word(' '.join(str(i) for i in value))(sent) is not None or find_whole_word('-'.join(str(i) for i in value))(sent) is not None:
			topic_entities_dict["themes"]["entities"][movie_selected_themes[film_title][0]]["args"].append((sent, polarity))
			break

	return topic_entities_dict


def find_whole_word(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def decide_arg_vote_topic(topic_entities_dict, key, sent, polarity):
	for value in main_topics[key]:
		#itero le parole simili a quella della chiave richiesta
		if find_whole_word(value)(sent) is not None:
			#se almeno c'è una corrispondenza allora appendo
			topic_entities_dict[key]["args"].append((sent, polarity))
			break
	return topic_entities_dict


def decide_arg_vote_entity(topic_entities_dict, key, ent, sent, polarity):
	#print("decido arg vote entity")
	topic_entities_dict[key]["entities"][ent]["args"].append((sent, polarity))
	return topic_entities_dict


def extract_sentences_for_topic_entities(director, writer, actors, lower_case_reviews_sents, film_title):
	print("Phrases are being associated with the various keys")
	#topics è lista di tutti i vocaboli simili a director, writing.. film.. (accorpamento dei vari main_topics sopra)
	topics = list(chain(*main_topics.values()))
	assert set(topics) < set(fixed_entities)

	topic_entities_dict = dict()
	for k in main_topics.keys():
		topic_entities_dict[k] = dict()
		topic_entities_dict[k]["args"] = []

	#una volta creata struttura array (che poi farà il json), creo un ulteriore sottoarray per ogni entity di ogni key, sulla base di cosa ho trovato analizzando l'html
	topic_entities_dict["director"]["entities"] = dict()
	for x in director:
		#print("sto ciclando i direttori, %s e creo gli array" % director)
		topic_entities_dict["director"]["entities"][x] = dict()
		topic_entities_dict["director"]["entities"][x]["args"] = []

	topic_entities_dict["writer"]["entities"] = dict()
	for x in writer:
		topic_entities_dict["writer"]["entities"][x] = dict()
		topic_entities_dict["writer"]["entities"][x]["args"] = []

	topic_entities_dict["acting"]["entities"] = dict()
	for x in actors:
		topic_entities_dict["acting"]["entities"][x] = dict()
		topic_entities_dict["acting"]["entities"][x]["args"] = []

	topic_entities_dict["themes"]["entities"] = dict()
	if film_title in movie_selected_themes.keys():
		topic_entities_dict["themes"]["entities"][movie_selected_themes[film_title][0]] = dict()
		topic_entities_dict["themes"]["entities"][movie_selected_themes[film_title][0]]["args"] = []

	#una volta creata struttura dei vari array, ciclo le recensioni, di ogni recensione ciclo le frasi, e se la frase è abbastanza lunga, allora ne calcolo polarità e neutralità. Poi per ogni istanza di direttore/writer/actor/theme (ex. Angelina Jolie), controllo se la frase contiene parti di una certa istanza. Se sì associo frase ad istanza, altrimenti alla chiave padre
	print("Iterating every review with associated idx and every phrase with that idx")
	for review in lower_case_reviews_sents:	
		for sent in review:
			if len(sent) > 25:
				#neutralità è quanto è neutrale la analisi (>0 )
				#polarità è quanto è positivo (>0) /quanto negativo (<0)
				polarity, neutrality = polarity_subjectivity(sent)
				director_entity_seen = False
				writer_entity_seen = False
				actor_entity_seen = False
				film_entity_seen = False
				#neutrality threshold (se > 0.8 ignoriamo)
				if neutrality < 0.8:
					for ent in director:
						ent_split = ent.lower().replace("'s", " ").split()
						if len(ent_split) > 1:
							ent_split = ent_split[1:]
							ent_split = [x for x in ent_split if '.' not in x] # discard initials
						#print("controllo se ogni ent_split sia in sent, se sì salvo in ent_appearance")
						ent_appearance = any([find_whole_word(x)(sent) is not None for x in ent_split])
						if ent_appearance:
							
							#se c'è, allora la associo a quella istanza di quella key (una istanza di direttore)
							topic_entities_dict = decide_arg_vote_entity(topic_entities_dict, "director", ent, sent, polarity)
							director_entity_seen = True
							#print("director_entity_seen a true")
							break # so the same sentence does not appear twice

					if not director_entity_seen:
						#se nessuna istanza di direttore è stata trovata nella sent, allora controllo se associabile a key director generica
						
						#print("director_entity_seen rimasto a false")
						topic_entities_dict = decide_arg_vote_topic(topic_entities_dict, "director", sent, polarity)
						#print(topic_entities_dict)


					for ent in writer:
						if ent not in director:
							ent_split = ent.lower().replace("'s", " ").split()

							if len(ent_split) > 1:
								ent_split = ent_split[1:]
								ent_split = [x for x in ent_split if '.' not in x] # discard initials

							ent_appearance = any([find_whole_word(x)(sent) is not None for x in ent_split])
							if ent_appearance:
								topic_entities_dict = decide_arg_vote_entity(topic_entities_dict, "writer", ent, sent, polarity)
								writer_entity_seen = True
								break # so the same sentence does not appear twice

					if not writer_entity_seen:
						topic_entities_dict = decide_arg_vote_topic(topic_entities_dict, "writer", sent, polarity)

					if "??" in actors:
						actors.remove("??") # https://www.rottentomatoes.com/celebrity/_31
					for ent in actors:
						ent_split = ent.lower().replace("'s", " ").split()

						if len(ent_split) > 1:
							ent_split = ent_split[1:]
							ent_split = [x for x in ent_split if '.' not in x] # discard initials

						ent_appearance = any([find_whole_word(x)(sent) is not None for x in ent_split])
						if ent_appearance:
							topic_entities_dict = decide_arg_vote_entity(topic_entities_dict, "acting", ent, sent, polarity)
							actor_entity_seen = True
							break # so the same sentence does not appear twice

					if not actor_entity_seen:
						topic_entities_dict = decide_arg_vote_topic(topic_entities_dict, "acting", sent, polarity)


					#se la frase non è associabile a nessun direttore, scrittore o attore, allora la associo a film
					if not director_entity_seen and not writer_entity_seen and not actor_entity_seen:
						#print("not director_entity_seen and not writer_entity_seen and not actor_entity_seen")
						topic_entities_dict = decide_arg_vote_topic(topic_entities_dict, "film", sent, polarity)
						#print("topic_entities_dict post decide arg vote topic")
						#print(topic_entities_dict)
						if film_title[:-5] in sent and not any([find_whole_word(x)(sent) is not None for x in main_topics["film"]]):
							#print("film_title[:-5] in sent and not any([find_whole_word(x)(sent) is not None for x in main_topics[film]])")
							topic_entities_dict["film"]["args"].append((sent, polarity))

				if film_title in movie_selected_themes.keys():
					topic_entities_dict = extract_sentences_for_themes(film_title, topic_entities_dict, sent, polarity)
	#print("stampo il risultato")
	#print(topic_entities_dict)
	print("Phrases have been associated.")
	return topic_entities_dict


def fetch_themes(film_title, lower_case_reviews_sents, entities):
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	#data_file = "RT/themes_pkl/"+film_title+"_themes"+".pkl"
	data_file="./themes_pkl/"+film_title+"_themes"+".pkl"
	#se esiste già file con i vari temi associato al film, lo leggo, se no lo creo
	if os.path.isfile(data_file):
		selected_themes = pickle.load(open(data_file, "rb"))

	else:
		selected_ngrams = ngrams_themes(lower_case_reviews_sents, entities)
		concepts_dict = themes(selected_ngrams, entities)
		selected_themes = sorted(concepts_dict.items(), key = lambda item : len(item[1]), reverse=True)[:25]

		with open(data_file, 'wb') as f:
			pickle.dump(selected_themes, f)


def threshold_af(topic_entities_dict):
	updated_topic_entities_dict = dict()
	#threshold della polarità a 0.6 dopo che era stata applicata anche quella di neutralità a 0.8. Quella scritta nel paper è +- 0.6 polarità.
	for key in topic_entities_dict.keys():
		updated_topic_entities_dict[key] = dict()
		updated_topic_entities_dict[key]["unique_args"] = []
		for (arg, polarity) in topic_entities_dict[key]["unique_args"]:
			if abs(float(polarity)) > 0.6:
				updated_topic_entities_dict[key]["unique_args"].append((arg, polarity))

		if "entities" in topic_entities_dict[key].keys():
			updated_topic_entities_dict[key]["entities"] = dict()
			for ent in topic_entities_dict[key]["entities"].keys():
				updated_topic_entities_dict[key]["entities"][ent] = dict()
				updated_topic_entities_dict[key]["entities"][ent]["unique_args"] = []
				for (ent_arg, ent_polarity) in topic_entities_dict[key]["entities"][ent]["unique_args"]:
					if abs(float(ent_polarity)) > 0.6:
						updated_topic_entities_dict[key]["entities"][ent]["unique_args"].append((ent_arg, ent_polarity))

	
	return updated_topic_entities_dict


def process_url_pref(url):
	
	print("ho passato questo url e vado a creare o leggere il file AF"+url)
	film_title = url.split("m/")[2].split("/")[0].replace("_", " ")
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	#af_file="./af/original/"+film_title+".json"
	af_file="./af/2023/"+film_title+".json"
	
	#lista zippata ("testo recensione", 1/0)
	top_critics_reviews_tomatoes = rt_top_critics_reviews_tomatoes(url)
	#numero recensioni (solo fino al load more - tendenzialmente sono 20)
	nr_critics = len(top_critics_reviews_tomatoes)

	if nr_critics > 0:
		#splitto l'url e passo dai top critics all'url normale del film, principale, per passarlo a rt_top_critics_score che semplicemente mi dà il tomatometerscore
		rt_score = rt_top_critics_score(url.split("reviews")[0])
		#print("ho preso le recensioni principali (recen, 1/0)  e ho calcolato rt score")
		print("RT score: %d" % rt_score)
		print("Film title: %s" % film_title)

		if not os.path.isfile(af_file):
			print("file not found (AF FILE)")

			#se non c'è già file dell'AF, allora viene creato
			#da ogni recensione estraggo prima sentences e poi phrases, e ogni phrases in lower_case_reviews_sents è salvata come idxRece dalla quale proviene _ frase stessa. In più in tomatoes ci sono i vari rotten/tomato (uno per ogni Rece)
			lower_case_reviews_sents, tomatoes = get_sentences(top_critics_reviews_tomatoes)
			#estraggo entities varie, direttore, writer, actors a partire da url
			entities, director, writer, actors = film_entities(url)
			#print("entities prese dopo estrazione sentences: %s"% entities)
			#al momento è sempre a yes
			if with_themes == "y":
				fetch_themes(film_title, lower_case_reviews_sents, entities)

			#qui associo le frasi a director, writer, actors, entities 
			topic_entities_dict = extract_sentences_for_topic_entities(director, writer, actors, lower_case_reviews_sents, film_title)

			#qui traformo gli args in unique args e ESTENDO tutte le recensioni delle istanze di entities ai loro parent (da [key][entities][entity][unique args] a  [key][unique args] ex. rece su attrice A viene messa anche negli unique args di acting)
			#print("Stampo topic entities dict prima unique: %s" %topic_entities_dict)
			topic_entities_dict = unique_critics_score(topic_entities_dict)
			#elimino frasi che hanno polarità p : -0.6<p<0.6
			topic_entities_dict = threshold_af(topic_entities_dict)
			
			#qui AUGMENTO nel movie stesso le reviews delle sue keys non già presenti nel suo unique args. A ogni sottostruttura tolgo i rimanenti args
			topic_entities_dict = augment(topic_entities_dict, nr_critics)
			#print("Post augument: %s" % topic_entities_dict)
			#print("topic entities dopo augmentation: %s" % topic_entities_dict)
			print("Creating AF file")
			with open(af_file, 'w') as f:
				json.dump(topic_entities_dict, f, ensure_ascii=False, indent=4)

		else:
			print ("file found - computing")
			print("prendo dal file AF le topic entities dict e le passo al metodo della strenght scelta")
			#apre l'AF file json e prende i topic_entities_dict, ergo le varie strutture dell'af
			topic_entities_dict = json.loads(open(af_file).read())
			# print("topic_entities_dict")
			# print(topic_entities_dict)
			#print(film_title)
			#print(rt_score)
		print (film_title)
		print (rt_score)

		#strengths_tipostrength_unique è copia di strengths_tipostrength ma con "unique_args" anzichè "args"
		
		return film_title, rt_score, topic_entities_dict, nr_critics

	else:
		return None
	
def readAFfile(topic_entities_dict, nr_critics, semantics):
	answerPreferences = input("Do you want to express preferences between items? y/n: ")
	booleanPref= False
	
	if(answerPreferences == "y"):
		booleanPref = True
		list_entities={}
		list_keys={}
	
		i=0
		for key in topic_entities_dict.keys():
			if key != "film":
				#salvo in list_keys i vari acting, directing etc
				list_keys[i]=key
				i=i+1
				
				if key=="acting" or key=="themes":
					#solo per acting e themes ho anche una lista specifica per i children nodes
					list_entities[key] = {}
					
					n=0
					for entity in topic_entities_dict[key]["entities"]:
						
						if topic_entities_dict[key]["entities"][entity]["unique_args"]:
							list_entities[key][n]=entity
							n=n+1
		
		listAnsPref={}
		#salvo in listAnsPref[gen] le preferenze tra acting/writer etc
		generalPreference = input("Express a preference between "+ str(list_keys)+", using the related number, like 0>1 if you prefer "+ str(list_keys[0])+ " to "+str(list_keys[1])+ ". Otherwise press enter: ")
		listAnsPref["general"]= generalPreference
		#e in listAnsPref[acting] e/o listAnsPref[themes] le preferenze sui children nodes (se >=2)
		for entity in list_entities:
			listAnsPref[entity]=""
			#se la entity ha almeno 2 istanze (2 attori o 2 temi)
			if len(list_entities[entity])>=2:
				pref = input("Express a preference between "+ str(list_entities[entity])+", using the related number, like 0>1 if you prefer "+ str(list_entities[entity][0])+ " to "
				+str(list_entities[entity][1])+". Otherwise press enter: ")
				listAnsPref[entity]=pref

		print(listAnsPref)
		#se utente ha sempre cliccato invio allora non ha espresso preferenze e uso metodo standard
		if all(value == '' for value in listAnsPref.values()):
			booleanPref = False
			if semantics == "dfquad":
				film_score = strengths_dfquad_unique(topic_entities_dict, nr_critics)
			elif semantics == "quad":
				film_score = strengths_quad_unique(topic_entities_dict, nr_critics)
			elif semantics == "euler":
				film_score = strengths_euler_unique(topic_entities_dict, nr_critics)
			else:
				film_score == strengths_energy_unique(topic_entities_dict, nr_critics)

		else:
			#altrimenti passo le varie liste: keys generali, keys entities, e le preferenze effettive
			booleanPref= True
			if semantics == "dfquad":
				film_score = strengths_dfquad_weights(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities)
			
			elif semantics == "quad":
				film_score = strengths_quad_weights(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities)
			elif semantics == "euler":
				film_score = strengths_euler_pref(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities)
			
	elif (answerPreferences == "n"):
		booleanPref = False
		if semantics == "dfquad":
			film_score = strengths_dfquad_unique(topic_entities_dict, nr_critics)
		elif semantics == "quad":
			film_score = strengths_quad_unique(topic_entities_dict, nr_critics)
		elif semantics == "euler":
			film_score = strengths_euler_unique(topic_entities_dict, nr_critics)
		else:
			film_score = strengths_energy_unique(topic_entities_dict, nr_critics)

	return film_score, booleanPref

def readAFfileExtended(topic_entities_dict, nr_critics, semantics):
	answerPreferences = input("Do you want to express preferences between items? y/n: ")
	booleanPref= False
	
	if(answerPreferences == "y"):
		booleanPref = True
		list_entities={}
		list_keys={}
		list_entities_complete={'acting':[], 'themes':[]}
		i=0
		for key in topic_entities_dict.keys():
			if key != "film":
				#salvo in list_keys i vari acting, directing etc
				list_keys[i]=key
				i=i+1
				if key=="acting" or key=="themes":
					#solo per acting e themes ho anche una lista specifica per i children nodes
					list_entities[key] = {}
					
					n1=0
					n2=0
					for entity in topic_entities_dict[key]["entities"]:
						list_entities_complete[key].append(entity)
						n2= n2+1
						if topic_entities_dict[key]["entities"][entity]["unique_args"]:
							list_entities[key][n1]=entity
							n1=n1+1

		#lista per salvare preferenze
		listAnsPref={}
		#max numero preferenze esprimibili
		maxCoupleKeys= int(math.factorial(len(list_keys)) / (2*math.factorial(len(list_keys)-2)))
		n1=0
		listAnsPref["keysPreferences"]=[]
		listAnsPref["entities"]={'acting': [], 'themes': []}
		while n1!= maxCoupleKeys:
			generalPreference = input("Express a preference between "+ str(list_keys)+", using the related number, like 0>1 if you prefer "+ str(list_keys[0])+ " to "+str(list_keys[1])+ ". Otherwise press enter: ")
			listAnsPref["keysPreferences"].append(generalPreference)
			if (n1+1) != maxCoupleKeys:
				anotherPref = input("Do you want to add another preference? y/n: ")
				if (anotherPref == 'y'):
					n1=n1+1
				else:
					break
			else:
				break


		
		for entity in list_entities:
				#se la entity ha almeno 2 istanze (2 attori o 2 temi)
				if len(list_entities[entity])>=2:
					n1=0
					maxCoupleEntity= int(math.factorial(len(list_entities[entity])) / (2*math.factorial(len(list_entities[entity])-2)))
					while n1!= maxCoupleEntity:
						prefEntity = input("Express a preference between "+ str(list_entities[entity])+", using the related number, like 0>1 if you prefer "+ str(list_entities[entity][0])+ " to "
						+str(list_entities[entity][1])+". Otherwise press enter: ")
						listAnsPref["entities"][entity].append(prefEntity)
						if (n1+1) != maxCoupleEntity:
							anotherPref = input("Do you want to add another preference? y/n: ")
							if (anotherPref == 'y'):
								n1=n1+1
							else:
								break
						else:
							break

			

		print(listAnsPref)
		#se utente ha sempre cliccato invio allora non ha espresso preferenze e uso metodo standard
		listAnsPrefOrig = copy.deepcopy(listAnsPref)
		if all(value == '' for value in listAnsPref.values()):
			booleanPref = False
			if semantics == "dfquad":
				film_score = strengths_dfquad_unique(topic_entities_dict, nr_critics)
			elif semantics == "quad":
				film_score = strengths_quad_unique(topic_entities_dict, nr_critics)
			elif semantics == "euler":
				film_score = strengths_euler_unique(topic_entities_dict, nr_critics)
			elif semantics == "energy": 
				film_score == strengths_energy_unique(topic_entities_dict, nr_critics)
			else:
				film_score = [strengths_dfquad_unique(topic_entities_dict, nr_critics),strengths_quad_unique(topic_entities_dict, nr_critics),strengths_euler_unique(topic_entities_dict, nr_critics),strengths_energy_unique(topic_entities_dict, nr_critics)]

		else:
			#altrimenti passo le varie liste: keys generali, keys entities, e le preferenze effettive
			booleanPref= True
			preferenceMethod = input("Do you want preferences as weights or attacks? w/a:")
			if(preferenceMethod == 'w'):
				if semantics == "dfquad":
					film_score = strengths_dfquad_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
					
				
				elif semantics == "quad":
					film_score = strengths_quad_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
					
				elif semantics == "euler":
					film_score = strengths_euler_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
					
				elif semantics == "energy":
					film_score = strengths_energy_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
					
				else:
					
					film_score_dfquad = strengths_dfquad_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)
					
					film_score_quad = strengths_quad_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)

					film_score_euler = strengths_euler_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)

					film_score_energy = strengths_energy_weights_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)
					film_score = [film_score_dfquad, film_score_quad, film_score_euler, film_score_energy]

			elif(preferenceMethod == 'a'):
				if semantics == "dfquad":
					film_score = strengths_dfquad_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
				
				elif semantics == "quad":
					film_score = strengths_quad_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
				elif semantics == "euler":
					film_score = strengths_euler_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
				elif semantics == "energy":
					film_score = strengths_energy_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					
				else:
					film_score_dfquad = strengths_dfquad_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)
					film_score_quad = strengths_quad_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)
					film_score_euler = strengths_euler_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)
					film_score_energy = strengths_energy_attacks_extended(topic_entities_dict,nr_critics, listAnsPref, list_keys, list_entities, list_entities_complete)
					listAnsPref =copy.deepcopy(listAnsPrefOrig)
					film_score = [film_score_dfquad, film_score_quad, film_score_euler, film_score_energy]

				
	elif (answerPreferences == "n"):
		booleanPref = False
		if semantics == "dfquad":
			film_score = strengths_dfquad_unique(topic_entities_dict, nr_critics)
		elif semantics == "quad":
			film_score = strengths_quad_unique(topic_entities_dict, nr_critics)
		elif semantics == "euler":
			film_score = strengths_euler_unique(topic_entities_dict, nr_critics)
		elif semantics == "energy":
			film_score = strengths_energy_unique(topic_entities_dict, nr_critics)
		else:
			film_score = [strengths_dfquad_unique(topic_entities_dict, nr_critics),strengths_quad_unique(topic_entities_dict, nr_critics),strengths_euler_unique(topic_entities_dict, nr_critics),strengths_energy_unique(topic_entities_dict, nr_critics)]

	return film_score, booleanPref



def process_url_nlp(url, model, tokenizer):
	#model = load_model("critics/nlp/concat_False_lstm_dropout_after_lstm.h5")
	#tokenizer = pickle.load(open("critics/nlp/deep_tokenizer.pkl", "rb"))
	film_title = url.split("m/")[2].split("/")[0].replace("_", " ")
	
	#af_file = "RT/af/all_sent/"+film_title+"_af"+".json"
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	af_file="./af/original/"+film_title+".json"
	
	print("sono in process_url")
	print ("af_file %s" % af_file)
	#af_nlp_file = "RT/af/all_nlp_sent_relation/"+film_title+"_nlp_af"+".json"
	af_nlp_file="./af/all_nlp_sent_relation/"+film_title+"_nlp_af"+".json"


	top_critics_reviews_tomatoes = rt_top_critics_reviews_tomatoes(url)
	nr_critics = len(top_critics_reviews_tomatoes)
	if nr_critics > 0:
		rt_score = rt_top_critics_score(url.split("reviews")[0])

		if not os.path.isfile(af_nlp_file):
			movie_af = json.loads(open(af_file).read())
			topic_entities_dict = process_af(movie_af, tokenizer, model)

			topic_entities_dict = unique_critics_score(topic_entities_dict)
			topic_entities_dict = threshold_af(topic_entities_dict)
			topic_entities_dict = augment(topic_entities_dict, nr_critics)

			with open(af_nlp_file, 'x') as f:
				json.dump(topic_entities_dict, f, ensure_ascii=False, indent=4)
			
		else:
			topic_entities_dict = json.loads(open(af_nlp_file).read())

		print (film_title)
		print (rt_score)

		if semantics == "dfquad":
			film_score = strengths_dfquad(topic_entities_dict, nr_critics)
		elif semantics == "quad":
			film_score = strengths_quad(topic_entities_dict, nr_critics)
		elif semantics == "euler":
			film_score = strengths_euler(topic_entities_dict, nr_critics)

		print (film_score)

		return (rt_score, film_score, film_title)
	else:
		return None

#check if URL exists in the website rotten tomato
def checkExistingUrl(url):
	try:
			response = requests.get(url)
			response.raise_for_status()
			print(f"The URL {url} exists.")
			return True
	except requests.exceptions.RequestException:
			return False
	
#once URL exists, then the info are extracted from the html
def useUrl(url, method, semantics):
	
	if method == "sent":
		#here we retrieve film title, rt score, nr critics, and we create a new AF file/check that there's already an AF file
		film_title, rt_score, topic_entities_dict, nr_critics = process_url_pref(url)
		#here we read the AF file and we ask the user if he/she wants to add preferences on the BASIS of the AF file structure
		film_score, booleanPref = readAFfileExtended(topic_entities_dict, nr_critics, semantics)
		#here we retrieve the final results: rt score, strength score, film title
		results.append((rt_score, film_score, film_title))
	

		#we save the results on a json file on the basis of the presence of preferences
		#print(booleanPref)
		if not isinstance(film_score, list):
			if booleanPref:
				
				with jsonlines.open(('./preferences/all_%s_%s_sent_pref.jsonl' % (method, semantics)), mode='a') as writer:
					for x in results:
						if x != None:
							writer.write(x)
				#comparison_strengths(film_title, semantics, contentPreferences, film_score)
			else:
				with jsonlines.open(('./all_%s_%s_sent.jsonl' % (method, semantics)), mode='a') as writer:
					for x in results:
						if x != None:
							writer.write(x)
		else:
				print(results)
				if booleanPref:
					
					with jsonlines.open(('./preferences/all_%s_allSemantics_sent_pref.jsonl' % (method)), mode='a') as writer:
						for x in results:
							if x != None:
								writer.write(x)
					#comparison_strengths(film_title, semantics, contentPreferences, film_score)
				else:
					with jsonlines.open(('./all_%s_allSemantics_sent.jsonl' % (method)), mode='a') as writer:
						for x in results:
							if x != None:
								writer.write(x)
	elif method == "nlp":
		print("Please use method sent")

	

if __name__ == "__main__":
	booleanPreferences = False
	contentPreferences = ""
	semantics = input("semantics? dfquad/quad/euler/energy ")
	#with_themes = input("with themes? y/n ")
	with_themes="y"
	method = input("sent/nlp? ")
	
	choice= input("Do you want to search a specific movie or to analyze movies chosen by the system? specific/chosen: ")
	if choice == "chosen":
		#this links don't work, go to else
		if not os.path.isfile("rt_bo_films.pkl"):
			# current year
			for i in range(34):
				bo_url = "https://www.rottentomatoes.com/browse/box-office/?rank_id=%d&country=us" % i
				films.extend(rt_box_office(bo_url))

			# years 2017,2016,2015
			for i in range(34, 190):
				bo_url = "https://www.rottentomatoes.com/browse/box-office/?rank_id=%d&country=us" % i
				films.extend(rt_box_office(bo_url))

			films.extend(rt_top_movies("https://www.rottentomatoes.com/top/bestofrt/"))
			films = list(set(films))

			with open("rt_bo_films.pkl", 'wb') as f:
				pickle.dump(films, f)
		else:
			films = pickle.load(open("rt_bo_films.pkl", "rb"))
		
		#this is the nlp part that doesnt work
		# with ProcessPoolExecutor(max_workers=THREADS) as executor:
		# 	if method == "sent":
		# 		results = executor.map(process_url, [url for url in films])
		# 	elif method == "nlp":
		# 		results = executor.map(process_url_nlp, [url for url in films])

		#model = load_model("./nlp/concat_False_lstm_dropout_after_lstm.h5")
		#tokenizer = pickle.load(open("./nlp/deep_tokenizer.pkl", "rb"))
		results = []
	
		for idx, url in enumerate(films):
			#idx < 22 for a problem of rt file
			if(idx<22):
				print ("%d/%d" % (idx, len(films)))
				#here I don't call checkUrl because we already know that until idx==22 the URl work (2023)
				useUrl(url, method, semantics)
	
	
	elif choice == "specific":
		whichMovie= input("Insert name of movie (example: oppenheimer): ")
		whichMovieYear = input("Insert the year in which the movie was made (example: 2023): ")
		results=[]
		whichMovie=whichMovie.split()
		whichMovie = "_".join(word.lower() for word in whichMovie)
		
		#some movies have a unique title, then their URLs just contain their title, while others have a title that has been already used for other movies, so their URLs also contain the year of the movie
		url1= "https://www.rottentomatoes.com/m/"+whichMovie+"_"+whichMovieYear+"/reviews?type=top_critics"
		url2 = "https://www.rottentomatoes.com/m/"+whichMovie+"/reviews?type=top_critics"
		url =""
		booleanUrl1=checkExistingUrl(url1)
		#if the url with film title and year exists (it's the most common option), we use the URL, otherwise we check for the URL without year
		if booleanUrl1:
			useUrl(url1, method, semantics)
		else:
			print("Since %s %s hasn't been found, we search for a movie called %s without a specific year" % (whichMovie, whichMovieYear, whichMovie))
			booleanUrl2=checkExistingUrl(url2)
			if booleanUrl2:
				useUrl(url2, method, semantics)
			else:
				print("Sorry, the URL hasn't been found")
	
	'''
	#per toy example
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	#af_file="./af/original/"+film_title+".json"
	af_file="./af/2023/"+"toyExample"+".json"
	topic_entities_dict = json.loads(open(af_file).read())
	nr_critics = 90 
	results=[]
	#ci sono attualmente 61 reviews, sono da intendersi come pezzi di frase, quindi suppongo ci siano circa 90 reviews (di solito con 20 critics se ne hanno 12/13)
	film_score, booleanPref = readAFfileExtended(topic_entities_dict, nr_critics, semantics)
	results.append(("RT score", film_score, "Toy Example 24"))
	if booleanPref:
			with jsonlines.open(('./preferences/all_%s_%s_sent_pref.jsonl' % (method, semantics)), mode='a') as writer:
				for x in results:
					if x != None:
						writer.write(x)
			#comparison_strengths(film_title, semantics, contentPreferences, film_score)
	else:
		with jsonlines.open(('./all_%s_%s_sent.jsonl' % (method, semantics)), mode='a') as writer:
			for x in results:
				if x != None:
					writer.write(x)
	
	'''
		
			
		


	

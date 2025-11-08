from functools import reduce
from operator import mul
import json
import jsonlines
import re
import os
import pickle


def strength_aggregation_att(base_score, arg_scores):
	length = len(arg_scores)
	if length == 0:
		return None
	prod = [1-score for score in arg_scores]
	return base_score * reduce(mul, prod, 1)


def strength_aggregation_sup(base_score, arg_scores):
	length = len(arg_scores)
	if length == 0:
		return None
	prod = [1-score for score in arg_scores]
	return 1 - (1-base_score) * reduce(mul, prod, 1)
	

def combination_function(base_score, att, supp):
	if att == None and supp == None:
		return base_score
	elif att == None and supp != None:
		return supp
	elif supp == None and att != None:
		return att
	else:
		return (att+supp)/2


#questa è la funzione che viene chiamata in rt_films e al quale vengono passati i "pezzi" del file AF di uno specifico film e numero di critiche (che serve al denominatore)
def strengths_quad(topic_entities_dict, nr_critics):
	nr_votes = dict()

	print ("numero critici: %s" % str(nr_critics))
	#print("stampo le chiavi di topic entities dict")
	#print(topic_entities_dict.keys())
	#dict_keys(['film', 'themes', 'director', 'acting', 'writer'])

	#quindi immagino sia un albero che ha come item "film", "sibling nodes: themes, director, acting, writer"
	feature_strengths = dict()
	for key in topic_entities_dict.keys():
		if key == "film":
			continue
			#non vengono considerati eventuali voti dati direttamente al film
		if key == "writer" or key == "director":
			
			pos_votes = 0
			neg_votes = 0
			
			for (text, polarity) in topic_entities_dict[key]["args"]:
				#guardo polarità degli argomenti dentro "args" generico, non dentro le singole entities writer/director
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1
			
			feature_strengths[key] = float(abs(pos_votes - neg_votes)) / nr_critics

			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes
			nr_votes[key]["neg"] = neg_votes


		elif key == "acting":
			pos_votes_act=0
			neg_votes_act=0
			#args generici
			for (text,polarity) in topic_entities_dict[key]["args"]:
				#se polarità (ottenuta automaticamente) è >0 allora è voto positivo
				if float(polarity)>0:
					pos_votes_act +=1
				else:
					neg_votes_act +=1
			
			#base score calcolato come abs (numero voti positivi totali-negativi totali)/nr critics
			base_score_act = float(abs(pos_votes_act - neg_votes_act))/nr_critics
			supps= []
			atts=[]
			#e poi singoli
			for actor in topic_entities_dict[key]["entities"]:
				pos_votes = 0
				neg_votes = 0
				#if topic_entities_dict[key]["entities"][actor]["unique_args"]:
				if topic_entities_dict[key]["entities"][actor]["args"]:
					#for (text, polarity) in topic_entities_dict[key]["entities"][actor]["unique_args"]:
					for (text, polarity) in topic_entities_dict[key]["entities"][actor]["args"]:
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1

					ent_score = float(abs(pos_votes - neg_votes)) / nr_critics
					feature_strengths["acting_"+actor] = ent_score
					# print ("base_score_acting_%s %s" % (actor, str(ent_score)))

					#assegno supporti e attacchi tra entity (pos_votes, neg_votes) che sto valutando in questo ciclo (un certo attore), e il nodo acting parent (pos_votes_act, neg_votes_act)
					if pos_votes >= neg_votes and pos_votes_act >= neg_votes_act:
						#allora questo attore è un supporter che ha come base score "ent_score"
						supps.append(ent_score)
					elif pos_votes <= neg_votes and pos_votes_act <= neg_votes_act:
						supps.append(ent_score)
					elif neg_votes > pos_votes and pos_votes_act > neg_votes_act:
						atts.append(ent_score)
					elif neg_votes < pos_votes and pos_votes_act < neg_votes_act:
						atts.append(ent_score)

				nr_votes[actor] = dict()
				nr_votes[actor]["pos"] = pos_votes
				nr_votes[actor]["neg"] = neg_votes

			# print ("act_atts %s" % str(atts))
			# print ("act_supps %s" % str(supps))

			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes_act
			nr_votes[key]["neg"] = neg_votes_act
			#calcolo la strenght di acting
			feature_strengths[key] = combination_function(base_score_act, strength_aggregation_att(base_score_act, atts), strength_aggregation_sup(base_score_act, supps))
		else:
			# it's a theme
			pos_votes_theme = 0
			neg_votes_theme = 0
			#for (text, polarity) in topic_entities_dict["themes"]["unique_args"]:
			for (text, polarity) in topic_entities_dict["themes"]["args"]:
				if float(polarity) > 0:
					pos_votes_theme += 1
				else:
					neg_votes_theme += 1

			base_score_theme = float(abs(pos_votes_theme - neg_votes_theme)) / nr_critics

			# print ("base_score_theme %s" % str(base_score_theme))

			supps = []
			atts = []

			# HACK with one theme only
			pos_votes = 0
			neg_votes = 0
			if topic_entities_dict["themes"]["entities"]:
				ent = list(topic_entities_dict["themes"]["entities"].keys())[0]
				#for (text, polarity) in topic_entities_dict["themes"]["entities"][ent]["unique_args"]:
				for (text, polarity) in topic_entities_dict["themes"]["entities"][ent]["args"]:
					if float(polarity) > 0:
						pos_votes += 1
					else:
						neg_votes += 1

				ent_score = float(abs(pos_votes - neg_votes)) / nr_critics
				feature_strengths["theme_"+ent] = ent_score

				if pos_votes >= neg_votes and pos_votes_theme >= neg_votes_theme:
					supps.append(ent_score)
				elif pos_votes <= neg_votes and pos_votes_theme <= neg_votes_theme:
					supps.append(ent_score)
				elif neg_votes > pos_votes and pos_votes_theme > neg_votes_theme:
					atts.append(ent_score)
				elif neg_votes < pos_votes and pos_votes_theme < neg_votes_theme:
					atts.append(ent_score)


				nr_votes[ent] = dict()
				nr_votes[ent]["pos"] = pos_votes
				nr_votes[ent]["neg"] = neg_votes

			# print ("theme_atts %s" % str(atts))
			# print ("theme_supps %s" % str(supps))

			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes
			nr_votes[key]["neg"] = neg_votes

			feature_strengths[key] = combination_function(base_score_theme, strength_aggregation_att(base_score_theme, atts), strength_aggregation_sup(base_score_theme, supps))

	m_atts = []
	m_supps = []

	pos_votes_film = 0
	neg_votes_film = 0
	#for (text, polarity) in topic_entities_dict["film"]["unique_args"]:
	for (text, polarity) in topic_entities_dict["film"]["args"]:
		if float(polarity) > 0:
			pos_votes_film += 1
		else:
			neg_votes_film += 1

	for key in feature_strengths.keys():
		if "acting_" not in key and "theme_" not in key:
			pos_votes_key = nr_votes[key]["pos"]
			neg_votes_key = nr_votes[key]["neg"]
			if pos_votes_key > neg_votes_key:
				m_supps.append(feature_strengths[key])
			elif neg_votes_key > pos_votes_key:
				m_atts.append(feature_strengths[key])

	film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics

	# print ("film_base_score %s" % str(film_base_score))
	# print ("m_atts %s" % str(m_atts))
	# print ("m_supps %s" % str(m_supps))

	nr_votes["film"] = dict()
	nr_votes["film"]["pos"] = pos_votes_film
	nr_votes["film"]["neg"] = neg_votes_film

	feature_strengths["film"] = combination_function(film_base_score, strength_aggregation_att(film_base_score, m_atts), strength_aggregation_sup(film_base_score, m_supps))

	for key, v in feature_strengths.items():
		print ("%s %s" % (key, str(v)))

	# print (nr_votes)

	return feature_strengths["film"]*100

if __name__ == "__main__":
	film_title ="interstellar 2014" 
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	af_file="./af/original/"+film_title+".json"
	topic_entities_dict = json.loads(open(af_file).read())
	nr_critics = 20
	#printo la strength calcolata
	film_score = strengths_quad(topic_entities_dict, nr_critics)
	print(film_score)
from functools import reduce
from operator import mul
import json
import jsonlines
import re
import os
import pickle


def strength_aggregation(arg_scores):
	length = len(arg_scores)
	if length == 0:
		return 0
	else:
		return recursive_function(arg_scores)


def recursive_function(arg_scores):
	print("mi è stato passato per la recursive arg_scores " )
	print(arg_scores)
	prod = [1-score for score in arg_scores]
	return 1 - reduce(mul, prod, 1)


def combination_function(base_score, att, supp):
	print("ho passato base_score %.4f" %base_score)
	print("att")
	print(att)
	print("supp")
	print(supp)
	if att == supp:
		return base_score
	elif att > supp:
		return base_score - base_score*abs(supp-att)
	else:
		print("supp>att")
		print(base_score + (1-base_score)*abs(supp-att))
		return base_score + (1-base_score)*abs(supp-att)


def strengths_dfquad(topic_entities_dict, nr_critics):
	nr_votes = dict()
	
	#print ("critics %s" % str(nr_critics))

	#vado a prendere i voti polari sulle features
	feature_strengths = dict()
	for key in topic_entities_dict.keys():
		if key == "film":
			continue
		if key == "writer" or key == "director":
			pos_votes = 0
			neg_votes = 0
			#for (text, polarity) in topic_entities_dict[key]["unique_args"]:
			for (text, polarity) in topic_entities_dict[key]["args"]:
				print("sono nella key %s che ha degli args" % key)
				print("polarity %.4f"% float(polarity))
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1
			print("attualmente la key %s ha %d voti positivi" % (key,pos_votes))
			print("attualmente la key %s ha %d voti negativi" % (key,neg_votes))
			print ("%s_base_score %s" % (key, str(float(abs(pos_votes - neg_votes)) / nr_critics)))
			'''
			for writerOrDirector in topic_entities_dict[key]["entities"]:
				if topic_entities_dict[key]["entities"][writerOrDirector]["args"]:
					for (text, polarity) in topic_entities_dict[key]["entities"][writerOrDirector]["args"]:
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1
			
			'''
			#probabilmente qui si è presupposto che writer e director non hanno figli, quindi la strenght è uguale al base score
			feature_strengths[key] = float(abs(pos_votes - neg_votes)) / nr_critics
			

			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes
			nr_votes[key]["neg"] = neg_votes
			#print(nr_votes[key]["pos"])
			#print(nr_votes[key]["neg"])

		elif key == "acting":
			pos_votes_act = 0
			neg_votes_act = 0
			for (text, polarity) in topic_entities_dict[key]["args"]:
				print("sono in acting che ha degli args")
				if float(polarity) > 0:
					pos_votes_act += 1
				else:
					neg_votes_act += 1
			print("acting generico ha %d voti positivi" % pos_votes_act)
			print("acting generico ha %d voti negativi"% neg_votes_act)
			base_score_act = float(abs(pos_votes_act - neg_votes_act)) / nr_critics

			print ("base_score_act %s" % str(base_score_act))

			supps = []
			atts = []

			for actor in topic_entities_dict[key]["entities"]:
				print("sto ciclando un attore %s"% actor)
				pos_votes = 0
				neg_votes = 0
				if topic_entities_dict[key]["entities"][actor]["args"]:
					print("questo attore %s ha delle reviews" % actor)
					for (text, polarity) in topic_entities_dict[key]["entities"][actor]["args"]:
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1
					print("questo attore ha %d voti positiv" % pos_votes )
					print("questo attore ha %d voti negativi"% neg_votes )
					ent_score = float(abs(pos_votes - neg_votes)) / nr_critics
					feature_strengths["acting_"+actor] = ent_score
					print ("base_score_acting_%s %s" % (actor, str(ent_score)))

					#assegnamento supporti attacchi su base stessa polarità tra argomenti linkati o diversa polarità
					if pos_votes >= neg_votes and pos_votes_act >= neg_votes_act:
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
			print("stampo vettori atts e supps")
			print(atts)
			print(supps)
			print("calcolo la strength di acting combinando il suo base score, strength atts (subfeatures) e strength supps (subfeatures)")
			feature_strengths[key] = combination_function(base_score_act, strength_aggregation(atts), strength_aggregation(supps))
			print(feature_strengths[key])
		else:
			# it's a theme
			pos_votes_theme = 0
			neg_votes_theme = 0
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

			feature_strengths[key] = combination_function(base_score_theme, strength_aggregation(atts), strength_aggregation(supps))

	m_atts = []
	m_supps = []
	# qui guardo invece le recensioni sul film in generale
	pos_votes_film = 0
	neg_votes_film = 0
	for (text, polarity) in topic_entities_dict["film"]["args"]:
		print("sono negli args del film - che non ha entitites")
		if float(polarity) > 0:
			pos_votes_film += 1
		else:
			neg_votes_film += 1
	print("numero voti positivi film %d" % pos_votes_film)
	print("numero voti negativi film %d" % neg_votes_film)
	film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics
	print ("film_base_score %s" % str(film_base_score))

	for key in feature_strengths.keys():
		print(key)
		#se c'è almeno una delle due, l'and diventa falso, quindi qui sto prendendo i sibling diretti di movie, le features, escludendo le subfeatures eventuali
		if "acting_" not in key and "theme_" not in key:
			print("dentro if")
			pos_votes_key = nr_votes[key]["pos"]
			neg_votes_key = nr_votes[key]["neg"]
			print("pos_votes_key %d, neg_votes_key %d" % (pos_votes_key, neg_votes_key))
			if pos_votes_key > neg_votes_key:
				m_supps.append(feature_strengths[key])
			elif neg_votes_key > pos_votes_key:
				m_atts.append(feature_strengths[key])

	
	# print ("m_atts %s" % str(m_atts))
	# print ("m_supps %s" % str(m_supps))

	nr_votes["film"] = dict()
	nr_votes["film"]["pos"] = pos_votes_film
	nr_votes["film"]["neg"] = neg_votes_film
	print("calcolo strength movie, stampo m_atts e m_supp")
	print(m_atts)
	print(m_supps)
	feature_strengths["film"] = combination_function(film_base_score, strength_aggregation(m_atts), strength_aggregation(m_supps))

	for key, v in feature_strengths.items():
		print ("%s %s" % (key, str(v)))

	#print ("nr_votes: %d", nr_votes)

	return feature_strengths["film"]*100


if __name__ == "__main__":
	film_title ="interstellar 2014" 
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	af_file="./af/original/"+film_title+".json"
	topic_entities_dict = json.loads(open(af_file).read())
	nr_critics = 20
	#printo la strength calcolata
	film_score = strengths_dfquad(topic_entities_dict, nr_critics)
	print(film_score)
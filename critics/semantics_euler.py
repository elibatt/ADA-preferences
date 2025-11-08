from functools import reduce
from operator import mul
import math


def strength_aggregation(arg_scores):
	return sum(arg_scores)


def combination_function(base_score, att, supp):
	return 1 - ((1-(base_score**2))/(1 + (base_score * math.exp(supp-att))))


def strengths_euler(topic_entities_dict, nr_critics):
	nr_votes = dict()

	# print ("critics %s" % str(nr_critics))

	feature_strengths = dict()
	for key in topic_entities_dict.keys():
		if key == "film":
			continue
		if key == "writer" or key == "director":
			pos_votes = 0
			neg_votes = 0
			#for (text, polarity) in topic_entities_dict[key]["unique_args"]:
			for (text, polarity) in topic_entities_dict[key]["args"]:
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1

			# print ("%s_base_score %s" % (key, str(float(abs(pos_votes - neg_votes)) / nr_critics)))
			feature_strengths[key] = float(abs(pos_votes - neg_votes)) / nr_critics

			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes
			nr_votes[key]["neg"] = neg_votes

		elif key == "acting":
			pos_votes_act = 0
			neg_votes_act = 0
			#for (text, polarity) in topic_entities_dict[key]["unique_args"]:
			for (text, polarity) in topic_entities_dict[key]["args"]:
				if float(polarity)>0:
					pos_votes_act +=1
				else:
					neg_votes_act +=1
			
			base_score_act = float(abs(pos_votes_act - neg_votes_act)) / nr_critics

			# print ("base_score_act %s" % str(base_score_act))

			supps = []
			atts = []

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

			feature_strengths[key] = combination_function(base_score_act, strength_aggregation(atts), strength_aggregation(supps))
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

			feature_strengths[key] = combination_function(base_score_theme, strength_aggregation(atts), strength_aggregation(supps))

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

	feature_strengths["film"] = combination_function(film_base_score, strength_aggregation(m_atts), strength_aggregation(m_supps))

	for key, v in feature_strengths.items():
		print ("%s %s" % (key, str(v)))

	# print (nr_votes)

	return feature_strengths["film"]*100


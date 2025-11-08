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


def strengths_quad_unique(topic_entities_dict, nr_critics):
	print("sono in strengths QUAD NO PREF")
	nr_votes = dict()
	#print("sono nel film semantics dfquad gen")
	print ("critics %s" % str(nr_critics))
	feature_strengths = dict()
	#se la key è film proseguo
	for key in topic_entities_dict.keys():
		if key == "film":
			continue
		#se la key che leggo è writer o director
		if key == "writer" or key == "director":
			#non vado a controllare anche le singole entities (che comunque hanno rece GIA presenti nell' unique args di writer e director, grazie ad augmentation)
			pos_votes = 0
			neg_votes = 0
			numberReviews= 0
			#ciclo le rece di writer o director, e se hanno polarità >0 allora è un voto positivo, altrimenti negativo
			for (text, polarity) in topic_entities_dict[key]["unique_args"]:
				#print("sono nella key %s che ha degli unique_args" % key)
				#print("polarity %.4f"% float(polarity))
				numberReviews+=1
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1
			#print("attualmente la key %s ha %d voti positivi" % (key,pos_votes))
			#print("attualmente la key %s ha %d voti negativi" % (key,neg_votes))
		
			#sulla base dei voti negativi calcolo base score
			#print ("%s_base_score %s" % (key, str(float(abs(pos_votes - neg_votes)) / nr_critics)))
			
			#visto cosa si presuppone, cioè che writer e director NON abbiano figli, allora base score == strength dfquad, sono nodi foglia
			#feature_strengths[key] = float(abs(pos_votes - neg_votes)) / nr_critics
		
			if numberReviews == 0:
				print ("%s_base_score %s" % (key, str(0)))	
				feature_strengths[key] = 0
			else:
				print ("%s_base_score %s" % (key, str(float(abs(pos_votes - neg_votes)) / numberReviews)))	
				feature_strengths[key] = float(abs(pos_votes - neg_votes)) / numberReviews
			print("feature_strength di %s uguale a base score: %.3f" % (key, float(feature_strengths[key])))
			
			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes
			nr_votes[key]["neg"] = neg_votes
			#print(nr_votes[key]["pos"])
			#print(nr_votes[key]["neg"])

		elif key == "acting":
			#leggo acting
			numberReviewsActing = 0
			pos_votes_act = 0
			neg_votes_act = 0
			for (text, polarity) in topic_entities_dict[key]["unique_args"]:
				
				#ciclo le recensioni di acting (che contiene anche quelle delle entities) in unique args e faccio solito calcolo voti positivi e negativi
				numberReviewsActing+=1
				if float(polarity) > 0:
					pos_votes_act += 1
				else:
					neg_votes_act += 1
			#print("acting generico ha %d voti positivi" % pos_votes_act)
			#print("acting generico ha %d voti negativi"% neg_votes_act)
			
			#calcolo base score, sta volta non è anche strength perchè qui è previsto ci siano eventuali nodi figli
			
			if numberReviewsActing==0:
				base_score_act = 0
			else:
				base_score_act = float(abs(pos_votes_act - neg_votes_act)) / numberReviewsActing
			print ("base_score_acting generico %s" % str(base_score_act))

			supps = []
			atts = []
			supps_act_arg=[]
			atts_act_arg=[]
			for actor in topic_entities_dict[key]["entities"]:
				#ciclo gli attori
				numberReviewsActor = 0
				pos_votes = 0
				neg_votes = 0
				if topic_entities_dict[key]["entities"][actor]["unique_args"]:
					#se l'attore ha delle recensioni, le ciclo e controllo sempre la polarità, salvando n° voti positivi e negativi
					for (text, polarity) in topic_entities_dict[key]["entities"][actor]["unique_args"]:
						numberReviewsActor+=1
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1
					#print("questo attore ha %d voti positiv" % pos_votes )
					#print("questo attore ha %d voti negativi"% neg_votes )

					#calcolo base score == strength dell'attore (nodo foglia)
					
					
					if numberReviewsActor==0:
						ent_score = 0
					else:
						ent_score = float(abs(pos_votes - neg_votes)) / numberReviewsActor
					feature_strengths["acting_"+actor] = ent_score
					print ("base_score_acting_%s %s = feature strength" % (actor, str(ent_score)))

					#assegnamento supporto o  attacco (da questo attore ad acting) su base stessa polarità tra argomenti 
					if pos_votes >= neg_votes and pos_votes_act >= neg_votes_act:
						supps.append(ent_score)
						supps_act_arg.append(actor)
					elif pos_votes <= neg_votes and pos_votes_act <= neg_votes_act:
						supps.append(ent_score)
						supps_act_arg.append(actor)
					elif neg_votes > pos_votes and pos_votes_act > neg_votes_act:
						atts.append(ent_score)
						atts_act_arg.append(actor)
					elif neg_votes < pos_votes and pos_votes_act < neg_votes_act:
						atts.append(ent_score)
						atts_act_arg.append(actor)

				nr_votes[actor] = dict()
				nr_votes[actor]["pos"] = pos_votes
				nr_votes[actor]["neg"] = neg_votes

			# print ("act_atts %s" % str(atts))
			# print ("act_supps %s" % str(supps))

			#a questo punto so base score acting, so base score==strength di eventuali nodi figli e anche se sono attacchi o supporti
			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes_act
			nr_votes[key]["neg"] = neg_votes_act
			print("ATTS ACTING: %s, values: %s" % (atts_act_arg, atts))
			print("SUPPS ACTING: %s, values: %s" % (supps_act_arg, supps))
			
			feature_strengths[key] = combination_function(base_score_act, strength_aggregation_att(base_score_act,atts), strength_aggregation_sup(base_score_act,supps))
			print("Acting strength: %s" % str(feature_strengths[key]))
		else:
			# it's a theme
			numberReviewsThemes = 0
			pos_votes_theme = 0
			neg_votes_theme = 0
			for (text, polarity) in topic_entities_dict["themes"]["unique_args"]:
				numberReviewsThemes+=1
				if float(polarity) > 0:
					pos_votes_theme += 1
				else:
					neg_votes_theme += 1
			print("themes ha %d pos e %d neg" % (pos_votes_theme, neg_votes_theme))
			#base_score_theme = float(abs(pos_votes_theme - neg_votes_theme)) / nr_critics
			
			if numberReviewsThemes == 0:
				base_score_theme = 0
			else:
				base_score_theme = float(abs(pos_votes_theme - neg_votes_theme)) / numberReviewsThemes
			print ("base_score_theme %s" % str(base_score_theme))

			supps = []
			atts = []
			supps_th_arg = []
			atts_th_arg = []
			# before was for one theme only
			for theme in topic_entities_dict[key]["entities"]:
				pos_votes = 0
				neg_votes = 0
				numberReviewsTheme = 0
				if topic_entities_dict["themes"]["entities"]:
					for (text, polarity) in topic_entities_dict["themes"]["entities"][theme]["unique_args"]:
						numberReviewsTheme +=1
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1
					print("%s ha %d pos e %d neg"% (theme, pos_votes, neg_votes))
					
					if numberReviewsTheme==0:
						ent_score = 0
					else:
						ent_score = float(abs(pos_votes - neg_votes)) / numberReviewsTheme
					print("%s base score == strength: %s" %(str(theme), str(ent_score)))
					feature_strengths["theme_"+theme] = ent_score

					if pos_votes >= neg_votes and pos_votes_theme >= neg_votes_theme:
						supps.append(ent_score)
						supps_th_arg.append(theme)
					elif pos_votes <= neg_votes and pos_votes_theme <= neg_votes_theme:
						supps.append(ent_score)
						supps_th_arg.append(theme)
					elif neg_votes > pos_votes and pos_votes_theme > neg_votes_theme:
						atts.append(ent_score)
						atts_th_arg.append(theme)
					elif neg_votes < pos_votes and pos_votes_theme < neg_votes_theme:
						atts.append(ent_score)
						atts_th_arg.append(theme)
					
				nr_votes[theme] = dict()
				nr_votes[theme]["pos"] = pos_votes
				nr_votes[theme]["neg"] = neg_votes

			print("ATTS THEMES: %s, values: %s" % (atts_th_arg, atts))
			print("SUPPS THEMES: %s, values: %s" % (supps_th_arg, supps))
			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes_theme
			nr_votes[key]["neg"] = neg_votes_theme

			# print ("theme_atts %s" % str(atts))
			# print ("theme_supps %s" % str(supps))

			feature_strengths[key] = combination_function(base_score_theme, strength_aggregation_att(base_score_theme,atts), strength_aggregation_sup(base_score_theme,supps))
			print("Themes strength: %s"% str(feature_strengths[key]))
	m_atts = []
	m_supps = []
	supps_movie_arg = []
	atts_movie_arg = []
	numberReviewsMovie = 0
	#a questo punto ho guardato tutti i nodi dell'albero tranne il movie
	pos_votes_film = 0
	neg_votes_film = 0

	#questi unique args contengono tutte le possibili recensioni, grazie ad augmentazione, quindi ogni recensione la prendo e faccio solito calcolo numero voti positivi e negativi
	for (text, polarity) in topic_entities_dict["film"]["unique_args"]:
		numberReviewsMovie +=1
		if float(polarity) > 0:
			pos_votes_film += 1
		else:
			neg_votes_film += 1
	print("movie ha %d pos e %d neg" % (pos_votes_film, neg_votes_film))


	#grazie a numero voti pos e neg calcolo base score del movie
	#film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics


	#film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics
	film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / numberReviewsMovie
	print ("film_base_score %s" % str(film_base_score))

	#ciclo solo i nodi figli di movie (non le subfeatures)
	for key in feature_strengths.keys():
		#se c'è almeno una delle due, l'and diventa falso, quindi qui sto prendendo i sibling diretti di movie, le features, escludendo le subfeatures eventuali
		if "acting_" not in key and "theme_" not in key:
			pos_votes_key = nr_votes[key]["pos"]
			neg_votes_key = nr_votes[key]["neg"]
			#print("pos_votes_key %d, neg_votes_key %d" % (pos_votes_key, neg_votes_key))
			#if pos_votes_key != 0 or neg_votes_key != 0:
			if pos_votes_key >= neg_votes_key:
				m_supps.append(feature_strengths[key])
				supps_movie_arg.append(key)
			elif neg_votes_key > pos_votes_key:
				m_atts.append(feature_strengths[key])
				atts_movie_arg.append(key)

	
	# print ("m_atts %s" % str(m_atts))
	# print ("m_supps %s" % str(m_supps))

	#a questo punto so base score del movie, i suoi attacchi e supporti con relative strenght, posso calcolare la strength del movie
	nr_votes["film"] = dict()
	nr_votes["film"]["pos"] = pos_votes_film
	nr_votes["film"]["neg"] = neg_votes_film
	
	print("ATTS MOVIE: %s , values: %s" % (atts_movie_arg, m_atts))
	print("SUPPS MOVIE: %s , values: %s" % (supps_movie_arg, m_supps))

	
	feature_strengths["film"] = combination_function(film_base_score, strength_aggregation_att(film_base_score,m_atts), strength_aggregation_sup(film_base_score,m_supps))
	print("Movie strength: %s" % str(feature_strengths["film"]*100))

	for key, v in feature_strengths.items():
		print ("%s %s" % (key, str(v)))

	#print ("nr_votes: %d", nr_votes)

	return feature_strengths["film"]*100

if __name__ == "__main__":
	film_title ="oppenheimer 2023" 
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	#af_file="./af/original/"+film_title+".json"
	af_file = "./af/2023/"+film_title+".json"
	topic_entities_dict = json.loads(open(af_file).read())
	nr_critics = 20
	#printo la strength calcolata
	film_score = strengths_quad_unique(topic_entities_dict, nr_critics)
	print(film_score)
from functools import reduce
from operator import mul
import json
import jsonlines
import re
import os
import pickle
from assegnaLivelli import fromPrefToLevels
from assegnaLivelli import fromLevelsToWeights

def strength_aggregation(arg_scores):
	length = len(arg_scores)
	if length == 0:
		return 0
	else:
		return recursive_function(arg_scores)


def recursive_function(arg_scores):
	prod = [1-score for score in arg_scores]
	return 1 - reduce(mul, prod, 1)


def combination_function(base_score, att, supp):
	if att == supp:
		return base_score
	elif att > supp:
		#print("att>supp")
		return base_score - base_score*abs(supp-att)
	else:
		#print("supp>att")
		print(base_score + (1-base_score)*abs(supp-att))
		return base_score + (1-base_score)*abs(supp-att)




def strengths_dfquad_weights_extended(topic_entities_dict, nr_critics, listAnsPref, list_keys, list_entities_preferences, list_entities_complete):
	nr_votes = dict()
	levelsLists=[]
	print("Sono in DFQUAD WEIGHTS")
	print("nr_critics: %d"% nr_critics)
	print("list answers preferences: %s" % listAnsPref)
	print("list_keys: %s"% list_keys)
	print("list_entities: %s"% list_entities_preferences)
	print("list entities complete: %s"% list_entities_complete)
	empty=True
	#turn indexes into features' names
	levelsKeys=[]
	for element in listAnsPref["keysPreferences"]:
		if element != '':
			empty=False
			index= listAnsPref["keysPreferences"].index(element)
			a= list_keys[int(element[0])]
			b= list_keys[int(element[2])]
			newelement= a+'>'+b
			listAnsPref["keysPreferences"][index]=newelement
	if empty==False:
		print("converted list: %s"% listAnsPref['keysPreferences'])
		#calculate levels
		levelsKeys = fromPrefToLevels(listAnsPref['keysPreferences'])
		print("levels list: %s "% levelsKeys)
		#remove multiple square brackets
		#levelsKeys = [item for sublist in levelsKeys for item in sublist]
		levelsLists.append(levelsKeys)
	else:
		print("list Keys is empty")

	#same for entities
	levelsEntity = {'acting': [], 'themes': []}
	for entity in listAnsPref["entities"]:
		empty=True
		for element in listAnsPref["entities"][entity]:
			if element != '':
				empty=False
				index= listAnsPref["entities"][entity].index(element)
				a= list_entities_preferences[entity][int(element[0])]
				b= list_entities_preferences[entity][int(element[2])]
				newelement= a+'>'+b
				listAnsPref["entities"][entity][index]=newelement
		if empty==False:
			print("converted list entities: %s" % listAnsPref['entities'][entity])
			levelsEntity[entity] = fromPrefToLevels(listAnsPref['entities'][entity])
			#levelsEntity[entity] = [item for sublist in levelsEntity for item in sublist]
			print("levels list entities: %s" %levelsEntity[entity])
			levelsLists.append(levelsEntity[entity])
		else:
			print("list entity "+ entity+ "is empty")
		
	
	#calculate weights on the basis of levels
	weights_dict_keys={}
	weights_dict_entites={'acting': [], 'themes': []}
	weights_dict_keys = fromLevelsToWeights(levelsKeys, list(list_keys.values()))
	for entity in listAnsPref["entities"]:
		#print("entity: %s"%entity)
		weights_dict_entites[entity] =fromLevelsToWeights(levelsEntity[entity], list_entities_complete[entity])
		
	feature_strengths = dict()
	print("Weights dict keys %s"%weights_dict_keys)
	print("Weights dict entities %s" % weights_dict_entites)


	for key in topic_entities_dict.keys():
		if key == "film":
			continue
		if key == "writer" or key == "director":
			#not children nodes here, so directly calculate base score (on the basis of n° pos and neg votes) * weight
			weightKey = weights_dict_keys[key]
			numberReviews = 0
			pos_votes = 0
			neg_votes = 0
			for (text, polarity) in topic_entities_dict[key]["unique_args"]:
				numberReviews +=1
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1
			
			if numberReviews ==0:
				feature_strengths[key]= 0
				print("%s -  weight : %s, base score == strength: %d" %(key,str(weightKey),0))
			else:
				feature_strengths[key] = (float(abs(pos_votes - neg_votes)) / numberReviews)*weightKey
				print("%s -  weight : %s, base score: %s, then strength= bs*w: %s" %(key, str(weightKey), str(float(abs(pos_votes - neg_votes)) / numberReviews), str(feature_strengths[key])))
			#store n° pos and negative votes of this key
			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes
			nr_votes[key]["neg"] = neg_votes

		elif key == "acting":
			#here there can be children nodes
			weightKey = weights_dict_keys[key]
			numberReviewsActing= 0
			pos_votes_act = 0
			neg_votes_act = 0
			
			for (text, polarity) in topic_entities_dict[key]["unique_args"]:
				numberReviewsActing+=1
				if float(polarity) > 0:
					pos_votes_act += 1
				else:
					neg_votes_act += 1
		
			if numberReviewsActing == 0:
				base_score_act = 0
			else:
				base_score_act = float(abs(pos_votes_act - neg_votes_act)) / numberReviewsActing
			base_score_acting_weighted = base_score_act * weightKey
			print("%s - base score: %s, weight: %s,  basescore*weight: %s" %(key, str(base_score_act), str(weightKey),str(base_score_acting_weighted)))
			

			supps = []
			atts = []
			supps_act_arg=[]
			atts_act_arg=[]
			
			#now we check for actors
			for actor in topic_entities_dict[key]["entities"]:
				weightActor = weights_dict_entites[key][actor]
				numberReviewsActor = 0
				pos_votes = 0
				neg_votes = 0
				#check if this actor has some related reviews:
				if topic_entities_dict[key]["entities"][actor]["unique_args"]:
					for (text, polarity) in topic_entities_dict[key]["entities"][actor]["unique_args"]:
						numberReviewsActor +=1
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1
						
						#base score actor == its strength
					if numberReviewsActor == 0:
						base_score_actor = 0
					else:
						base_score_actor = float(abs(pos_votes - neg_votes)) / numberReviewsActor
					base_score_actor_weighted = base_score_actor*weightActor
					print("%s - base score: %s, weight: %s,  basescore*weight == strength: %s" % (actor, str(base_score_actor),str(weightActor), str(base_score_actor_weighted)))
					feature_strengths["acting_"+actor] = base_score_actor_weighted

					#now we calculate if this actor is a supporter of acting or an attacker:
					if pos_votes >= neg_votes and pos_votes_act >= neg_votes_act:
						supps.append(base_score_actor_weighted)
						supps_act_arg.append(actor)
					elif pos_votes <= neg_votes and pos_votes_act <= neg_votes_act:
						supps.append(base_score_actor_weighted)
						supps_act_arg.append(actor)
					elif neg_votes > pos_votes and pos_votes_act > neg_votes_act:
						atts.append(base_score_actor_weighted)
						atts_act_arg.append(actor)
					elif neg_votes < pos_votes and pos_votes_act < neg_votes_act:
						atts.append(base_score_actor_weighted)
						atts_act_arg.append(actor)
				#once again we save number of pos and neg votes
				nr_votes[actor] = dict()
				nr_votes[actor]["pos"] = pos_votes
				nr_votes[actor]["neg"] = neg_votes

			#print supporters and attackers of acting once we checked every actor
			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes_act
			nr_votes[key]["neg"] = neg_votes_act
			
			print("Acting attackers and strength values: %s, %s" % (atts_act_arg, atts))
			print("Acting supporters and strength values: %s, %s" % (supps_act_arg, supps))
			#we now calculate Strength of acting on the basis of its base score and strength of actors
			
			feature_strengths[key] = combination_function(base_score_acting_weighted, strength_aggregation(atts), strength_aggregation(supps))
			print("Strength of acting : %s"% str(feature_strengths[key]))
		else:
			# it's a theme
			weightKey = weights_dict_keys[key]
			numberReviewsThemes = 0
			pos_votes_theme = 0
			neg_votes_theme = 0
			#themes base score
			for (text, polarity) in topic_entities_dict["themes"]["unique_args"]:
				numberReviewsThemes +=1
				if float(polarity) > 0:
					pos_votes_theme += 1
				else:
					neg_votes_theme += 1
		
			if numberReviewsThemes == 0:
				base_score_themes = 0
			else:
				base_score_themes = float(abs(pos_votes_theme - neg_votes_theme)) / numberReviewsThemes
			base_score_themes_weighted= base_score_themes*weightKey
			print("%s -weight : %s, base score: %s, bs*weight : %s" %(key, str(weightKey), str(base_score_themes), str(base_score_themes_weighted)))
			
			
			

			# print ("base_score_theme %s" % str(base_score_theme))

			supps = []
			atts = []
			supps_th_arg = []
			atts_th_arg = []
			# before: with one theme 
			for theme in topic_entities_dict[key]["entities"]:
				pos_votes = 0
				neg_votes = 0
				numberReviewsTheme = 0
				#if there is at least one entity of themes (child node):
				if topic_entities_dict["themes"]["entities"]:
					weightEnt = weights_dict_entites[key][theme]
					for (text, polarity) in topic_entities_dict["themes"]["entities"][theme]["unique_args"]:
						numberReviewsTheme +=1
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1
				
					if numberReviewsTheme == 0:
						theme_base_score = 0
					else:
						theme_base_score = float(abs(pos_votes - neg_votes)) / numberReviewsTheme
					theme_base_score_weighted= theme_base_score*weightEnt
					print("%s - weight: %s, base score: %s, strength= bs*w: %s" %(theme, str(weightEnt), str(theme_base_score), str(theme_base_score_weighted)))
					feature_strengths["theme_"+theme] = theme_base_score_weighted

					if pos_votes >= neg_votes and pos_votes_theme >= neg_votes_theme:
						supps.append(theme_base_score_weighted)
						supps_th_arg.append(theme)
					elif pos_votes <= neg_votes and pos_votes_theme <= neg_votes_theme:
						supps.append(theme_base_score_weighted)
						supps_th_arg.append(theme)
					elif neg_votes > pos_votes and pos_votes_theme > neg_votes_theme:
						atts.append(theme_base_score_weighted)
						atts_th_arg.append(theme)
					elif neg_votes < pos_votes and pos_votes_theme < neg_votes_theme:
						atts.append(theme_base_score_weighted)
						atts_th_arg.append(theme)

				nr_votes[theme] = dict()
				nr_votes[theme]["pos"] = pos_votes_theme
				nr_votes[theme]["neg"] = neg_votes_theme

				
	
			
			print("Themes attackers: %s, values: %s" % (atts_th_arg, atts))
			print("Themes supporters: %s, values: %s" % (supps_th_arg, supps))
			nr_votes[key] = dict()
			nr_votes[key]["pos"] = pos_votes
			nr_votes[key]["neg"] = neg_votes

			feature_strengths[key] = combination_function(base_score_themes_weighted, strength_aggregation(atts), strength_aggregation(supps))
			print("Strength themes: %s" % str(feature_strengths[key]))
	#once we analyzed all the keys and subkeys, let's proceed with the movie
	m_atts = []
	m_supps = []
	supps_movie_arg = []
	atts_movie_arg = []

	#a questo punto ho guardato tutti i nodi dell'albero tranne il movie
	pos_votes_film = 0
	neg_votes_film = 0
	numberReviewsMovie = 0
	#print("ciclo gli unique_args del film ")
	#questi unique args contengono tutte le possibili recensioni, grazie ad augmentazione, quindi ogni recensione la prendo e faccio solito calcolo numero voti positivi e negativi
	for (text, polarity) in topic_entities_dict["film"]["unique_args"]:
		numberReviewsMovie +=1
		if float(polarity) > 0:
			pos_votes_film += 1
		else:
			neg_votes_film += 1
	

	#grazie a numero voti pos e neg calcolo base score del movie
	if numberReviewsMovie == 0:
		film_base_score = 0
	else:
		film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / numberReviewsMovie
	print ("Film_base_score %s" % str(film_base_score))

	#ciclo solo i nodi figli di movie (non le subfeatures) e capisco se sono supps o atts
	for key in feature_strengths.keys():
		#se c'è almeno una delle due, l'and diventa falso, quindi qui sto prendendo i sibling diretti di movie, le features (=keys), escludendo le subfeatures eventuali
		if "acting_" not in key and "theme_" not in key:
			pos_votes_key = nr_votes[key]["pos"]
			neg_votes_key = nr_votes[key]["neg"]
			if pos_votes_key >= neg_votes_key:
				m_supps.append(feature_strengths[key])
				supps_movie_arg.append(key)
			elif neg_votes_key > pos_votes_key:
				m_atts.append(feature_strengths[key])
				atts_movie_arg.append(key)

	
	#we know movie base score, its atts and supps, lets calculate strength
	nr_votes["film"] = dict()
	nr_votes["film"]["pos"] = pos_votes_film
	nr_votes["film"]["neg"] = neg_votes_film

	print("Movie atts and strength values: %s, %s" % (atts_movie_arg, m_atts))
	print("Movie supps and strength values: %s, %s" % (supps_movie_arg, m_supps))
	
	feature_strengths["film"] = combination_function(film_base_score, strength_aggregation(m_atts), strength_aggregation(m_supps))

	print("Movie strength: %s"% str(feature_strengths["film"]*100))

	for key, v in feature_strengths.items():
		print ("%s %s" % (key, str(v)))

	
	return feature_strengths["film"]*100

def strengths_dfquad_attacks_extended(topic_entities_dict, nr_critics, listAnsPref, list_keys, list_entities_preferences, list_entities_complete):
	print("Sono in DFQUAD ATTACKS, nr critics %d" % nr_critics)
	listaEntitiesReplacing=['writer','director','acting','themes']
	print("list answers preferences: %s" % listAnsPref)
	print("list_keys: %s"% list_keys)
	print("list_entities: %s"% list_entities_preferences)
	nr_votes= dict()
	attacksList={}
	empty=True
	#turn indexes into features' names
	for element in listAnsPref["keysPreferences"]:
		if element != '':
			empty=False
			index= listAnsPref["keysPreferences"].index(element)
			a= list_keys[int(element[0])]
			b= list_keys[int(element[2])]
			newelement= a+'>'+b
			listAnsPref["keysPreferences"][index]=newelement
	if empty==False:
		print("Converted list: %s"% listAnsPref['keysPreferences'])
	else:
		print("list Keys is empty")

	#same for entities
	for key in listAnsPref["entities"]:
		empty=True
		for element in listAnsPref["entities"][key]:
			if element != '':
				empty=False
				index= listAnsPref["entities"][key].index(element)
				a= list_entities_preferences[key][int(element[0])]
				b= list_entities_preferences[key][int(element[2])]
				newelement= a+'>'+b
				listAnsPref["entities"][key][index]=newelement
			if empty==False:
				print("converted list entity: %s" % listAnsPref['entities'][key])
			else:
				print("list entity "+ key+ "is empty")

	feature_strengths = dict()
	atts_btw_entities_children={}
	atts_between_keys={}
	#TRASFORMO PREFERENZE IN ATTACCHI
	#atts_btw_entities_children={acting:[], themes:[]}
	#atts_btw_entities_children[acting]['Brad Pitt']=['Angelina Jolie','Anne Hathaway']
	#Prima tra children nodes delle keys (i vari actor e i vari themes)
	for entity in list_entities_preferences:
		atts_btw_entities_children[entity]={}
		for entityValue in list_entities_preferences[entity].values():
			print(entityValue)
			atts_btw_entities_children[entity][entityValue]=[]
			if listAnsPref['entities'][entity] !=['']:
				for elem in listAnsPref['entities'][entity]:
					#print(elem)
					if entityValue == elem.split(">")[1]:
						atts_btw_entities_children[entity][entityValue].append(elem.split(">")[0])
			print(atts_btw_entities_children[entity][entityValue])
		
		atts_btw_entities_children[entity]=sorted(atts_btw_entities_children[entity].items(), key= lambda x: len(x[1]), reverse=False)
		print(atts_btw_entities_children[entity])
	
	#atts_keys={acting:['themes','director'], 'themes':[]}..
	#poi tra lekeys
	
	for key in list_keys.values():
		atts_between_keys[key]=[]
		for elem in listAnsPref['keysPreferences']:
			if elem != '':
				if key == elem.split(">")[1]:
					atts_between_keys[key].append(elem.split(">")[0])
	atts_between_keys=sorted(atts_between_keys.items(), key= lambda x: len(x[1]), reverse=False)
	print(atts_between_keys)
	
	
	baseScoreEntity={}
	entityAttackers = {}
	entitySupporters = {}
	#calcolo Base Scores
	for entity in listaEntitiesReplacing:
		#per ogni entity calcolo base score
		entityAttackers[entity]=[]
		entitySupporters[entity]=[]
		numberReviews = 0
		pos_votes = 0
		neg_votes = 0
		for (text, polarity) in topic_entities_dict[entity]["unique_args"]:
			numberReviews +=1
			if float(polarity) > 0:
				pos_votes += 1
			else:
				neg_votes += 1
		
		baseScoreEntity[entity] = (float(abs(pos_votes - neg_votes)) / numberReviews)
		print("%s  base score: %s" %(entity, str(float(abs(pos_votes - neg_votes)) / numberReviews)))
		nr_votes[entity] = dict()
		nr_votes[entity]["pos"] = pos_votes
		nr_votes[entity]["neg"] = neg_votes
		baseScoreChildEntity={}
		if entity in atts_btw_entities_children.keys():
			#e base score dei loro figli:
			for (childEntity,lista) in atts_btw_entities_children[entity]:
				
				numberReviewsEntity = 0
				pos_votes = 0
				neg_votes = 0
				if topic_entities_dict[entity]["entities"][childEntity]["unique_args"]:
					for (text, polarity) in topic_entities_dict[entity]["entities"][childEntity]["unique_args"]:
						numberReviewsEntity +=1
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1
						
				
				baseScoreChildEntity[childEntity] = (float(abs(pos_votes - neg_votes)) / numberReviewsEntity)
				print("%s base score %s " % (str(childEntity), str(baseScoreChildEntity[childEntity] )))
				nr_votes[childEntity] = dict()
				nr_votes[childEntity]["pos"] = pos_votes
				nr_votes[childEntity]["neg"] = neg_votes

			#calcoliamo la feature_strength dei nodi figli (non più necessariamente == base score)
			for (childEntity, lista) in	atts_btw_entities_children[entity]:
				print("%s attaccanti: %s" % (childEntity, lista))
				if len(lista)==0:
					feature_strengths[entity+"_"+childEntity]=baseScoreChildEntity[childEntity]
					print("%s non ha attaccanti quindi strength=bS %s" % (childEntity,str(feature_strengths[entity+"_"+childEntity])))
				else:
					attsStrenghts=[]
					for elem in lista:
						attsStrenghts.append(feature_strengths[entity+"_"+elem])
					print("strengths attaccanti %s: %s"%(childEntity, attsStrenghts))
					feature_strengths[entity+"_"+childEntity]=combination_function(baseScoreChildEntity[childEntity], strength_aggregation(attsStrenghts), strength_aggregation([]))
					print("%s ha almeno un attaccante, strength %s" % (childEntity,str(feature_strengths[entity+"_"+childEntity])))
		
				#capiamo se childEntity è attaccante o supporter di entity
				if nr_votes[childEntity]["pos"] >= nr_votes[childEntity]["neg"] and nr_votes[entity]["pos"] >= nr_votes[entity]["neg"]:
					entitySupporters[entity].append(feature_strengths[entity+"_"+childEntity])
					print("%s è supporter di %s" %(childEntity, entity))
				elif nr_votes[childEntity]["pos"]  <= nr_votes[childEntity]["neg"] and nr_votes[entity]["pos"] <= nr_votes[entity]["neg"]:
					entitySupporters[entity].append(feature_strengths[entity+"_"+childEntity])
					print("%s è supporter di %s" %(childEntity, entity))
				elif nr_votes[childEntity]["neg"] > nr_votes[childEntity]["pos"]  and nr_votes[entity]["pos"] > nr_votes[entity]["neg"]:
					entityAttackers[entity].append(feature_strengths[entity+"_"+childEntity])
					print("%s è attacker di %s" %(childEntity, entity))
				elif nr_votes[childEntity]["neg"] < nr_votes[childEntity]["pos"]  and nr_votes[entity]["pos"] < nr_votes[entity]["neg"]:
					entityAttackers[entity].append(feature_strengths[entity+"_"+childEntity])
					print("%s è attacker di %s" %(childEntity, entity))
		
	#  a questo punto ho già base score delle keys e strengths dei loro figli
	# devo calcolare le strengths delle keys sulla base del loro base score (c'è), della strength di chi li attacca 

	print("Base scores keys: %s" % baseScoreEntity)
	print("Strengths di attori e temi (children): %s " % feature_strengths)
	print("Supporters delle entity - strengths:%s "% entitySupporters)
	print("Attackers delle entity - strengths:%s "% entityAttackers)

	#per ogni key unisco agli attacchi-preferenze, gli attacchi provenienti dal basso
	for (key, lista) in atts_between_keys:
		#controllo attacchi orizzontali (dx sx)
		if len(lista)==0:
			if (len(entityAttackers[key])==0 and len(entitySupporters[key])==0):
				print("La key %s non è involved nelle preferences e non ha attaccanti supporti neanche dal basso"% key)
				feature_strengths[key]=baseScoreEntity[key]
				print("Quindi strength == bS : %s" % feature_strengths[key])
			else:
				feature_strengths[key] =  combination_function(baseScoreEntity[key], strength_aggregation(entityAttackers[key]), strength_aggregation(entitySupporters[key]))
				print("La key %s non è involved nelle preferences ma ha attaccanti/supporti dal basso. Strength : %s" % (key,feature_strengths[key]))
		#controllo attacchi verticali e orizzontali (dx sx, basso)
		else:
			print("La key %s ha degli attacchi/preferenze e può avere anche attaccanti/supporti dal basso. " % key)
			unifiedAttackers =[]
			for elem in lista:
				unifiedAttackers.append(feature_strengths[elem])
			unifiedAttackers= unifiedAttackers + entityAttackers[key]
			feature_strengths[key] =  combination_function(baseScoreEntity[key], strength_aggregation(unifiedAttackers), strength_aggregation(entitySupporters[key]))
			print("Strength : %s"%feature_strengths[key])
			
	#ora che ho le strength delle keys, devo capire se sono attaccanti o supporter del movie, di cui calcolo baseScore:
	
	m_atts = []
	m_supps = []
	m_atts_arg = []
	m_supps_arg = []

	#a questo punto ho guardato tutti i nodi dell'albero tranne il movie
	pos_votes_film = 0
	neg_votes_film = 0
	numberReviewsMovie = 0
	#print("ciclo gli unique_args del film ")
	#questi unique args contengono tutte le possibili recensioni, grazie ad augmentazione, quindi ogni recensione la prendo e faccio solito calcolo numero voti positivi e negativi
	for (text, polarity) in topic_entities_dict["film"]["unique_args"]:
		numberReviewsMovie +=1
		if float(polarity) > 0:
			pos_votes_film += 1
		else:
			neg_votes_film += 1
	

	#grazie a numero voti pos e neg calcolo base score del movie

	film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / numberReviewsMovie
	print ("Film_base_score %s" % str(film_base_score))

	#ciclo solo i nodi figli di movie (non le subfeatures) e capisco se sono supps o atts
	for key in feature_strengths.keys():
		#se c'è almeno una delle due, l'and diventa falso, quindi qui sto prendendo i sibling diretti di movie, le features (=keys), escludendo le subfeatures eventuali
		if "acting_" not in key and "themes_" not in key:
			pos_votes_key = nr_votes[key]["pos"]
			neg_votes_key = nr_votes[key]["neg"]
			if pos_votes_key >= neg_votes_key:
				m_supps.append(feature_strengths[key])
				m_supps_arg.append(key)
				
			elif neg_votes_key > pos_votes_key:
				m_atts.append(feature_strengths[key])
				m_atts_arg.append(key)
				

	
	#we know movie base score, its atts and supps, lets calculate strength
	nr_votes["film"] = dict()
	nr_votes["film"]["pos"] = pos_votes_film
	nr_votes["film"]["neg"] = neg_votes_film
	
	print("Movie supps strength values: %s" % ( m_supps))
	print("Movie atts strength values: %s" % (m_atts))
	feature_strengths["film"] = combination_function(film_base_score, strength_aggregation(m_atts), strength_aggregation(m_supps))

	print("Movie strength: %s"% str(feature_strengths["film"]*100))

	for key, v in feature_strengths.items():
		print ("%s %s" % (key, str(v)))


	return feature_strengths["film"]*100	
	


if __name__ == "__main__":
	film_title ="oppenheimer 2023" 
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	#af_file="./af/original/"+film_title+".json"
	af_file="./af/2023/"+film_title+".json"
	topic_entities_dict = json.loads(open(af_file).read())
	nr_critics = 20
	#printo la strength calcolata
	film_score = strengths_dfquad_unique(topic_entities_dict, nr_critics)
	print(film_score)
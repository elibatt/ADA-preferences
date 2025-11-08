from functools import reduce
from operator import mul
import os
import json
import math
import sys
import copy
from assegnaLivelli import fromPrefToLevels
from assegnaLivelli import fromLevelsToWeights
from assegnaLivelli import fromLevelsToWeightsBinary
def custom_sort(x, y):
    len_x, len_y = len(x[1]), len(y[1])

    # If lengths are the same, check if the previous key is in the current list
    if len_x == len_y:
        return (len_x, x[0] in y[1])

    return len_x - len_y

def energy_value(att,supp):
	sumAtts = 0
	sumSupps = 0
	for elem in supp:
		sumSupps = elem + sumSupps
	for elem in att:
		sumAtts = elem + sumAtts
	return sumSupps-sumAtts

def hFunction (value):
	return ((max(0,value))**2)/(1+(max(0,value))**2)

def strength_aggregation_euler(arg_scores):
	return sum(arg_scores)

def strength_aggregation_att_quad(base_score, arg_scores):
	length = len(arg_scores)
	if length == 0:
		return None
	prod = [1-score for score in arg_scores]
	return base_score * reduce(mul, prod, 1)


def strength_aggregation_sup_quad(base_score, arg_scores):
	length = len(arg_scores)
	if length == 0:
		return None
	prod = [1-score for score in arg_scores]
	return 1 - (1-base_score) * reduce(mul, prod, 1)
	

def strength_aggregation_dfquad(arg_scores):
	length = len(arg_scores)
	if length == 0:
		return 0
	else:
		return recursive_function_dfquad(arg_scores)


def recursive_function_dfquad(arg_scores):
	prod = [1-score for score in arg_scores]
	return 1 - reduce(mul, prod, 1)


def superfunction(semantic, base_score, att, supp):
	if semantic == "dfquad":
		att = strength_aggregation_dfquad(att)
		supp = strength_aggregation_dfquad(supp)
		print("att aggregati: ",att)
		print("supp aggregati: ", supp)
		if att == supp:
			return base_score
		elif att > supp:
			return base_score - base_score*abs(supp-att)
		else:
			print("printo risultato strength: ")
			print(base_score + (1-base_score)*abs(supp-att))
			return base_score + (1-base_score)*abs(supp-att)
		
	elif semantic == "quad":
		att = strength_aggregation_att_quad(base_score,att)
		
		supp = strength_aggregation_sup_quad(base_score,supp)
		
		if att == None and supp == None:
			return base_score
		elif att == None and supp != None:
			return supp
		elif supp == None and att != None:
			return att
		else:
			return (att+supp)/2
	elif semantic == "euler":
		att = strength_aggregation_euler(att)
		supp = strength_aggregation_euler(supp)
		return 1 - ((1-(base_score**2))/(1 + (base_score * math.exp(supp-att))))
	elif semantic == "energy":
		energyValue = energy_value(att,supp)
		weight = base_score
		print(sys.getsizeof( weight + (1-weight) * hFunction(energyValue) -weight*hFunction(energyValue*-1)))
		return weight + (1-weight) * hFunction(energyValue) -weight*hFunction(energyValue*-1)


def strengths_attacks_extended_all(semantic, topic_entities_dict, nr_critics, listAnsPref, list_keys, list_entities_preferences, numberReviewOrCritic):
	
	print("Sono in "+ semantic + " attacks")
	listaEntitiesReplacing=['writer','director','acting','themes']
	#print("list answers preferences: %s" % listAnsPref)
	#print("list_keys: %s"% list_keys)
	#print("list_entities: %s"% list_entities_preferences)
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
	'''
	if empty==False:
		print("Converted list: %s"% listAnsPref['keysPreferences'])
	else:
		print("list Keys is empty")
	'''
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
			'''
			if empty==False:
				print("converted list entity: %s" % listAnsPref['entities'][key])
			else:
				print("list preferences between "+ key+ " siblings is empty")
			'''
	feature_strengths = dict()
	atts_btw_entities_children={}
	atts_between_keys={}
	#TRANSFORMING PREFERENCES IN ATTACKS
	#atts_btw_entities_children={acting:[], themes:[]}
	#atts_btw_entities_children[acting]['Brad Pitt']=['Angelina Jolie','Anne Hathaway']
	#Prima tra children nodes delle keys (i vari actor e i vari themes)
	for entity in list_entities_preferences:
		atts_btw_entities_children[entity]={}
		for entityValue in list_entities_preferences[entity].values():
			#print(entityValue)
			atts_btw_entities_children[entity][entityValue]=[]
			if listAnsPref['entities'][entity] !=['']:
				for elem in listAnsPref['entities'][entity]:
					#print(elem)
					if entityValue == elem.split(">")[1]:
						atts_btw_entities_children[entity][entityValue].append(elem.split(">")[0])
			#print(atts_btw_entities_children[entity][entityValue])
		'''
		atts_btw_entities_children[entity]=sorted(atts_btw_entities_children[entity].items(), key= lambda x: len(x[1]), reverse=False)
		print(atts_btw_entities_children[entity])
		'''
		#ordino prima per lunghezza ascendente di lista, e poi se due liste hanno stessa len, allora dò la precedenza a quell'elemento la cui chiave è nella lista del successivo. Se non ci sono elementi comuni, rimane così e si prosegue il controllo
		atts_btw_entities_children[entity]=sorted(atts_btw_entities_children[entity].items(), key= lambda x: len(x[1]), reverse=False)
		read_keys=[]
		for i in range(0, len(atts_btw_entities_children[entity])-1):
			read_keys.append(atts_btw_entities_children[entity][i][0])
			if len(atts_btw_entities_children[entity][i][1])!=0:
				for elem in atts_btw_entities_children[entity][i][1]:
					if elem not in read_keys:
						temp=atts_btw_entities_children[entity][i]
						atts_btw_entities_children[entity][i]=atts_btw_entities_children[entity][i+1]
						atts_btw_entities_children[entity][i+1]=temp
				

		print(atts_btw_entities_children[entity])
	
	#atts_keys={acting:['themes','director'], 'themes':[]}..
	#poi tra lekeys
	
	for key in list_keys.values():
		atts_between_keys[key]=[]
		for elem in listAnsPref['keysPreferences']:
			if elem != '':
				if key == elem.split(">")[1]:
					atts_between_keys[key].append(elem.split(">")[0])
	'''
	atts_between_keys=sorted(atts_between_keys.items(), key= lambda x: len(x[1]), reverse=False)
	print(atts_between_keys)
	'''
	atts_between_keys=sorted(atts_between_keys.items(), key= lambda x: len(x[1]), reverse=False)
	
	read_keys=[]
	for i in range(0, len(atts_between_keys)-1):
		read_keys.append(atts_between_keys[i][0])
		if len(atts_between_keys[i][1])!=0:
			for elem in atts_between_keys[i][1]:
				if elem not in read_keys:
					temp=atts_between_keys[i]
					atts_between_keys[i]=atts_between_keys[i+1]
					atts_between_keys[i+1]=temp
			

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
		
		if numberReviewOrCritic == "nr_reviews":
			if numberReviews == 0:
				baseScoreEntity[entity] = 0
				#print("%s  base score: %s" %(entity, str(0)))
			else:
				baseScoreEntity[entity] = (float(abs(pos_votes - neg_votes)) / numberReviews)
				#print("%s  base score: %s" %(entity, str(float(abs(pos_votes - neg_votes)) / numberReviews)))
		elif numberReviewOrCritic == "nr_critics":
			baseScoreEntity[entity] = (float(abs(pos_votes - neg_votes)) / nr_critics)
			#print("%s  base score: %s" %(entity, str(float(abs(pos_votes - neg_votes)) / nr_critics)))
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
						
				if numberReviewOrCritic == "nr_reviews":
					if numberReviewsEntity == 0:
						baseScoreChildEntity[childEntity] = 0
						#print("%s base score %s " % (str(childEntity), str(baseScoreChildEntity[childEntity] )))
					else:
						baseScoreChildEntity[childEntity] = (float(abs(pos_votes - neg_votes)) / numberReviewsEntity)
						#print("%s base score %s " % (str(childEntity), str(baseScoreChildEntity[childEntity] )))
				elif numberReviewOrCritic == "nr_critics":
					baseScoreChildEntity[childEntity] = (float(abs(pos_votes - neg_votes)) / nr_critics)
					#print("%s base score %s " % (str(childEntity), str(baseScoreChildEntity[childEntity] )))
						
				nr_votes[childEntity] = dict()
				nr_votes[childEntity]["pos"] = pos_votes
				nr_votes[childEntity]["neg"] = neg_votes

			#calcoliamo la feature_strength dei nodi figli (non più necessariamente == base score)
			for (childEntity, lista) in	atts_btw_entities_children[entity]:
				#print("%s attaccanti: %s" % (childEntity, lista))
				if len(lista)==0:
					feature_strengths[entity+"_"+childEntity]=baseScoreChildEntity[childEntity]
					#print("%s non ha attaccanti quindi strength=bS %s" % (childEntity,str(feature_strengths[entity+"_"+childEntity])))
				else:
					attsStrenghts=[]
					for elem in lista:
						attsStrenghts.append(feature_strengths[entity+"_"+elem])
					#print("strengths attaccanti %s: %s"%(childEntity, attsStrenghts))
					feature_strengths[entity+"_"+childEntity]=superfunction(semantic, baseScoreChildEntity[childEntity],attsStrenghts, [] )
					#print("%s ha almeno un attaccante, strength %s" % (childEntity,str(feature_strengths[entity+"_"+childEntity])))
		
				#capiamo se childEntity è attaccante o supporter di entity
				if nr_votes[childEntity]["pos"] >= nr_votes[childEntity]["neg"] and nr_votes[entity]["pos"] >= nr_votes[entity]["neg"]:
					entitySupporters[entity].append(feature_strengths[entity+"_"+childEntity])
					#print("%s è supporter di %s" %(childEntity, entity))
				elif nr_votes[childEntity]["pos"]  <= nr_votes[childEntity]["neg"] and nr_votes[entity]["pos"] <= nr_votes[entity]["neg"]:
					entitySupporters[entity].append(feature_strengths[entity+"_"+childEntity])
					#print("%s è supporter di %s" %(childEntity, entity))
				elif nr_votes[childEntity]["neg"] > nr_votes[childEntity]["pos"]  and nr_votes[entity]["pos"] > nr_votes[entity]["neg"]:
					entityAttackers[entity].append(feature_strengths[entity+"_"+childEntity])
					#print("%s è attacker di %s" %(childEntity, entity))
				elif nr_votes[childEntity]["neg"] < nr_votes[childEntity]["pos"]  and nr_votes[entity]["pos"] < nr_votes[entity]["neg"]:
					entityAttackers[entity].append(feature_strengths[entity+"_"+childEntity])
					#print("%s è attacker di %s" %(childEntity, entity))
		
	#  a questo punto ho già base score delle keys e strengths dei loro figli
	# devo calcolare le strengths delle keys sulla base del loro base score (c'è), della strength di chi li attacca 

	print("Base scores keys: %s" % baseScoreEntity)
	#print("Strengths di attori e temi (children): %s " % feature_strengths)
	#print("Supporters delle entity - strengths:%s "% entitySupporters)
	#print("Attackers delle entity - strengths:%s "% entityAttackers)

	#per ogni key unisco agli attacchi-preferenze, gli attacchi provenienti dal basso
	for (key, lista) in atts_between_keys:
		#controllo attacchi orizzontali (dx sx)
		if len(lista)==0:
			if (len(entityAttackers[key])==0 and len(entitySupporters[key])==0):
				#print("La key %s non è involved nelle preferences e non ha attaccanti supporti neanche dal basso"% key)
				feature_strengths[key]=baseScoreEntity[key]
				#print("Quindi strength == bS : %s" % feature_strengths[key])
			else:
				feature_strengths[key] =  superfunction(semantic, baseScoreEntity[key], entityAttackers[key], entitySupporters[key])
				#print("La key %s non è involved nelle preferences ma ha attaccanti/supporti dal basso. Strength : %s" % (key,feature_strengths[key]))
		#controllo attacchi verticali e orizzontali (dx sx, basso)
		else:
			#print("La key %s ha degli attacchi/preferenze e può avere anche attaccanti/supporti dal basso. " % key)
			unifiedAttackers =[]
			for elem in lista:
				unifiedAttackers.append(feature_strengths[elem])
			unifiedAttackers= unifiedAttackers + entityAttackers[key]
			feature_strengths[key] =  superfunction(semantic, baseScoreEntity[key], unifiedAttackers, entitySupporters[key])
			#print("Strength : %s"%feature_strengths[key])
			
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
	if numberReviewOrCritic == "nr_reviews":
		if numberReviewsMovie == 0:
			film_base_score = 0
			#print ("Film_base_score %s" % str(film_base_score))
		else:
			film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / numberReviewsMovie
			#print ("Film_base_score %s" % str(film_base_score))
	elif numberReviewOrCritic == "nr_critics":
		film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics
		#print ("Film_base_score %s" % str(film_base_score))


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
	
	#print("Movie supps strength values: %s" % ( m_supps))
	#print("Movie atts strength values: %s" % (m_atts))
	feature_strengths["film"] = superfunction(semantic,film_base_score, m_atts,m_supps)

	#print("Movie strength: %s"% str(feature_strengths["film"]*100))
	
	#for key, v in feature_strengths.items():
		#print ("%s %s" % (key, str(v)))
	
	print("FINAL PRINT")
	for element in feature_strengths:
		if ("acting_" in element) or ("themes_" in element):
			elementS = element.split("_")
			print(elementS[1].replace(" ", "")+" "+str(feature_strengths[element]))
		else:
			print(element.replace(" ", "")+" "+str(feature_strengths[element]))

	return feature_strengths["film"]*100	

def strengths_weights_extended_all(semantic,topic_entities_dict, nr_critics, listAnsPref, list_keys, list_entities_preferences, list_entities_complete,numberReviewOrCritic):
	nr_votes = dict()
	levelsLists=[]
	print("Sono in "+ semantic+" WEIGHTS")
	#print("nr_critics: %d"% nr_critics)
	#print("list answers preferences: %s" % listAnsPref)
	#print("list_keys: %s"% list_keys)
	#print("list_entities: %s"% list_entities_preferences)
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
		#print("converted list: %s"% listAnsPref['keysPreferences'])
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
			#print("converted list entities: %s" % listAnsPref['entities'][entity])
			levelsEntity[entity] = fromPrefToLevels(listAnsPref['entities'][entity])
			#levelsEntity[entity] = [item for sublist in levelsEntity for item in sublist]
			print("levels list entities: %s" %levelsEntity[entity])
			levelsLists.append(levelsEntity[entity])
		else:
			print("list entity "+ entity+ "is empty")
		
	
	#calculate weights on the basis of levels
	weights_dict_keys={}
	weights_dict_entites={'acting': [], 'themes': []}
	#weights_dict_keys = fromLevelsToWeights(levelsKeys, list(list_keys.values()))
	weights_dict_keys = fromLevelsToWeightsBinary(levelsKeys, list(list_keys.values()))
	for entity in listAnsPref["entities"]:
		#print("entity: %s"%entity)
		#weights_dict_entites[entity] =fromLevelsToWeights(levelsEntity[entity], list_entities_complete[entity])
		weights_dict_entites[entity] =fromLevelsToWeightsBinary(levelsEntity[entity], list_entities_complete[entity])
		
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
			if numberReviewOrCritic == "nr_reviews":
				if numberReviews ==0:
					feature_strengths[key]= 0
					#print("%s -  weight : %s, base score == strength: %s" %(key,str(weightKey),str(0)))
				else:
					feature_strengths[key] = (float(abs(pos_votes - neg_votes)) / numberReviews)*weightKey
					#print("%s -  weight : %s, base score: %s, then strength= bs*w: %s" %(key, str(weightKey), str(float(abs(pos_votes - neg_votes)) / numberReviews), str(feature_strengths[key])))
			elif numberReviewOrCritic == "nr_critics":
				feature_strengths[key] = (float(abs(pos_votes - neg_votes)) / nr_critics)*weightKey
				#print("%s -  weight : %s, base score: %s, then strength= bs*w: %s" %(key, str(weightKey), str(float(abs(pos_votes - neg_votes)) / nr_critics), str(feature_strengths[key])))

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
			if numberReviewOrCritic == "nr_reviews":
				if numberReviewsActing == 0:
					base_score_act = 0
				else:
					base_score_act = float(abs(pos_votes_act - neg_votes_act)) / numberReviewsActing
			elif numberReviewOrCritic == "nr_critics":
				base_score_act = float(abs(pos_votes_act - neg_votes_act)) / nr_critics
			base_score_acting_weighted = base_score_act * weightKey
			print("base_score_acting_weighted: ", base_score_acting_weighted)
			#print("%s - base score: %s, weight: %s,  basescore*weight: %s" %(key, str(base_score_act), str(weightKey),str(base_score_acting_weighted)))
			

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
					if numberReviewOrCritic == "nr_reviews":
						if numberReviewsActor == 0:
							base_score_actor = 0
						else:
							base_score_actor = float(abs(pos_votes - neg_votes)) / numberReviewsActor
					elif numberReviewOrCritic == "nr_critics":
						base_score_actor = float(abs(pos_votes - neg_votes)) / nr_critics

					base_score_actor_weighted = base_score_actor*weightActor
					#print("%s - base score: %s, weight: %s,  basescore*weight == strength: %s" % (actor, str(base_score_actor),str(weightActor), str(base_score_actor_weighted)))
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
			
			feature_strengths[key] = superfunction(semantic,base_score_acting_weighted, atts,supps)
			#print("Strength of acting : %s"% str(feature_strengths[key]))
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
			if numberReviewOrCritic == "nr_reviews":
				if numberReviewsThemes == 0:
					base_score_themes = 0
				else:
					base_score_themes = float(abs(pos_votes_theme - neg_votes_theme)) / numberReviewsThemes
			elif numberReviewOrCritic == "nr_critics":
				base_score_themes = float(abs(pos_votes_theme - neg_votes_theme)) / nr_critics
			base_score_themes_weighted= base_score_themes*weightKey
			#print("%s -weight : %s, base score: %s, bs*weight : %s" %(key, str(weightKey), str(base_score_themes), str(base_score_themes_weighted)))
			
			
			

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
					if numberReviewOrCritic == "nr_reviews":
						if numberReviewsTheme == 0:
							theme_base_score = 0
						else:
							theme_base_score = float(abs(pos_votes - neg_votes)) / numberReviewsTheme
					elif numberReviewOrCritic == "nr_critics":
						theme_base_score = float(abs(pos_votes - neg_votes)) / nr_critics
					theme_base_score_weighted= theme_base_score*weightEnt
					#print("%s - weight: %s, base score: %s, strength= bs*w: %s" %(theme, str(weightEnt), str(theme_base_score), str(theme_base_score_weighted)))
					feature_strengths["themes_"+theme] = theme_base_score_weighted

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

			feature_strengths[key] = superfunction(semantic,base_score_themes_weighted,atts,supps)
			#print("Strength themes: %s" % str(feature_strengths[key]))
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
	if numberReviewOrCritic == "nr_reviews":
		if numberReviewsMovie == 0:
			film_base_score = 0
		else:
			film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / numberReviewsMovie
	elif numberReviewOrCritic == "nr_critics":
		film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics
	#print ("Film_base_score %s" % str(film_base_score))

	#ciclo solo i nodi figli di movie (non le subfeatures) e capisco se sono supps o atts
	for key in feature_strengths.keys():
		#se c'è almeno una delle due, l'and diventa falso, quindi qui sto prendendo i sibling diretti di movie, le features (=keys), escludendo le subfeatures eventuali
		if "acting_" not in key and "themes_" not in key:
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
	
	feature_strengths["film"] = superfunction(semantic,film_base_score, m_atts,m_supps)

	#print("Movie strength: %s"% str(feature_strengths["film"]*100))

	#for key, v in feature_strengths.items():
		#print ("%s %s" % (key, str(v)))

	print("FINAL PRINT")
	for element in feature_strengths:
		if ("acting_" in element) or ("themes_" in element):
			elementS = element.split("_")
			print(elementS[1].replace(" ", "")+" "+str(feature_strengths[element]))
		else:
			print(element+" "+str(feature_strengths[element]))
	return feature_strengths["film"]*100

def strengths_nopref_all(semantic, topic_entities_dict, nr_critics, numberReviewOrCritic):
	print("sono in strengths "+ semantic + " NO PREF")
	nr_votes = dict()
	#print("sono nel film semantics dfquad gen")
	#print ("critics %s" % str(nr_critics))
	
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
			if numberReviewOrCritic == "nr_reviews":
				if numberReviews == 0:
					#print ("%s_base_score %s" % (key, str(0)))	
					feature_strengths[key] = 0
				else:
					print ("Nr_rev %s_base_score %s" % (key, str(float(abs(pos_votes - neg_votes)) / numberReviews)))	
					feature_strengths[key] = float(abs(pos_votes - neg_votes)) / numberReviews
			elif numberReviewOrCritic == "nr_critics":
				print (" Nr_cr %s_base_score %s" % (key, str(float(abs(pos_votes - neg_votes)) / nr_critics)))	
				feature_strengths[key] = float(abs(pos_votes - neg_votes)) / nr_critics

			#print("feature_strength di %s uguale a base score: %.3f" % (key, float(feature_strengths[key])))
			
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
			print("acting generico ha %d voti positivi" % pos_votes_act)
			print("acting generico ha %d voti negativi"% neg_votes_act)
			
			#calcolo base score, sta volta non è anche strength perchè qui è previsto ci siano eventuali nodi figli
			if numberReviewOrCritic == "nr_reviews":
				if numberReviewsActing==0:
					base_score_act = 0
				else:
					base_score_act = float(abs(pos_votes_act - neg_votes_act)) / numberReviewsActing
			elif numberReviewOrCritic == "nr_critics":
				base_score_act = float(abs(pos_votes_act - neg_votes_act)) / nr_critics

			print ("base_score_acting %s with %s" % (str(base_score_act), numberReviewOrCritic))

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
					
					if numberReviewOrCritic == "nr_reviews":
						if numberReviewsActor==0:
							ent_score = 0
						else:
							ent_score = float(abs(pos_votes - neg_votes)) / numberReviewsActor
					elif numberReviewOrCritic == "nr_critics":
						ent_score = float(abs(pos_votes - neg_votes)) / nr_critics

					feature_strengths["acting_"+actor] = ent_score
					print ("base_score_acting_%s %s with %s = feature strength" % (actor, str(ent_score), numberReviewOrCritic))

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
			
			feature_strengths[key] = superfunction(semantic, base_score_act, atts, supps)
			#print("Acting strength: %s" % str(feature_strengths[key]))
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
			#print("themes ha %d pos e %d neg" % (pos_votes_theme, neg_votes_theme))
			#base_score_theme = float(abs(pos_votes_theme - neg_votes_theme)) / nr_critics
			if numberReviewOrCritic == "nr_reviews":
				if numberReviewsThemes == 0:
					base_score_theme = 0
				else:
					base_score_theme = float(abs(pos_votes_theme - neg_votes_theme)) / numberReviewsThemes
			elif numberReviewOrCritic == "nr_critics":
				base_score_theme = float(abs(pos_votes_theme - neg_votes_theme)) / nr_critics
			print ("base_score_themes %s with %s" % (str(base_score_theme), numberReviewOrCritic))

			supps = []
			atts = []
			supps_th_arg = []
			atts_th_arg = []
			# before was for one theme only, now we cycle each theme entity
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
					#print("%s ha %d pos e %d neg"% (theme, pos_votes, neg_votes))
					if numberReviewOrCritic == "nr_reviews":
						if numberReviewsTheme==0:
							ent_score = 0
						else:
							ent_score = float(abs(pos_votes - neg_votes)) / numberReviewsTheme
					elif numberReviewOrCritic=="nr_critics":
						ent_score = float(abs(pos_votes - neg_votes)) / nr_critics
					print("Theme %s base score == strength: %s" %(str(theme), str(ent_score)))
					feature_strengths["themes_"+theme] = ent_score

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

			feature_strengths[key] = superfunction(semantic, base_score_theme, atts, supps)
			#print("Themes strength: %s"% str(feature_strengths[key]))
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
	#print("movie ha %d pos e %d neg" % (pos_votes_film, neg_votes_film))


	#grazie a numero voti pos e neg calcolo base score del movie
	#film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics

	if numberReviewOrCritic == "nr_reviews":
		film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / numberReviewsMovie
	elif numberReviewOrCritic == "nr_critics":
		film_base_score = 0.5 + (0.5*((pos_votes_film - neg_votes_film))) / nr_critics
	print ("Movie_base score with %s:  %s" % (numberReviewOrCritic, str(film_base_score)))

	#ciclo solo i nodi figli di movie (non le subfeatures)
	for key in feature_strengths.keys():
		#se c'è almeno una delle due, l'and diventa falso, quindi qui sto prendendo i sibling diretti di movie, le features, escludendo le subfeatures eventuali
		if "acting_" not in key and "themes_" not in key:
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

	
	feature_strengths["film"] = superfunction(semantic, film_base_score, m_atts,m_supps)
	#print("Movie strength: %s" % str(feature_strengths["film"]*100))

	#for key, v in feature_strengths.items():
		#print ("%s %s" % (key, str(v)))

	#print ("nr_votes: %d", nr_votes)
	
	print("FINAL PRINT")
	for element in feature_strengths:
		if ("acting_" in element) or ("themes_" in element):
			elementS = element.split("_")
			print(elementS[1].replace(" ", "")+" "+str(feature_strengths[element]))
		else:
			print(element+" "+str(feature_strengths[element]))

	return feature_strengths["film"]*100


if __name__ == "__main__":
	film_title ="toyExample" 
	nuova_cartella = os.path.join(os.path.dirname(os.getcwd()), 'RT')
	os.chdir(nuova_cartella)
	#af_file="./af/original/"+film_title+".json"
	af_file="./af/2023/"+film_title+".json"
	topic_entities_dict = json.loads(open(af_file).read())
	nr_critics = 90
	listAnsPref = {'keysPreferences': [''], 'entities': {'acting': ['1>0', '0>2', '2>3'], 'themes': ['1>0']}}
	list_keys = {0: 'director', 1: 'writer', 2: 'acting', 3: 'themes'}
	list_entities_preferences= {'acting': {0: 'Johnny Depp', 1: 'Angelina Jolie', 2: 'Brad Pitt', 3: 'Anne Hathaway'}, 'themes': {0: 'Power', 1: 'Revenge', 2: 'Love', 3: 'Betrayal'}}
	list_entities_complete={'acting': ['Johnny Depp', 'Angelina Jolie', 'Brad Pitt', 'Anne Hathaway'], 'themes': ['Power', 'Revenge', 'Love', 'Betrayal']}
	listOrig = copy.deepcopy(listAnsPref)
	#film_score = strengths_attacks_extended_all("dfquad",topic_entities_dict, nr_critics, listAnsPref, list_keys, list_entities_preferences, list_entities_complete)
	film_score = strengths_nopref_all("dfquad",topic_entities_dict, nr_critics)
	#print(film_score)
	
	listAnsPref = copy.deepcopy(listOrig)
	film_score = strengths_weights_extended_all("dfquad",topic_entities_dict, nr_critics, listAnsPref, list_keys, list_entities_preferences, list_entities_complete)
	#print(film_score)

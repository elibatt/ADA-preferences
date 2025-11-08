# it's assumed critics are already unique
def find_polarity_of_critic_in_args(critic_id, args):
	for (arg, polarity) in args:
		if arg.split("_")[0] == critic_id:
			#print("la critica con questo id è: %s" % arg)
			return polarity


def uniquify(args):
	unique_args = []
	critics = [arg.split("_")[0] for (arg, score) in args]
	duplicates = set([x for x in critics if critics.count(x) > 1])

	if duplicates:
		for dup in duplicates:
			max_tuple = ("None", 0)
			dup_arg_scores = [(arg, score) for (arg, score) in args if arg.split("_")[0] == str(dup)]
			for (arg, score) in dup_arg_scores:
				if abs(float(score)) > abs(max_tuple[1]):
					max_tuple = (arg, score)

			unique_args.append(max_tuple)

	uniques = set(critics).difference(duplicates)

	for (arg, score) in args:
		if arg.split("_")[0] in uniques:
			unique_args.append((arg, score))

	return unique_args


def unique_critics_score(topic_entities_dict):
	print("Extending from args to unique args")
	#preparazione del nuovo array a livello strutturale
	unique_topic_entities_dict = dict()
	for key in list(topic_entities_dict.keys()):
		unique_topic_entities_dict[key] = topic_entities_dict[key]
		unique_topic_entities_dict[key]["unique_args"] = []
		#se la key (writer/director etc) ha delle entity non vuote
		if "entities" in list(topic_entities_dict[key].keys()):
			for ent_key in list(topic_entities_dict[key]["entities"]):
				#allora per ogni entity preparo nel nuovo array unique uno spazio vuoto
				unique_topic_entities_dict[key]["entities"][ent_key]["unique_args"] = []
	
	#ora ciclo ogni chiave dell'array originale (writer/director etc)
	for key in topic_entities_dict.keys():
		#copio gli args delle key generiche in unique_args dopo aver tolto i duplicati
		unique_topic_entities_dict[key]["unique_args"].extend(uniquify(topic_entities_dict[key]["args"]))
		if "entities" in topic_entities_dict[key].keys():
			#se ha delle entities
			for ent_key in (topic_entities_dict[key]["entities"]):
				#tolgo eventuali duplicati da entities ent args
				uniquified = uniquify(topic_entities_dict[key]["entities"][ent_key]["args"])
				#copio da [key][entities][entity][args] a [key][entities][entity][unique args]
				unique_topic_entities_dict[key]["entities"][ent_key]["unique_args"].extend(uniquified)
				#IMPORTANTE
				#lo copio anche in [key][unique args] (quindi il generico unique args della key generica) --> quindi key generica ha args[], unique args[--], entities[--] forse veniva fatto per avere più reviews (ma qua non è augmentation)
				unique_topic_entities_dict[key]["unique_args"].extend(uniquified)
			unique_topic_entities_dict[key]["unique_args"] = uniquify(unique_topic_entities_dict[key]["unique_args"])

	#print("stampo il unique con estensione")
	print("Stampo unique_topic_entities_dict before augment : %s" %unique_topic_entities_dict)
	return unique_topic_entities_dict


def augment(topic_entities_dict, nr_critics):
	#qua struttura iniz è key: {args:[], unique args:[copia delle unique args delle entity] entities:{'entity':{args: ABC, unique args: ABC}}}
	#quindi args vuoti e doppioni nelle entity

	#key_critics contiene tutti gli id delle recensioni contenute nell'unique args delle entities, cioè le uniche recensioni al momento presenti.
	film_args = topic_entities_dict["film"]["unique_args"]
	film_critics = [arg.split("_")[0] for (arg, score) in topic_entities_dict["film"]["unique_args"]]
	print("film critics:\n %s" % film_critics)
	acting_critics = [arg.split("_")[0] for (arg, score) in topic_entities_dict["acting"]["unique_args"]]
	print("acting critics:\n %s" % acting_critics)
	director_critics = [arg.split("_")[0] for (arg, score) in topic_entities_dict["director"]["unique_args"]]
	print("director critics:\n %s" % director_critics)
	writer_critics = [arg.split("_")[0] for (arg, score) in topic_entities_dict
	["writer"]["unique_args"]]
	print("writer critics:\n %s" % writer_critics)

	#effettiva augmentazione (copiatura) delle rece dei figli del movie, dentro unique args del movie, in particolare di quelle che non sono già presenti
	for i in range(nr_critics):
		critic_id = str(i)
		pos_votes = 0
		neg_votes = 0
		if critic_id not in film_critics:
			#se c'è l'id str(i) di una critica non associato al movie 
			if critic_id in acting_critics:
				#ma l' id è associato a una review in acting (che è poi delle entities), allora estraggo la polarità di quella critica, se è positiva conta come voto positivo, se è negativa come voto negativo
				polarity = find_polarity_of_critic_in_args(critic_id, topic_entities_dict["acting"]["unique_args"])
				#print("questa critica ha polartà %.4f" % float(polarity))
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1

			if critic_id in director_critics:
				#print("critic id %s è in driector_critics ma non in film_critics"% critic_id)
				#idem se critica è nel direttore
				polarity = find_polarity_of_critic_in_args(critic_id, topic_entities_dict["director"]["unique_args"])
				#print("questa critica ha polartà %.4f" % float(polarity))
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1
				#print("stampo topic entities: %s" % topic_entities_dict)
			if critic_id in writer_critics:
				#o nel writer
				polarity = find_polarity_of_critic_in_args(critic_id, topic_entities_dict["writer"]["unique_args"])
				#print("questa critica ha polartà %.4f" % float(polarity))
				if float(polarity) > 0:
					pos_votes += 1
				else:
					neg_votes += 1

			#Se la critica che è in una key o piu key ha in totale piu voti positivi (cioe piu polarità > 0) vs negativi, allora viene aggiunta all'unique args di movie come (id_critica, polarità=1), in caso contrario (id_critica, polarità = -1), quindi sto AUGMENTANDO dai figli verso il movie
			if pos_votes > neg_votes:
				#print("essendo di piu i voti positivi, appendo a film unique args con voto 1 -- augmento")
				topic_entities_dict["film"]["unique_args"].append((critic_id, 1))
				#print(topic_entities_dict)
			elif neg_votes > pos_votes:
				#print("essendo di piu i voti negativi, appendo a film unique args con voto 1 -- augmento")
				topic_entities_dict["film"]["unique_args"].append((critic_id, -1))


	#acting entities contiene tutte le rece di acting e figli
	#acting_critics solo gli id delle rece suddette
	#in critics_acting_ent vengono salvati id di quelle rece che sono specificatamente degli attori (visto che li ciclo), quindi dei nodi figli di acting
	acting_entities = topic_entities_dict["acting"]["entities"]
	critics_acting_ent = dict()
	for ent in acting_entities:
		#print("sto ciclando %s: "% ent)
		ent_critics = [arg.split("_")[0] for (arg, score) in acting_entities[ent]["unique_args"]]
		duplicates = set([x for x in ent_critics if ent_critics.count(x) > 1])
		critics_acting_ent[ent] = set(ent_critics)
		#print("critics_acting_ent: %s" % critics_acting_ent[ent])

	acting_critics = [arg.split("_")[0] for (arg, score) in topic_entities_dict["acting"]["unique_args"]]
	print("acting_critics: %s" % acting_critics)
	
	for i in range(nr_critics):
		if str(i) not in acting_critics:
			#se un certo numero non è tra  gli id delle review sugli attori
			#print("%s not in acting_critics" % str(i))
			ents = []
			#ciclo gli attori
			for ent in critics_acting_ent.keys():
				if str(i) in critics_acting_ent[ent]:
					print("%s in critics_acting_ent e lo appendo a ents" % str(i))
					ents.append(ent)
			if len(ents) == 1:
				polarity = find_polarity_of_critic_in_args(str(i), topic_entities_dict["acting"]["entities"][ents[0]]["unique_args"])
				print("ents ha lunghezza 1 e lo appendo a topic_entities_dict")
				topic_entities_dict["acting"]["unique_args"].append((str(i), polarity))
			elif len(ents) > 1:
				print("ents ha lunghezza >1 e lo appendo a topic_entities_dict")
				pos_votes = 0
				neg_votes = 0
				for ent in ents:
					if str(i) in critics_acting_ent[ent]:
						polarity = find_polarity_of_critic_in_args(str(i), topic_entities_dict["acting"]["entities"][ents[0]]["unique_args"])
						if float(polarity) > 0:
							pos_votes += 1
						else:
							neg_votes += 1

				if pos_votes > neg_votes:
					topic_entities_dict["acting"]["unique_args"].append((str(i), 1))
				elif neg_votes > pos_votes:
					topic_entities_dict["acting"]["unique_args"].append((str(i), -1))

	#print("stampo topic entities dict finale")
	#print("stampo topic entities dopo  il for: %s " % topic_entities_dict)
	return topic_entities_dict


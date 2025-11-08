from functools import reduce
from operator import mul
import math
'''
listAnsPref = {'keysPreferences': ['writer>acting', 'acting>themes', 'themes>director'], 'entities': {'acting': ['Angelina Jolie>Johnny Depp', 'Johnny Depp>Anne Hathaway'], 'themes': ['']}}
list_keys= {0: 'director', 1: 'writer', 2: 'acting', 3: 'themes'}
list_entities_preferences= {'acting': {0: 'Johnny Depp', 1: 'Angelina Jolie', 2: 'Brad Pitt', 3: 'Anne Hathaway'}, 'themes': {0: 'Power', 
1: 'Revenge', 2: 'Love', 3: 'Betrayal'}}

atts_btw_entities_children={}
atts_between_keys={}
#TRANSFORMING PREFERENCES IN ATTACKS
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
        #print(atts_btw_entities_children[entity][entityValue])
  
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

print("prima di tutto : %s"%atts_between_keys)
atts_between_keys=sorted(atts_between_keys.items(), key= lambda x: len(x[1]), reverse=False)
print("dopo sorted: %s" %atts_between_keys)
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
'''

def strength_aggregation_euler(arg_scores):
	return sum(arg_scores)

def strength_aggregation_dfquad(arg_scores):
	length = len(arg_scores)
	if length == 0:
		return 0
	else:
		return recursive_function_dfquad(arg_scores)


def recursive_function_dfquad(arg_scores):
	prod = [1-score for score in arg_scores]
	return 1 - reduce(mul, prod, 1)

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
	

def superfunction(semantic, base_score, att, supp):
	if semantic == "dfquad":
		att = strength_aggregation_dfquad(att)
		print("fatt: %s"%str(att))
		supp = strength_aggregation_dfquad(supp)
		print("fsupp: %s"%str(supp))
		if att == supp:
			return base_score
		elif att > supp:
			return base_score - base_score*abs(supp-att)
		else:
			print(base_score + (1-base_score)*abs(supp-att))
			return base_score + (1-base_score)*abs(supp-att)
	elif semantic == "quad":
		att = strength_aggregation_att_quad(base_score,att)
		print("fatt: %s"% str(att))
		supp = strength_aggregation_sup_quad(base_score,supp)
		print("fsupp: %s"% str(supp))
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

print("att  è 1")
print(superfunction("dfquad", 1.0, [1.0], []))
print(superfunction("quad", 1.0, [1.0], []))
print(superfunction("euler", 1.0, [1.0], []))
print("supp  è 1")
print(superfunction("dfquad", 1.0, [], [1.0]))
print(superfunction("quad", 1.0, [], [1.0]))
print(superfunction("euler", 1.0, [], [1.0]))

#print(superfunction("quad", 0.1, [0.4], [0.2]))
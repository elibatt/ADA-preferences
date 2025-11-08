import numpy as np

def firstMethod(inequalities):
    left_side_letters = []
    right_side_letters = []
    letters=['a','b','c','d','e','f']   
    for inequality in inequalities:
        left, right = inequality.split('>')
        left_side_letters.append(left)
        right_side_letters.append(right)


    preferred = np.setdiff1d(left_side_letters, right_side_letters)

    my_list = [[] for _ in range(len(letters))]
    for pref in preferred:
        my_list[0].append(pref)
    print(my_list[0])

    for i in range(len(my_list)):
        if len(my_list[i]) != 0:
            indicilist=[]
            for elemento in my_list[i]:
                indici = [i for i, x in enumerate(left_side_letters) if x == elemento]
                for indie in indici:
                    indicilist.append(indie)
            
            for indice in indicilist:
                if right_side_letters[indice] not in my_list[i+1]:
                    my_list[i+1].append(right_side_letters[indice])
            print(my_list[i+1])
            
        else:
            break

    for i in range(len(my_list)-1):
        print(i)
        if len(my_list[i+1])!=0:
            for elem in my_list[i+1]:
                if elem in my_list[i]:
                    my_list[i].remove(elem)
            
    print(my_list)

def fromPrefToLevels(inequalities):
    left_side_letters = []
    right_side_letters = [] 
    for inequality in inequalities:
        left, right = inequality.split('>')
        left_side_letters.append(left)
        right_side_letters.append(right)


    preferred = np.setdiff1d(left_side_letters, right_side_letters)

    my_list = []
    my_list.append(list(preferred))
    isboolean= True
    i=0
    while isboolean:
        
        indicilist=[]
        for elemento in my_list[i]:
            indici = [i for i, x in enumerate(left_side_letters) if x == elemento]
            for indie in indici:
                indicilist.append(indie)
        if len(indicilist)!=0:
            templist=[]
            for indice in indicilist:
                if right_side_letters[indice] not in templist:
                    templist.append(right_side_letters[indice])
            my_list.append(templist)
            #print(my_list[i+1])
            i=i+1
        else:
            isboolean=False
            


    for i in range(len(my_list)-1):
        if len(my_list[i+1])!=0:
            for elem in my_list[i+1]:
                if elem in my_list[i]:
                    my_list[i].remove(elem)
            
    #print(my_list)
    return my_list

def calculate_w_j_roc(n, j):
    r_values = list(range(1, n + 1))
    sum=0
    for k in range(j,n):
        sum = sum + 1/r_values[k]
    w_j_roc= sum/n
    #print(w_j_roc)
    return w_j_roc
def calculate_roc_weights(n):
    weightList=[]
    for i in range(0,n):
        weightList.append(round(calculate_w_j_roc(n,i),2))
   # print(weightList)
    return weightList

#listaKeys OR listaEntity1 OR listaEntity2..
def fromLevelsToWeights(listOfLevels, listComplete):
    weights_dict={}
    #print(listOfLevels)
    #ROC methods
    listaFlattened=[]
   
    if is_nested(listOfLevels):  
        listaFlattened = custom_flatten(listOfLevels)
        #print(listaFlattened)
    else:
        listaFlattened = listOfLevels
    elementiMancanti=(list(set(listComplete)-set(listaFlattened)))
    #print("lista flattened: %s, len: %d" % (listaFlattened, len(listaFlattened)))
    
    #("elementiMancanti: %s"%elementiMancanti)

    weightsLista =calculate_roc_weights(len(listaFlattened))
    #print("weightsLista : %s" % weightsLista)
    
    if elementiMancanti:
        for elem in elementiMancanti:
            if weightsLista:
                length= len(weightsLista)
                #weights_dict[elem] =  (1 + weightsLista[length-2])/2
                weights_dict[elem] = 1
            else:
                #se la lista vuota perchè non c'è neanche una preferenza  tra questi sibling nodes, allora lascio il peso di tutti i sibling nodes aka elementi mancanti a 1
                weights_dict[elem] = 1
    for i in range(0, len(listOfLevels)):
            if isinstance(listOfLevels[i], list):
                if i!=0:
                    for item in listOfLevels[i]:
                        weights_dict[item] = weightsLista[i-1]
                else:
                    for item in listOfLevels[i]:
                        weights_dict[item] = 1
            else:
                if i!=0:
                    weights_dict[listOfLevels[i]] = weightsLista[i-1]
                else:
                    weights_dict[listOfLevels[i]] = 1
    
    #print(weights_dict)
    return weights_dict
    

def custom_flatten(input_list):
    flattened_list = []
    for item in input_list:
        if isinstance(item, list):
            flattened_list.extend(item)
        else:
            flattened_list.append(item)
    return flattened_list

def is_nested(input_list):
    return any(isinstance(item, list) for item in input_list)

def fromLevelsToWeightsBinary(levels, complete):
    weights_dict={}
    seen=set()
    if levels == []:
        for elem in complete:
            weights_dict[elem]=1
    else:
        for item in levels[0]:
            seen.add(item)
            weights_dict[item]=1
        for item in levels[1]:
            seen.add(item)
            #DEFINIZIONE DELTA
            weights_dict[item]=0.75
        for elem in complete:
            if elem not in seen:
                weights_dict[elem]=1
    return weights_dict

if __name__ == "__main__":
    
    #inequalities=['a>b', 'a>c', 'd>b', 'c>e']
    #inequalities=['a>b', 'a>c', 'c>b', 'b>e', 'c>d', 'd>f']
    inequalities=['a>b', 'c>d']
    #calculate_roc_weights(5)
    print(fromLevelsToWeightsBinary(fromPrefToLevels(inequalities),['a','b','c','d', 'e']))
    #fromLevelsToWeights([['Cillian Murphy', 'Johnny Depp'], 'Emily Blunt'], ['Cillian Murphy', 'Robert Downey Jr.', 'Emily Blunt', 'Johnny Depp'])
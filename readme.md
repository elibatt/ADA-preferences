# ROTTEN TOMATOES 
## What is the point of this code?

This code was originally written in 2019 in relation to the paper "Extracting Dialogical Explanations for Review Aggregations with Argumentative Dialogical Agents" by Cocarascu, Rago, Toni, and it also contains some new preference-related features added in 2023. The main idea of the code is to build a QBAF extracted from the aggregation of reviews about a movie. In particular, we use the website "Rotten Tomatoes" to retrieve the reviews and to compare the obtained strength with the TomatometerScore (see [Rotten Tomatoes](https://www.rottentomatoes.com/)).

Note that, since most of this code is old (2019), some functionalities do not work (for example, the links have changed). This document describes the functionalities that work.

### Two possibilities
More in detail, this code presents two main possibilities:
* Calculate the base score/strengths of the arguments and determine the attacks/supports of an argumentation framework whose structure is _already existing_. The structure of an AF is stored in a JSON file; some already existing AF JSON files are in the folder _RT/af/original_. Warning: these files do not have the final structure required by the code to calculate everything correctly. In fact, if you run one of them, you will obtain very different results from the ones saved in the files "all_sent_dfquad_sent.jsonl" and similar. The AF files to be taken into consideration, instead, are in _RT/af/2023_ folder (the code automatically considers this folder for the moment). 

* Calculate the base score/strengths of the nodes and determine the attacks/supports of an argumentation framework that is _created during code execution_, about a certain movie. The movie could be one whose title exists in the file _rt_bo_films.pkl_, or one you want to search and analyze on the website.  


### General code execution

1) To execute the code, from the terminal, you have to access the folder **critics** and then run the file **rt_films.py**. 
2) The code asks you which type of gradual semantics you want to use: dfquad/quad/euler; then it asks you if you want to use sentiment analysis or NLP. Type "**sent**", since NLP does not work at the moment.
3) The system asks you if you want to search for a specific movie on the website or analyze movies chosen by the system. The second option leads to the analysis of the 22 titles contained in  the file _rt_bo_films.pkl_. The first one requires you to insert the name and year of the movie you want, and then it checks if the URL associated with that title and year (or just the title) exists. If it exists, it goes to point 4), otherwise it tells you that the movie has not been found on the RT website.
4) Once the URL has been found in _rt_bo_films.pkl_ or directly by the system if you inserted the name and year of the movie, then the code extracts from Rotten Tomatoes website the actual value of the TomatometerScore for that movie, and the top critics' reviews (until the "load more" button).
5) At this point:
* if the related AF file doesn't already exist in the _RT/af/original_ folder, the procedure is described in section "Creating the content of the new QBAF files".
* if the related AF file already exists, then the following procedure is the one in section "Reading the existing AF file"

### Creating the content of the new QBAF files
1) First of all, the code extracts sentences from the collected reviews. Then, reading the HTML of the website page, it extracts the director, the writer (both are supposed to be just one person each), and the actors. 
2) Then it proceeds by creating the effective structure of the JSON file. These are the keys (features): _film_, _director_, _writer_, and _acting_. _Director, writer_, and _acting_ also contain entities (subfeatures). Read the paper to understand the graphical structure (tree) that represents the AF.
3) At this point, through several methods, it assigns each sentence to a certain key or entity. There is also an _augmentation_ phase that copies the entities' reviews inside their related parent key, and finally it also augments all the reviews inside the keys _director_, _writer_, _acting_ into the key _film_.
4) Now the JSON file (nameOfFilm year.json) is completed and therefore saved in _RT/af/2023_; it is then used to calculate the quantitative elements of the QBAF, so the base scores and the strengths. 
5) At this point, the system asks you if you want to add preferences:
* Without preferences:
6) Within every semantic, first of all, there is the calculation of the base score of _writer_ and _director_ (based on the number of positive and negative votes); since they are meant not to have any child node, the value of their base scores will be equal to the value of their related strengths. Then, for both _acting_ and the entities _actors_, the base score is calculated; from a comparison between positive and negative votes of _acting_ and all the _actors_, the supporters and attackers are determined. Finally base score and the strength of the film are calculated similarly.\
In particular, the py files used here are "semantic_nameOfSemantic_gen.py", in the _critics_ folder; the files "semantic_nameOfSemantic.py", instead, are meant to read the old json files in _RT/af/original_. In fact, the first type of files read "unique_args", while the second type of files read "args".
7) The results are saved in the directory _RT/all_sent_nameOfSemantic_sent.jsonl_  where nameOfSemantic can be "dfquad", "quad", or "euler". In particular, the result is saved as [RT score, calculated strength, movie title].
The other files all_sent_nameOfSemantic_sent and similar, outside the _RT_ folder, are the ones compiled in 2019; obviously, they contain slightly different values for the same movies, since the RT generally changed over the years, and new reviews have been added.

* With preferences:
6) The system asks you to express a preference between a couple of features taken from this list: _acting_, _writer_, _director_, _themes_. If _acting_ and/or _themes_ have at least two child nodes, then the system also lets you insert a related preference. In both cases, if you click "enter", then no preference is considered. If you click "enter" every time the system asks you to insert a preference, then it is like there are no preferences, so the system follows the procedure written above ("Without preferences:").
7) Within every semantic, first of all there's the calculation of the base score of _writer_ and _director_ (based on the number of positive and negative votes) which is multiplied by a proper weight based on the expressed preferences; since they are meant not to have any children nodes, the value of their base scores will be equal to the value of their related strengths. Then, for both _acting_ and the _actors_ entities, the base score is calculated and once again multiplied by proper weights; from a comparison between positive and negative votes of "acting" and all the "actors", the supporters and attackers are determined. Finally base score and the strength of the film are calculated similarly.\
In particular, the py files used here are "semantic_nameOfSemantic_pref.py", in the _critics_ folder; the files "semantic_nameOfSemantic.py", instead, are meant to read the old json files in _RT/af/original_. In fact, the first type of files read "unique_args", while the second type of files read "args".
8) The results are saved in the directory _RT/all_sent_nameOfSemantic_sent_pref.jsonl_  where nameOfSemantic can be "dfquad", "quad", or "euler". In particular, the result is saved as [RT score, calculated strength, movie title].


### Reading the existing AF files
The existing AF file is read, and the strengths are directly calculated with the gradual semantics you have previously chosen. Basically, the procedure directly starts at point 5 of the previous section.

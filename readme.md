# Building argumentation frameworks from Rotten Tomatoes reviews 
## What is the point of this code?

This code was originally written in 2019 in relation to the paper "Extracting Dialogical Explanations for Review Aggregations with Argumentative Dialogical Agents" by Cocarascu, Rago, Toni (https://doi.org/10.5555/3306127.3331830) and it also contains some new preference-related features added in 2023 (see the paper "Integrating User Preferences into Gradual Bipolar Argumentation for Personalised Decision Support" by Battaglia, Baroni, Rago and Toni, https://doi.org/10.1007/978-3-031-76235-2_2). The main idea of the code is to build a QBAF (Quantitative Bipolar Argumentation Framework) extracted from the aggregation of reviews about a movie. In particular, we use the website "Rotten Tomatoes" to retrieve the reviews and to compare the obtained argumentative strength with the TomatometerScore (see [Rotten Tomatoes](https://www.rottentomatoes.com/)).

Note that, since most of this code is rather old (2019), some functionalities are not working properly at the moment (for example, some hyperlinks have changed). This document describes the functionalities that work.

### Main functions
More in detail, this code presents two main functions:
* Computing the base score and strengths of the arguments and determining the attackers or supporters in an Argumentation Framework (AF) whose structure already exists. The structure of an AF is stored in a JSON file and the AF files to be taken into consideration are in the _RT/af/2023_ folder (the code automatically considers this folder at the moment). 

* Computing the base score and strengths of the arguments and determining the attackers or supporters of an argumentation framework that is _created at runtime_, about a certain movie. The movie can be one whose title is included in the file _rt_bo_films.pkl_, or one you want to search and analyze on the website.  


### General code execution

1) To run the code, from the terminal, you have to access the folder **critics** and then run the file **rt_films.py**. 
2) The code asks you which type of gradual argumentation semantics you want to use among three options: dfquad/quad/euler; then it asks you whether you want to use sentiment analysis or NLP. Type "**sent**" for sentiment analysis, since NLP does not work at the moment.
3) The system asks you if you want to search for a specific movie on the website or analyze movies already available in the system.  The first option requires you to enter the name and year of the desired movie, and then it checks if the URL associated with that title and year (or just the title) exists. If it exists, it goes to point 4), otherwise, it tells you that the movie has not been found on the Rotten Tomatoes website. The second option leads to the analysis of the 22 titles contained in  the file _rt_bo_films.pkl_ and executes point 4) for each of them.
4) The code extracts from the Rotten Tomatoes website the current value of the TomatometerScore for the movie, and the top critics' reviews (namely, those available before the "load more" button).
5) At this point:
* if the corresponding AF file does not already exist in the _RT/af/2023_ folder, the procedure described in section "Creating the content of the new QBAF files" is executed.
* if the corresponding AF file already exists, then the procedure described in the section "Reading the existing AF file" is executed.

### Creating the content of the new QBAF files
1) First of all, the code extracts sentences from the collected reviews. Then, processing the HTML of the website page, it extracts the director, the writer (both are supposed to be exactly one person each), and the actors. 
2) Then it proceeds by creating the structure of the JSON file, including the following keys (features): _film_, _director_, _writer_, and _acting_. The keys _director, writer_, and _acting_ contain further entities representing subfeatures. Please refer to the paper "Extracting Dialogical Explanations for Review Aggregations with Argumentative Dialogical Agents" by Cocarascu, Rago and Toni (https://doi.org/10.5555/3306127.3331830) for more details on the tree structure that represents the AF.
3) At this point, the code assigns each extracted sentence to a certain key or entity. This is followed by  an _augmentation_ phase that recursively copies the reviews from each entity to its parent key, and finally it augments all the reviews present in the keys _director_, _writer_, _acting_, copying them into their parent key _film_.
4) Now the JSON file (nameOfFilm year.json) is completed and therefore saved in _RT/af/2023_ and the code moves to step 5) to compute the quantitative elements of the QBAF, namely the base scores, and the strengths. 
5) At this point, the system asks you if you want to add preferences:
* Without preferences:
6) For each argumentation semantics, base scores are  calculated. Then, on the basis of these values, attackers and supporters are determined.
7) The results are saved in the directory _RT/all_sent_nameOfSemantic_sent.jsonl_  where nameOfSemantic can be "dfquad", "quad", or "euler". In particular, the result for each movie is saved as a triple [RT score, calculated strength, movie title].

* With preferences:
6) The system asks you to express a preference between a couple of features taken from this list: _acting_, _writer_, _director_, _themes_. If _acting_ and/or _themes_ have at least two child nodes, then the system also lets you insert a preference between them. In both cases, if you click "enter", then no preference is considered. If you click "enter" every time the system asks you to insert a preference, then you indicate that there are no preferences, so the system follows the procedure presented above ("Without preferences:").
7) For each argumentation semantics, first of all the base score of _writer_ and _director_ is computed. Then this base score is multiplied by a proper weight based on the expressed preferences. Then, for both entities _acting_ and the _actors_, the base score is computed and once again multiplied by preference-based weights. The roles of supporters and attackers of the various nodes of the AF are then determined. Finally, the base score and the strength of the film are computed in a similar way.
8) The results are saved in the directory _RT/all_sent_nameOfSemantic_sent_pref.jsonl_  where nameOfSemantic can be "dfquad", "quad", or "euler". In particular, the result for each movie is saved as a triple [RT score, calculated strength, movie title].


### Reading the existing AF files
The existing AF file is read, and the strengths are directly computed with the previously selected gradual semantics. Basically, the procedure starts directly at point 5 of the previous section.

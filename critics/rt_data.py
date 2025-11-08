from bs4 import BeautifulSoup
import urllib.request
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json

ROTTEN = 0
FRESH  = 1


def rt_top_critics_reviews_tomatoes(url):
	print("Extracting reviews and TS score")
	#print(url)
	
	content = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(content, "lxml")

	#prendo tutti i testi delle varie recensioni, che erano dentro "review-text" del soup
	#in particolare prendo solo quelli della prima pagina (circa 20), dopo ci sarebbe il LOAD MORE
	'''
	top_critics_reviews = soup.find_all("p", class_="review-text")
	top_critics_reviews = [x.text for x in top_critics_reviews]
	#prendo anche le relative valutazioni "rotten" o "tomatoes", mettendole nell'array tomatoes
	tomatoes=soup.find_all("div",class_="review-data")
	tomatoes = [ROTTEN if "rotten" in str(x) else FRESH for x in tomatoes]
	# print("stampo per vedere se ha preso rotten o fresh o niente")
	# print(tomatoes)
	top_critics_reviews_tomatoes = list(zip(top_critics_reviews, tomatoes))
	#ritorno una lista zippata di [(testoCritica, Rotten/Tomatoes)]
	#print(top_critics_reviews)
	'''
	#inseriamo qua tutte le reviews anche dopo il load button, estratte manualmente con chatgpt
	top_critics_reviews_tomatoes=[
    ("As lumbering as its title, Pirates of the Caribbean: Dead Men Tell No Tales will leave you running for the plank, or the exit.", 0),
    ("Oh, if only dead men told no tales. Then we might have avoided this fifth Pirates of the Caribbean adventure, which fails to justify its own existence in any way whatsoever.", 0),
    ("There are lame, crude jokes about bottoms and horologists. There is $230 million of CG effects that never look like anything more than pixels. And then there's Depp's panto drunkenness.", 0),
    ("The subtitle of the new Pirates of the Caribbean movie is 'Dead Men Tell No Tales.' The moral of the movie, alas, is that the same cannot be said of dead franchises.", 0),
    ("If being dull, gruesome and obnoxiously loud weren't enough, Dead Men Tell No Tales makes sure to get in a blast of sexism, too.", 0),
    ("The plot is nominal, and so are the film's first 90 minutes (Paul McCartney cameo included).", 0),
    ("The bounty of bawdy bits feel borrowed from Benny Hill ('No woman's ever handled my Herschel before!' says a stunned telescope operator), while the slapstick violence skews toward the Three Stooges.", 0),
    ("Dead Men shows life when there are big action scenes. If 30 minutes of jumbled mythology and cheesy writing had been cut, the movie would have had an action beat as driving as the heart-pounding score by Geoff Zanelli.", 1),
    ("Is this really only the fifth entry in the Pirates film franchise? It feels like the 50th. Except for Javier Bardem, who brings a dollop of fresh mischief to this paycheck party, Dead Men has all the flavor of rotting leftovers.", 0),
    ("Directors Joachim Rønning and Espen Sandberg work up a stormy sea-parting finale that is better than anything in The Ten Commandments. Again, the trick to enjoying this film is to expect nothing.", 1),
    ("I daresay it is the very best fourth sequel ever made to a movie based on a 50-year-old theme park ride.", 0),
    ("There are no new treasures to be found in this installment, which is dragged down by the anchor of a prescribed franchise blueprint.", 0),
    ("This amusing buccaneering adventure, fifth time to sea, isn't ready to walk the plank just yet.", 1),
    ("But even with a not-so-subtle passing of the torch hinting at potential future sequels or spinoffs, here's hoping this really is the last cruise of the Black Pearl.", 0),
    ("Pirates of the Caribbean: Dead Men Tell No Tales is an egregious example of bloated franchise filmmaking, an exercise stuffed with idiocy and sorely lacking in fun.", 0),
    ("To accuse Depp of phoning it in would be to flatter him. In this fifth run-out as Sparrow he barely has the energy to tweet it in.", 0),
    ("Now in its fifth outing and trying to press reset after an unnecessary fourth movie, Depp's campy performance in that role is losing crucial energy and humour.", 0),
    ("We had zero hope for the fifth chapter in the waterlogged Pirates of The Caribbean franchise. And we were wrong. This thing is terrific.", 1),
    ("The fact is, Pirates, you are so insultingly lazy it's a wonder anyone puts up with you at all. If you were a person, I'd have thrown you out the house years ago.", 0),
    ("As expected, there's little subtlety in Salazar's Revenge. It's over-the-top comedy and loud action, unnecessarily salacious jokes and copied scenes from the original.", 0),
    ("Productions like this come and go, crumbling tentpoles to be replaced by new timber, but they are self-fulfilling prophecies, and dire ones, about the future of the theatrical movie business. They're accomplices in a soul heist.", 0),
    ("Boring. That's how I'd describe the latest Pirates film. Apparently, live men tell leaden tales like this, overstuffed with subplots and uninteresting characters. I'd rather walk the plank than spend another two hours with Jack Sparrow and company.", 0),
    ("Maybe if I watched it again, Dead Men would make more sense, but here's the thing: I didn't get Curse of the Black Pearl all in one go either, but I knew I wanted to watch it again.", 0),
    ("Popcorn munchers and franchise fans will find plenty to like.", 1),
    ("Its pleasures are so meager, its delight in its own inventions so forced and false, that it becomes almost the perfect opposite of entertainment.", 0),
    ("[It] tries to turn back time, seeking to replicate the first 2003 film's chemistry. That attempt to swim against the tide doesn't entirely work, but at least delivers moments that fleetingly jolt this... fifth installment to sporadic life.", 0),
    ("I found Dead Men Tell No Tales to be passably fun and certainly no harder to watch than any of the better-pedigreed blockbusters this year.", 1),
    ("'Pirates of the Caribbean: Dead Men Tell No Tales' remains true to its Disney theme park roots. Loud, overstimulating and hard to take in all in one sitting, it feels like the vacation that you'll need a vacation from.", 0),
    ("Depp, who once was among the most risk-taking actors in film, seems to be merely going through the motions.", 0),
    ("Worth it for the astonishing open set-piece, but the rest is hot garbage.", 0),
    ("How was the movie? It was okay, I guess! Second best Pirates of the Caribbean movie! With a bullet! (For the record, that's not really a compliment.)", 0),
    ("Better to scupper this armada of waterlogged mediocrity as soon as possible.", 0),
    ("It's stuffed to the gills with effects executed by the highest-paid artists and technicians in the business. But it's still a sorry spectacle.", 0),
    ("Been there, plundered that.", 0),
    ("The dead tell a tale in the latest Pirates of the Caribbean movie, but unfortunately that tale is erratic, filled with holes, peppered with far-too-convenient plot points and tarnished by over-the-top situations ...", 0),
    ("A cartoonish Depp and a muddled plot send this fifth 'Pirates' film to the bottom.", 0),
    ("Does the world really need a fifth Pirates of the Caribbean movie? Is there a limit to the amount of times a Hollywood studio can yell, 'Captain Jack is back!' before the collective audience replies: 'Who cares?!'", 0),
    ("Dead men may tell no tales, but bored audience members do. Open bar, anyone? Can we toast the end of this franchise? Please?", 0),
    ("A surprisingly sprightly and enjoyable late entry in the Pirates Of The Caribbean franchise.", 1),
    ("We have Oscar winners Geoffrey Rush and Javier Bardem hamming it up beneath all the makeup and CGI trickery, and that's a hoot. Bardem's Salazar is a genuinely frightening creation.", 1),
    ("Ever ridden an amusement-park ride once and it was really fun and exciting? And then you rode it again and again and it got less fun, until finally you wondered why you liked it in the first place? And here we are.", 0),
    ("Whatever charm and charisma Johnny Depp once had is well and truly lost at sea.", 0),
    ("Five films in, Pirates still leaves you feeling a lot like the Magic Kingdom ride it's so famously inspired by: alternately thrilled, exhausted, and seriously regretting that last funnel cake.", 1),
    ("A mostly fun partial reset, but this series needs to slip its moorings and make for new horizons.", 1),
    ("The franchise has lost a bit of its luster with every successive installment, but never has a 'Pirates' film felt this inessential, this depressingly pro forma.", 0),
    ("Ghost sharks should have been added a long time ago.", 1)
]




	return (top_critics_reviews_tomatoes)



#updated August 2024
def rt_writers_actors_directors(url):
	content = urllib.request.urlopen(url+"/cast-and-crew").read()
	soup = BeautifulSoup(content, "html.parser")

	
	ems_id=0

	# Initialize lists to store names
	directors = []
	screenwriters = []
	actors = []

	# Loop through all cast-and-crew cards to extract information
	for card in soup.find_all('cast-and-crew-card'):
		role = card.find('rt-text', {'slot': 'credits'}).text.strip()
		name = card.find('rt-text', {'context': 'label'}).text.strip()

		# Identify the role and add the name to the appropriate list
		if "director" in role.lower():
			directors.append(name)
		elif "screenwriter" in role.lower():
			screenwriters.append(name)
		elif "actor" in role.lower():
			actors.append(name)

	# Output the results
	print("Directors:", directors)
	print("Screenwriters:", screenwriters)
	print("Actors:", actors[:4])  # Limit to first 4 actors
	return [directors[0],screenwriters[0],actors]



def rt_top_critics_score(url):
	#print("sono in rt top critics score")
	print("url passato a rt top critics score: %s" % url)

	content = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(content, "lxml")
	
	try:
		# Find the element containing the score
		score_element = soup.find("rt-text", {"slot": "criticsScore"})

		# Extract the text and remove the '%' sign
		if score_element:
			score = int(score_element.text.strip().replace('%', ''))
			

		return score
	except Exception:
		return None


if __name__ == "__main__":
	url = "https://www.rottentomatoes.com/m/barbie/reviews?type=top_critics"
	print("passo url: %s"% url)
	listazippata= rt_top_critics_reviews_tomatoes(url)
	'''
	print("lunghezza lista zippata")
	print(len(listazippata))
	'''
	url = url.split("reviews")[0]
	print("nuovo url: %s" % url)
	url="https://www.rottentomatoes.com/m/barbie#cast-and-crew"
	'''
	writer = rt_writer(url)
	print (writer)
	'''
	everyone = rt_writers_actors_directors(url)
	print(everyone[0][1])

	'''
	top_critics_score = rt_top_critics_score(url)
	print(top_critics_score)
	'''
	
	
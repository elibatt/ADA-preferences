from bs4 import BeautifulSoup
import urllib.request

#the URLs should be changed - 2023
def rt_box_office(url):
	content = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(content, "lxml")

	box_office_films = []
	box_office_films = soup.find_all("td", class_="left")
	box_office_films = ["https://www.rottentomatoes.com/" + x.find("a")["href"] + "/reviews/?type=top_critics" for x in box_office_films]
	return box_office_films


def rt_top_movies(url):
	content = urllib.request.urlopen(url).read()
	soup = BeautifulSoup(content, "lxml")

	top_movies = soup.find("table", class_="table").find_all("a", class_="unstyled articleLink")
	top_movies = ["https://www.rottentomatoes.com/" + x["href"] + "/reviews/?type=top_critics" for x in top_movies]

	return (top_movies)


if __name__ == "__main__":
	box_office_films = rt_box_office("https://www.rottentomatoes.com/browse/box-office/?rank_id=0&country=us")
	print (box_office_films)

	box_office_films = rt_box_office("https://www.rottentomatoes.com/browse/box-office/?rank_id=13&country=us")
	print (box_office_films)

	top_movies = rt_top_movies("https://www.rottentomatoes.com/top/bestofrt/")
	print (top_movies)
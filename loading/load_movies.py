import xlrd

actor_file = 'files/actor.xlsx'
actress_file = 'files/actress.xlsx'
API_KEY = 'c7f2c862'

class Spreadsheet:

	def __init__(self, url, sheet, actor_column, movie_column, year_column):
		self.workbook = xlrd.open_workbook(url)
		self.sheet = sheet
		self.worksheet = self.workbook.sheet_by_name(sheet)
		self.num_rows = self.worksheet.nrows
		self.actor_column = actor_column
		self.movie_column = movie_column
		self.year_column = year_column

	def get_movies(self):
		movies = []
		for row in range(0, self.num_rows):
			actor = self.get_cell(row, self.actor_column).strip()
			movie = self.get_cell(row, self.movie_column).strip()
			year = str(self.get_cell(row, self.year_column)).split("/")[0].split(".")[0]

			if movie != "" and "(" not in movie:
				movies.append((movie, year))

		return movies

	def get_actors(self):
		actors = []
		for row in range(0, self.num_rows):
			actor = self.get_cell(row, self.actor_column).strip()
			if actor != "":
				actors.append(actor)
		return actors

	def get_cell(self, curr_row, curr_cell):
		return self.worksheet.cell_value(curr_row, curr_cell)


def uniquify_movies(movies):
	unique_movies = []
	for movie in movies:
		if movie not in unique_movies:
			unique_movies.append(movie)
	return unique_movies


def get_all_movies():
	spreadsheet_data_claim = Spreadsheet(actress_file, 'Sheet1', 0, 1, 2)
	actress_movies = spreadsheet_data_claim.get_movies()
	print (len(actress_movies))

	spreadsheet_data_claim = Spreadsheet(actor_file, 'Sheet1', 0, 1, 2)
	actor_movies = spreadsheet_data_claim.get_movies()
	print (len(actor_movies))

	movies = actress_movies + actor_movies
	return movies


def get_all_actors():
	spreadsheet_data_claim = Spreadsheet(actress_file, 'Sheet1', 0, 1, 2)
	actresses = spreadsheet_data_claim.get_actors()
	print ('actresses %d' % len(actresses))

	spreadsheet_data_claim = Spreadsheet(actor_file, 'Sheet1', 0, 1, 2)
	actors = spreadsheet_data_claim.get_actors()
	print ('actors %d' % len(actors))

	all_actors = actresses + actors
	return all_actors
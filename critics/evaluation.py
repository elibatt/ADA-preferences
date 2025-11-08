from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import classification_report
from math import sqrt
import jsonlines
import os

def read_data(data_file):
	data = []
	with jsonlines.open(data_file) as reader:
		for obj in reader:
			data.append(obj)
	return data


def evaluate(data):
	score_af = []
	score_rt = []

	cleaned_data = []
	for line in data:
		if line[0] != None:
			cleaned_data.append(line)
	data = cleaned_data
	print ("size clean data %d" % len(data))

	for line in data:
		score_rt.append(int(line[0]))
		score_af.append(round(int(line[1])))


	tomatoes_rt = ['F' if x >= 60 else 'R' for x in score_rt]
	tomatoes_af = ['F' if x >= 60 else 'R' for x in score_af]
	print (classification_report(tomatoes_rt, tomatoes_af))


	rmse = sqrt(mean_squared_error(score_rt, score_af))
	print ("original rmse %f" % rmse)

	mae = mean_absolute_error(score_rt, score_af)
	print ("original mae %f" % mae)

	score_rt = [int(x/10) if x!=100 else 9 for x in score_rt]
	score_af = [int(x/10) if x!=100 else 9 for x in score_af]

	rmse = sqrt(mean_squared_error(score_rt, score_af))
	print ("point rmse %f" % rmse)

	mae = mean_absolute_error(score_rt, score_af)
	print ("point mae %f" % mae)

	score_af = []
	score_rt = []
	for line in data:
		if int(line[0]) != 100 and int(line[0]) != 0:
			score_rt.append(int(line[0]))
			score_af.append(round(int(line[1])))

	print ("size removed 0/100RT original rmse %d" % len(score_af))

	rmse = sqrt(mean_squared_error(score_rt, score_af))
	print ("removed 0/100RT original rmse %f" % rmse)

	mae = mean_absolute_error(score_rt, score_af)
	print ("removed 0/100RT original mae %f" % mae)

	score_rt = [int(x/10) if x!=100 else 9 for x in score_rt]
	score_af = [int(x/10) if x!=100 else 9 for x in score_af]

	rmse = sqrt(mean_squared_error(score_rt, score_af))
	print ("removed 0/100RT point rmse %f" % rmse)

	mae = mean_absolute_error(score_rt, score_af)
	print ("removed 0/100RT point mae %f" % mae)




if __name__ == "__main__":
	# get the current working directory
	current_working_directory = os.getcwd()
	print(current_working_directory)
	os.chdir('../RT/')
	new_directory= os.getcwd()
	print(new_directory)

	semantics = input("semantics? dfquad/quad/euler ")
	method = input("method? sent/nlp ")
	if semantics == "dfquad":
		if method == "sent":
			data = read_data('all_sent_dfquad_sent.jsonl')
		elif method == "nlp":
			data = read_data('../all_nlp_dfquad_sent.jsonl')
	elif semantics == "quad":
		if method == "sent":
			data = read_data('../all_sent_quad_sent.jsonl')
		elif method == "nlp":
			data = read_data('../all_nlp_quad_sent.jsonl')
	elif semantics == "euler":
		if method == "sent":
			data = read_data('../all_sent_euler_sent.jsonl')
		elif method == "nlp":
			data = read_data('../all_nlp_euler_sent.jsonl')

	evaluate(data)

import pickle
import os


# ('175468', 'tt0246677', '2', 3.3586914561749457, 3.4531621493105087)
# ('175468', 'tt0165361', '3', 3.3586914561749457, 2.2986125530910817)
def calculate_accuracy(file_name, acc_type, rounding):
	data = pickle.load(open(file_name, "rb"))
	total_nr = len(data)
	total_pred = 0
	for i in range(total_nr):
		(user_id, movie_id, true_rating, _, pred_rating) = data[i]
		if acc_type == "exact":
			if int(true_rating) == round(pred_rating):
				total_pred += 1
		if acc_type == "1dif":
			if rounding == "y":
				if abs(int(true_rating) - round(pred_rating)) <= 1:
					total_pred += 1
			else:
				if float(pred_rating)  >= float(true_rating) - 1 and float(pred_rating) <= float(true_rating) + 1:
					total_pred += 1

	return total_nr, float(total_pred)/total_nr


def print_baseline(file_name, acc_type, rounding):
	total_nr, acc = calculate_accuracy(os.path.join("baseline/", file_name), acc_type, rounding)
	print (("alg %s | acc type %s | nr pred %d | acc %f") % (file_name, acc_type, total_nr, acc))



def baseline_algos(rounding):
	for file_name in os.listdir("baseline/"):
		if file_name.endswith(".pkl"):
	    	# print_baseline(file_name, "exact")
			print_baseline(file_name, "1dif", rounding)

def arg_accuracy(file_name, acc_type, rounding):
	data = pickle.load(open(file_name, "rb"))
	total_nr = len(data)
	total_pred = 0
	for i in range(total_nr):
		(true_rating, pred_rating) = data[i]
		if acc_type == "exact":
			if int(true_rating) == round(pred_rating):
				total_pred += 1
		if acc_type == "1dif":
			if rounding == "y":
				if round(pred_rating)  >= true_rating - 1 and round(pred_rating) <= true_rating + 1:
					total_pred += 1
			else:
				if pred_rating  >= true_rating - 1 and pred_rating <= true_rating + 1:
					total_pred += 1

	return total_nr, float(total_pred)/total_nr

if __name__ == "__main__":
	# baseline_algos("y")
	# print ("\n")
	# baseline_algos("n")
	# print (arg_accuracy("predictions.pkl", "1dif", "y"))
	# print (arg_accuracy("predictions.pkl", "1dif", "n"))

	# print (arg_accuracy("predictions_3352_20_10.pkl", "1dif", "y"))
	print (arg_accuracy("predictions_3352_20_10.pkl", "1dif", "n"))
	# print (arg_accuracy("predictions_3352_20_7.pkl", "1dif", "y"))
	print (arg_accuracy("predictions_3352_20_7.pkl", "1dif", "n"))
	# print (arg_accuracy("predictions_3352_20_5.pkl", "1dif", "y"))
	print (arg_accuracy("predictions_3352_20_5.pkl", "1dif", "n"))
	# print (arg_accuracy("predictions_3352_10_5.pickle", "1dif", "y"))
	print (arg_accuracy("predictions_3352_10_5.pkl", "1dif", "n"))
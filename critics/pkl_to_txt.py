import pickle

def pkl_to_txt(pkl_file):
	data = pickle.load(open(pkl_file, "rb"))
	f = open(pkl_file.split(".pkl")[0] + ".txt", 'w')
	for item in data:
		f.write("%s\n" % str(item))


# pkl_to_txt("alien covenant_themes.pkl")
# pkl_to_txt("all eyez on me 2017_themes.pkl")
# pkl_to_txt("fifty shades darker_themes.pkl")
# pkl_to_txt("lady bird_themes.pkl")
# pkl_to_txt("lbj_themes.pkl")
# pkl_to_txt("mother 2017_themes.pkl")
# pkl_to_txt("pirates of the caribbean dead men tell no tales_themes.pkl")
# pkl_to_txt("the foreigner 2017_themes.pkl")
# pkl_to_txt("three billboards outside ebbing missouri_themes.pkl")
# pkl_to_txt("wonder wheel_themes.pkl")

pkl_to_txt("../RT/themes_pkl/a quiet place 2018_themes.pkl")

# pkl_to_txt("RT/themes_pkl/call me by your name_themes.pkl")
# pkl_to_txt("RT/themes_pkl/coco 2017_themes.pkl")
# pkl_to_txt("RT/themes_pkl/et the extraterrestrial_themes.pkl")
# pkl_to_txt("RT/themes_pkl/game night 2018_themes.pkl")
# pkl_to_txt("RT/themes_pkl/get out_themes.pkl")
# pkl_to_txt("RT/themes_pkl/ghost in the shell 2017_themes.pkl")
# pkl_to_txt("RT/themes_pkl/godfather_themes.pkl")
# pkl_to_txt("RT/themes_pkl/i tonya_themes.pkl")
# pkl_to_txt("RT/themes_pkl/inception_themes.pkl")
# pkl_to_txt("RT/themes_pkl/jumanji welcome to the jungle_themes.pkl")
# pkl_to_txt("RT/themes_pkl/la la land_themes.pkl")
# pkl_to_txt("RT/themes_pkl/lawrence of arabia_themes.pkl")
# pkl_to_txt("RT/themes_pkl/moana 2016_themes.pkl")
# pkl_to_txt("RT/themes_pkl/mollys game_themes.pkl")
# pkl_to_txt("RT/themes_pkl/phantom thread_themes.pkl")
# pkl_to_txt("RT/themes_pkl/singin in the rain_themes.pkl")
# pkl_to_txt("RT/themes_pkl/the dark knight_themes.pkl")
# pkl_to_txt("RT/themes_pkl/the greatest showman 2017_themes.pkl")
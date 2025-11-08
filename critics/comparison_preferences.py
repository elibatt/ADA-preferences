import os
import jsonlines

def comparison_strengths(film_title, semantic, contentPreferences, strength):
    filtered_line = ""

    nuova_dir = os.path.join(os.path.dirname(os.getcwd()), 'RT')
    os.chdir(nuova_dir)
    #print(nuova_dir)
    standardFile = "./all_sent_%s_sent.jsonl" % semantic
    with jsonlines.open(standardFile, 'r') as jsonl_f:
            filtered_line = [line for line in jsonl_f if film_title in line]
            #print(filtered_line)
    if filtered_line:
        result = (film_title, contentPreferences, strength , "original: ", filtered_line[0][1])
        with jsonlines.open(('./comparison/comparison_%s.jsonl' %  semantic), mode='a') as writer:
            writer.write(result)

if __name__ == "__main__":
     comparison_strengths("napoleon 2023", "dfquad", "w>t", 56.143359375)
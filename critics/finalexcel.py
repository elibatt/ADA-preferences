import re
from provaexcel import chiamametodi
def extract_sections(text):
    sections = []
    final_print_regex = re.compile(r'FINAL PRINT.*?(film \d+\.\d+)', re.MULTILINE | re.DOTALL)
    matches = final_print_regex.finditer(text)
    for match in matches:
        section = match.group(0).strip()
        sections.append(section)
    return sections

# Example usage:
text='''
Sono in dfquad WEIGHTS
levels list: [['director'], ['writer']]
levels list entities: [['Javier Bardem'], ['Johnny Depp']]
list entity themesis empty
Weights dict keys {'director': 1, 'writer': 0.75, 'acting': 1, 'themes': 1}
Weights dict entities {'acting': {'Javier Bardem': 1, 'Johnny Depp': 0.75, 'Brenton Thwaites': 1, 'Kaya Scodelario': 1, 'Orlando Bloom': 1, 'Kevin R. McNally': 1, 'Golshifteh Farahani': 1, 'Stephen Graham': 1, 'Keira Knightley': 1, 'Martin Klebba': 1, 'Paul McCartney': 1, 'David Wenham': 1, 'Adam Brown': 1, 'Danny Kirrane': 1}, 'themes': {'Legacy': 1, 'Betrayal': 1, 'Adventure': 1}}
base_score_acting_weighted:  0.5
Acting attackers and strength values: ['Javier Bardem', 'Paul McCartney'], [1.0, 1.0]
Acting supporters and strength values: ['Johnny Depp'], [0.75]
att aggregati:  1.0
supp aggregati:  0.75
Themes attackers: ['Legacy'], values: [0.3333333333333333]
Themes supporters: ['Betrayal', 'Adventure'], values: [1.0, 0.3333333333333333]
att aggregati:  0.33333333333333326
supp aggregati:  1.0
printo risultato strength:
0.9166666666666667
Movie atts and strength values: ['writer', 'acting'], [0.75, 0.375]
Movie supps and strength values: ['director', 'themes'], [1.0, 0.9166666666666667]
att aggregati:  0.84375
supp aggregati:  1.0
printo risultato strength:
0.5359375
FINAL PRINT
director 1.0
writer 0.75
JohnnyDepp 0.75
JavierBardem 1.0
PaulMcCartney 1.0
acting 0.375
Legacy 0.3333333333333333
Betrayal 1.0
Adventure 0.3333333333333333
themes 0.9166666666666667
film 0.5359375
Sono in quad WEIGHTS
levels list: [['director'], ['writer']]
levels list entities: [['Javier Bardem'], ['Johnny Depp']]
list entity themesis empty
Weights dict keys {'director': 1, 'writer': 0.75, 'acting': 1, 'themes': 1}
Weights dict entities {'acting': {'Javier Bardem': 1, 'Johnny Depp': 0.75, 'Brenton Thwaites': 1, 'Kaya Scodelario': 1, 'Orlando Bloom': 1, 'Kevin R. McNally': 1, 'Golshifteh Farahani': 1, 'Stephen Graham': 1, 'Keira Knightley': 1, 'Martin Klebba': 1, 'Paul McCartney': 1, 'David Wenham': 1, 'Adam Brown': 1, 'Danny Kirrane': 1}, 'themes': {'Legacy': 1, 'Betrayal': 1, 'Adventure': 1}}
base_score_acting_weighted:  0.5
Acting attackers and strength values: ['Javier Bardem', 'Paul McCartney'], [1.0, 1.0]
Acting supporters and strength values: ['Johnny Depp'], [0.75]
Themes attackers: ['Legacy'], values: [0.3333333333333333]
Themes supporters: ['Betrayal', 'Adventure'], values: [1.0, 0.3333333333333333]
Movie atts and strength values: ['writer', 'acting'], [0.75, 0.4375]
Movie supps and strength values: ['director', 'themes'], [1.0, 0.75]
FINAL PRINT
director 1.0
writer 0.75
JohnnyDepp 0.75
JavierBardem 1.0
PaulMcCartney 1.0
acting 0.4375
Legacy 0.3333333333333333
Betrayal 1.0
Adventure 0.3333333333333333
themes 0.75
film 0.531640625
Sono in euler WEIGHTS
levels list: [['director'], ['writer']]
levels list entities: [['Javier Bardem'], ['Johnny Depp']]
list entity themesis empty
Weights dict keys {'director': 1, 'writer': 0.75, 'acting': 1, 'themes': 1}
Weights dict entities {'acting': {'Javier Bardem': 1, 'Johnny Depp': 0.75, 'Brenton Thwaites': 1, 'Kaya Scodelario': 1, 'Orlando Bloom': 1, 'Kevin R. McNally': 1, 'Golshifteh Farahani': 1, 'Stephen Graham': 1, 'Keira Knightley': 1, 'Martin Klebba': 1, 'Paul McCartney': 1, 'David Wenham': 1, 'Adam Brown': 1, 'Danny Kirrane': 1}, 'themes': {'Legacy': 1, 'Betrayal': 1, 'Adventure': 1}}
base_score_acting_weighted:  0.5
Acting attackers and strength values: ['Javier Bardem', 'Paul McCartney'], [1.0, 1.0]
Acting supporters and strength values: ['Johnny Depp'], [0.75]
Themes attackers: ['Legacy'], values: [0.3333333333333333]
Themes supporters: ['Betrayal', 'Adventure'], values: [1.0, 0.3333333333333333]
Movie atts and strength values: ['writer', 'acting'], [0.75, 0.3439768846932717]
Movie supps and strength values: ['director', 'themes'], [1.0, 0.8560244963948465]
FINAL PRINT
director 1.0
writer 0.75
JohnnyDepp 0.75
JavierBardem 1.0
PaulMcCartney 1.0
acting 0.3439768846932717
Legacy 0.3333333333333333
Betrayal 1.0
Adventure 0.3333333333333333
themes 0.8560244963948465
film 0.5939815758143068
Sono in energy WEIGHTS
levels list: [['director'], ['writer']]
levels list entities: [['Javier Bardem'], ['Johnny Depp']]
list entity themesis empty
Weights dict keys {'director': 1, 'writer': 0.75, 'acting': 1, 'themes': 1}
Weights dict entities {'acting': {'Javier Bardem': 1, 'Johnny Depp': 0.75, 'Brenton Thwaites': 1, 'Kaya Scodelario': 1, 'Orlando Bloom': 1, 'Kevin R. McNally': 1, 'Golshifteh Farahani': 1, 'Stephen Graham': 1, 'Keira Knightley': 1, 'Martin Klebba': 1, 'Paul McCartney': 1, 'David Wenham': 1, 'Adam Brown': 1, 'Danny Kirrane': 1}, 'themes': {'Legacy': 1, 'Betrayal': 1, 'Adventure': 1}}
base_score_acting_weighted:  0.5
Acting attackers and strength values: ['Javier Bardem', 'Paul McCartney'], [1.0, 1.0]
Acting supporters and strength values: ['Johnny Depp'], [0.75]
24
Themes attackers: ['Legacy'], values: [0.3333333333333333]
Themes supporters: ['Betrayal', 'Adventure'], values: [1.0, 0.3333333333333333]
24
Movie atts and strength values: ['writer', 'acting'], [0.75, 0.1951219512195122]
Movie supps and strength values: ['director', 'themes'], [1.0, 0.875]
24
FINAL PRINT
director 1.0
writer 0.75
JohnnyDepp 0.75
JavierBardem 1.0
PaulMcCartney 1.0
acting 0.1951219512195122
Legacy 0.3333333333333333
Betrayal 1.0
Adventure 0.3333333333333333
themes 0.875
film 0.70504214666341
[(30, [53.59374999999999, 53.1640625, 59.39815758143068, 70.504214666341], 'pirates of the caribbean dead men tell no tales', 'nr_reviews')]
'''
sections = extract_sections(text)
print(type(sections))
sostituzioni = ["QUAD", "DFQUAD", "REB", "ENERGY"]

# Sostituisci "FINAL PRINT" con le parole desiderate in base alla posizione
for i, sostituzione in enumerate(sostituzioni):
    sections[i] = sections[i].replace("FINAL PRINT", sostituzione)

# Stampa la lista risultante
print(sections)


texts = '\n'.join(sections)
print(texts)
chiamametodi(texts, "C:/Users/elisa/Desktop/excel tesi/journal/piratescaribbean17.xlsx", 'dir>wr bar>dep CUM 0.75 nr_rev')
    #dir>wr bard>depp

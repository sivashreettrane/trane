import csv

ahu_default = dict()
with open("AHU_Priority1.csv") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        ahu_default[row[1]] = {"sourceKey":row[0]}

print(ahu_default)
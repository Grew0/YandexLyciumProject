import csv

ships = [i.lower() for i in input().split(' - ')]
pir = input().lower()

with open('suitable_crew.csv', encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for index, row in enumerate(reader):
        if index == 0:
            continue
        if row[2] not in ships and pir not in row[3].lower():
            print(row[1], )

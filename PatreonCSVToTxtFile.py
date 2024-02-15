import csv
file = open('ClubOrionPatreons.txt', 'w', -1, 'utf-8')
with open("PatreonRaw.csv", 'r', -1, "utf-8") as raw:
  csvreader = csv.reader(raw)
  for row in csvreader:
    if(row[0] != 'Name'):
        print(row[0])
        file.write(row[0])
        file.write('\n')
file.close()
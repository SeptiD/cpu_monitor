import json
import csv


with open('hpc_info.txt') as inf:
    content = json.load(inf)
for elem in content:
    elem['key'] = 'r' + elem['UMask'][2:] + elem['EventCode'][2:]

fts = []
with open('feats') as inf:
    for line in inf:
        fts.append(line.strip()[0] + line.strip()[1:].upper())

results = []

for ft in fts:
    for elem in content:
        if ft in elem['key']:
            temp = {'key': elem['key'], 'EventName': elem['EventName'], 'BriefDescription': elem['BriefDescription']}
            results.append(temp)
            break
print(results)


with open('feat_csv.csv', mode='w') as csv_file:
    fieldnames = ['key', 'EventName', 'BriefDescription']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for res in results:
        writer.writerow(res)

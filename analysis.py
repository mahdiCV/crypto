import json
import pandas as pd


records = []
with open('log.txt') as f:
    for line in f.readlines():
        record = json.loads(line)
        if not record['action'] == 'sentOrder':
            records.append(record)
        #print(record)

df = pd.DataFrame(records)
df.to_csv('log.csv')
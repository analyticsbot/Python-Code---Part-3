import json

data= json.load(open('BAR.json', 'rb'))
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)

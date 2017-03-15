import pandas as pd
import time
from crunchbase_scraper_final import get_json_for_company
import requests

df = pd.read_csv('50urls.csv')
f = open('output.txt', 'wb')

for i, r in df.iterrows():
    url = r[0]
    res = requests.get(url).status_code
    try:
        if res ==200:
            res = get_json_for_company(url)
        else:
            res = get_json_for_company(url[53:])
        time.sleep(400)
        print url
        f.write(res + '\n\n')
    except:
        pass

f.close()
    
    

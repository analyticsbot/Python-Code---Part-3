import os
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:postgres@localhost:5432/dedupe')


df = pd.DataFrame(columns = ['phrase', 'volume'])
row_in_each_csv = 971150
directory = 'C:\\Users\\Ravi Shankar\\Documents\\Upwork\\dedupe\\'
#directory = '/home/ubuntu/dedupe/file1/'

done = ['dataset_5.csv%3Fdl=0', 'dataset_4_b.csv%3Fdl=0','dataset_4f.csv%3Fdl=0',\
        'dataset_4e.csv%3Fdl=0','dataset_4d.csv%3Fdl=0', 'dataset_4c.csv%3Fdl=0',\
        'dataset_4.csv%3Fdl=0', 'dataset_3_b.csv%3Fdl=0', 'dataset_3z.csv%3Fdl=0',\
        'dataset_3x.csv%3Fdl=0', 'dataset_3l.csv%3Fdl=0', 'dataset_3f.csv%3Fdl=0',\
        'dataset_3e.csv%3Fdl=0', 'dataset_3d.csv%3Fdl=0', 'dataset_3c.csv%3Fdl=0',\
        'dataset_3.csv%3Fdl=0', 'dataset_2_b.csv%3Fdl=0', 'dataset_2_a.csv%3Fdl=0',\
        'dataset_2z.csv%3Fdl=0', 'dataset_2x.csv%3Fdl=0', 'dataset_2l.csv%3Fdl=0',\
        'dataset_2k.csv%3Fdl=0', 'dataset_2g.csv%3Fdl=0', 'dataset_2f.csv%3Fdl=0',\
        'dataset_2e.csv%3Fdl=0', 'dataset_2d.csv%3Fdl=0', 'dataset_2c.csv%3Fdl=0',\
        'dataset_2.csv%3Fdl=0', 'dataset_1_b.csv%3Fdl=0', 'dataset_1_a.csv%3Fdl=0',\
        'dataset_1z.csv%3Fdl=0', 'dataset_1y.csv%3Fdl=0', 'dataset_1x.csv%3Fdl=0',\
        'dataset_1n.csv%3Fdl=0', 'dataset_1m.csv%3Fdl=0', 'dataset_1ll.csv%3Fdl=0',\
        'dataset_1l.csv%3Fdl=0', 'dataset_1k.csv%3Fdl=0', 'dataset_1g.csv%3Fdl=0',\
        'dataset_1f.csv%3Fdl=0', 'dataset_1ee.csv%3Fdl=0', 'dataset_1e.csv%3Fdl=0',\
        'dataset_1d.csv%3Fdl=0', 'dataset_1c.csv%3Fdl=0', 'dataset_1aa.csv%3Fdl=0',\
        'dataset_10_b.csv%3Fdl=0', 'dataset_10c.csv%3Fdl=0', 'dataset_1.csv%3Fdl=0']

for file in os.listdir(directory):
    
    if file.endswith(".csv%3Fdl=0"):
        if file in done:
            continue
        print file
        done.append(file)
        #os.rename(file, file[:-11] + '.csv')
        temp = pd.read_csv(file, sep = ",", header = None)
        print temp.shape
        print temp.columns
        if list(temp.columns) == [0,1]:
            temp.columns = ['phrase', 'volume']
        elif list(temp.columns) == [0,1,2]:
            temp.columns = ['junk', 'phrase', 'volume']
            temp = temp[['phrase', 'volume']]
        print temp.columns
        #temp.columns = ['phrase', 'volume']
        #temp = temp[['phrase', 'volume']]
        #df = pd.concat([df, temp], axis = 0)
        #print df.shape
        print temp.to_sql('dedupe2', engine, if_exists='append')

print df.shape

df = df.drop_duplicates()
print df.shape

count = 0
while True:
    from_ = row_in_each_csv*count
    to_ = row_in_each_csv*(count+1)
    print from_, to_
    if df[from_:to_].shape[0] != 0:
        df[971175*count:971175*(count+1)].to_csv('dataset_' + str(count+1)+'.csv')
        count +=1
    else:
        break

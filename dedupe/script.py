import pandas as pd
f = open('output.csv', 'rb')

df = pd.DataFrame(columns = ['phrase', 'volume'])
count = 0
while True:
    line = f.readline()
    if 'INSERT' in line:
        line_split = line.replace('INSERT INTO tmpdistinct VALUES (','').replace(';','').replace(')','').split(',')
        line_split = [l.strip().replace("'",'').replace('"','') for l in line_split][1:]
        nrow = df.shape[0]
        #print line_split
        df.loc[nrow+1] = line_split

        if df.shape[0] > 971155:
            count +=1
            df.to_csv('output_file_' + str(count) +'.csv', index= False)
            df = pd.DataFrame(columns = ['phrase', 'volume'])
            print 'output_file_' + str(count) +'.csv'

        if df.shape[0] == 0:
            break

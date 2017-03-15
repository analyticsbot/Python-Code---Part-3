f = open('output.backup', 'rb')

for i in range(48):
    f.readline()

count = 0
file_cnt= 1
import csv
o = open('output_0.csv', 'wb')
writer = csv.writer(o)
while True:
    count +=1
    d = f.readline().strip().split('\t')
    writer.writerow(d)
##    if count % 971150 ==0:
##        print count
    if len(d)==0:
        break
    if count % 971150 == 0:
        o.close()
        print 'output_'+str(file_cnt)+'.csv'
        o = open('output_'+str(file_cnt)+'.csv', 'wb')
        file_cnt +=1
        writer = csv.writer(o)

f.close()
o.close()
    
    

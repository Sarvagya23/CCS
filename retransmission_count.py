import csv

# open the CSV file and read the data
with open('retransmission_sequences.csv', 'r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # skip the first row
    data = list(csv_reader)

# extract the x and y data from the CSV
x = [float(row[0]) for row in data]
y = [float(row[1]) for row in data]

l = len(y)
mp = {1:0,2:0,3:0,4:0}

for i in range(l):
    count = int(y[i])
    if count not in mp.keys():
        mp[count] = 0
    mp[count] += 1

print(mp)
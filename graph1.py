import matplotlib.pyplot as plt
import csv

# open the CSV file and read the data
with open('window_size.csv', 'r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # skip the first row
    data = list(csv_reader)

# extract the x and y data from the CSV
x = [float(row[1]) for row in data]
y = [float(row[0]) for row in data]

# create a line graph using the x and y data
plt.scatter(x, y)

# add labels and title to the graph
plt.xlabel('X-axis label')
plt.ylabel('Y-axis label')
plt.title('Title of the graph')

# display the graph
plt.show()

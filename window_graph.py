import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a pandas dataframe
df = pd.read_csv('window_size.csv')

# Take the mean of every 10000 rows of window_size column and store in a new dataframe
df_agg = df.groupby(df.index // 10000).mean()

# Set the x-axis to be the timestamp column and the y-axis to be the window_size column
x = df_agg['timestamp']
y = df_agg['window_size']

# Plot the line graph
plt.plot(x, y)

# Add title and axis labels
plt.title('Window size over time')
plt.xlabel('Timestamp')
plt.ylabel('Window size')

# Display the graph
plt.show()






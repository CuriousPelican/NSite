"""# import statistics as s

# x = [1, 5, 7, 5, 43, 43, 8, 43, 6]

# quartiles = s.quantiles(x, n=4)
# print("Quartiles are: " + str(quartiles))
import numpy as np
import matplotlib.pyplot as plt

N = 5
menMeans = (20, 35, 30, 35, 27)
womenMeans = (25, 32, 34, 20, 25)

menStd = (2, 3, 4, 1, 2)
womenStd = (3, 5, 2, 3, 3)
# The x location for the groups
ind = np.arange(N)
print(ind)
# The width of the bars: can also be len(x) sequence
width = 0.35

p1 = plt.bar(ind, menMeans, width, yerr=menStd)
p2 = plt.bar(ind, womenMeans, width, bottom=menMeans, yerr=womenStd)

plt.ylabel('Scores')
plt.title('Scores by group and gender')
plt.xticks(ind, ('G1', 'G2', 'G3', 'G4', 'G5'))
plt.yticks(np.arange(0, 81, 10))
plt.legend((p1[0], p2[0]), ('Men', 'Women'))

plt.show()"""

from secrets import token_urlsafe
for i in range(30):
    i = token_urlsafe(32)
    print(i)
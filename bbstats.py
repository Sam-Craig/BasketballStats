import pandas
from os import listdir
from matplotlib import pyplot as plt
from scipy.stats import norm, normaltest
import numpy as np

csvloc = "/Users/samcraig/PycharmProjects/BasketballRefScraper/bbstats/"

playerdfs = []
for file in listdir(csvloc):
    if "players" in file:
        playerdfs.append((file[:9], pandas.read_csv(csvloc+file)))

playerdfs.sort(key = lambda x : x[0], reverse = True)

pp36 = [(p[0], p[1]["pp36"].values) for p in playerdfs]

#fig, axs = plt.subplots(3, 2)

#plt.subplots_adjust(hspace=.5)

stats = [(season[0], norm.fit(season[1])) for season in pp36]
print(stats)

'''for season in range(6):
    #plt.sca(axs[i // 2][i % 2])
    #stat, p = normaltest(pp36[i][1])
    #print(pp36[i][0] + ' Statistics=%.3f, p=%.3f' % (stat, p))
    mu, std = norm.fit(pp36[i][1])

    #plt.hist(pp36[i][1], bins=25, density=True, alpha=0.6, color='g')

    #plt.title(pp36[i][0])

    #xmin, xmax = plt.xlim()
    #x = np.linspace(xmin, xmax, 100)
    #p = norm.pdf(x, mu, std)
    #plt.plot(x, p, 'k', linewidth=2)
    #title = "{} season\n mu = {},  std = {}".format(pp36[i][0], round(mu,2), round(std,2))
    #plt.title(title)'''

plt.show()
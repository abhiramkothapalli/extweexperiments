import dpss

N = [4, 8, 16, 32, 64] # CONFIGURE
R = 1 # CONFIGURE
LOCAL = False # CONFIGURE


T = [int(n / 2) for n in N]

old_addrs = None
new_addrs = None

if LOCAL:
    old_addrs = ['localhost' + ':' + str(50000 + n) for n in range(N[-1])]
    new_addrs = ['localhost' +  ':' + str(50000 + N[-1] + n) for n in range(N[-1])]
else:
    old_addrs = ['node' + str(n) + ':' + '50050' for n in range(N[-1])]
    new_addrs = ['node' + str(N[-1] + n) +  ':' + '50050' for n in range(N[-1])]

resultsfile = 'experiment_results.txt'

PK = [dpss.setup(N[i], T[i]) for i in range(len(N))]





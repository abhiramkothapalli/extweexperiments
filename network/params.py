import dpss


N = [4]#[4, 8, 16]
T = [int(n / 2) for n in N]

NSHOST = 'localhost' # bulletin
NSPORT = 9090

resultsfile = 'experiment_results.txt'

PK = [dpss.setup(N[i], T[i]) for i in range(len(N))]


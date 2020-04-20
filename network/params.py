import dpss


N = [2]#[4, 8, 16]
T = [1]#[2, 4, 8]

PK = [dpss.setup(N[i], T[i]) for i in range(len(N))]


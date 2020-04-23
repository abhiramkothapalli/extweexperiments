import dpss


N = [4]#[4, 8, 16]
T = [2]#[2, 4, 8]

PK = [dpss.setup(N[i], T[i]) for i in range(len(N))]


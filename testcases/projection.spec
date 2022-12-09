#check x
#x = x[np.argsort(-fitness(x))][:n]
x = x[random.choices(range(n), weights=w)[0]]

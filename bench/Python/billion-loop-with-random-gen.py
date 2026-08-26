import time

def gen_rand_num():
    return int(str(time.time())[-1])

x = 0
for i in range(1000000000):
    x += i + gen_rand_num()

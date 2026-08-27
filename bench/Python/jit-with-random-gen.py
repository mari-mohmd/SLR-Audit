from numba import jit
import numpy as np

RANDOM_POOL = np.array([5, 4, 8, 9, 4, 2, 1])

@jit(nopython=True)
def compiled_function(random_pool):
    x = 0
    pool_size = random_pool.size

    for i in range(1000000000):
        if pool_size > 0:
            rand_num = random_pool[pool_size - 1]
            pool_size -= 1
        else:
            random_pool = np.array([5, 4, 8, 9, 4, 2, 1])
            pool_size = random_pool.size
            rand_num = random_pool[pool_size - 1]
            pool_size -= 1

        x += i + rand_num

    return x

result = compiled_function(RANDOM_POOL)

from numba import jit
    
@jit
def compiled_function():
    x = 0
    for i in range(1000000000):
        x+=i
    return x
    
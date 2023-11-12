import random
import math

class Randomizer:
    def Exp(self, mean_time):
        a = 0
        while a == 0:
            a = random.random()
        a = -mean_time * math.log(a)
        return a
        
    def Normal(self, mean_time, std_deviation):
        a = random.normalvariate(mean_time, std_deviation)
        return a
    
    def Uniform(self, a, b):
        a = random.uniform(a, b)
        return a
    
    # shape is k
    def Erlang(self, shape, mean_time):
        a = random.gammavariate(shape, mean_time / shape)
        return a
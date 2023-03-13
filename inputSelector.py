import itertools
import codecs
import string

# 1. How do we choose next input? (based on concrete data from past executions)
# CFG analyzer binary -> CFG, data collected -> generationally improving input selection
# Vulnerability -> path (one or more input that would cross this path) -> by choosing an input that can cross the path
# -> that would reveal the vulnerability if it existed
# 2^128 -> encounter at last case
# Symbolic -> loops -> infinite amount of possibilites -> and do loop unrolling
# Symbolic -> out-order-execution -> too many possible ways to reorder executions

class inputSelector:
    def __init__(self, logStorage, args):
        self.logStorage = logStorage
        self.args = args
        self.length = self.args.length[0]
        print(self.length)
        self.n = 0
        
    def select(self):
        #binary = self.__nthBinary(self.n)
        #binaryString = ''.join(binary)
        input = ''.join(self.__nth(itertools.product(string.ascii_letters, repeat = self.length), self.n))
        print(input)
        #input = self.__binaryToString(binaryString)
        self.n += 1
        return input


    #def __binaryToString(self, binary):
        #return int(binary, 2).to_bytes((len(binary) + 7) // 8, 'big').decode()

    #def __nthBinary(self, n):
        #return self.__nth(itertools.product("01", repeat = self.length), n)
    
    def __nth(self, iterable, n, default = None):
        return next(itertools.islice(iterable, n, None), default)
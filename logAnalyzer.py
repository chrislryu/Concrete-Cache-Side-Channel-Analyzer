from logStorage import logStorage
from assembly import *


class logAnalyzer:
    def __init__(self, logStorage, args, asmb):
        self.logStorage = logStorage
        self.args = args
        self.asmb = asmb
        self.uuid = args.uuid[0]
        self.functionNames = args.functions
        
        self.stack = 0
        self.functions = [self.asmb.get(functionName) for functionName in self.functionNames]
        
        for function in self.functions:
            print(function.getRet())
        
    def run(self, results):
        for index in results:
            self.__runSingle(index)
        
    def __runSingle(self, index):
        path = 'data/' + self.uuid + '/logs/' + str(index) + '/'
        depTraceFile = path + 'deptrace'
        instTraceFile = path + 'insttrace'
        cacheFile = path + 'system.l2.csv'
        
        #depTrace = (line[:-1].replace(':', ',').split(',') for line in open(depTraceFile, 'r').readlines() if len(line) > 1)
        instTrace = [line[:-1].split(',')[1:] for line in open(instTraceFile, 'r').readlines() if len(line) > 1]
        cacheTrace = [line[:-1].split(',') for line in open(cacheFile, 'r').readlines() if len(line) > 1]
        
        criticalCacheTrace = []
        cachePointer = 0
        
        for _, _, _, tick, pc in instTrace:
            if self.__inFunction(pc):
                self.stack += 1
            
            while cachePointer < len(cacheTrace) and int(tick) < int(cacheTrace[cachePointer][3]):
                if self.stack > 0:
                    criticalCacheTrace.append(cachePointer)
                cachePointer += 1
                
            if self.__outFunction(pc):
                self.stack -= 1
        
        print(criticalCacheTrace)
    
    def __inFunction(self, pc):
        # TODO: Could improve the algorithm in this one. Don't need to iterate everything. Maybe combine sets
        intPc = int(pc)
        
        for function in self.functions:
            if intPc is function.getFirst():
                return True
        return False
    
    def __outFunction(self, pc):
        # TODO: Could improve the algorithm in this one. Don't need to iterate everything. Maybe combine sets
        intPc = int(pc)
        
        for function in self.functions:
            if intPc in function.getRet():
                return True
        return False
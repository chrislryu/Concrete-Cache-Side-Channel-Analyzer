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
        
        
    def run(self, results):
        for index in results:
            self.__runSingle(index)
        
        
    def __runSingle(self, index):
        path = 'data/' + self.uuid + '/logs/' + str(index) + '/'
        depTraceFile = path + 'deptrace'
        instTraceFile = path + 'insttrace'
        icacheFile = path + 'system.cpu.icache.csv'
        dcacheFile = path + 'system.cpu.dcache.csv'
        
        #depTrace = (line[:-1].replace(':', ',').split(',') for line in open(depTraceFile, 'r').readlines() if len(line) > 1)
        #instTrace = [line[:-1].split(',')[1:] for line in open(instTraceFile, 'r').readlines() if len(line) > 1]
        icacheTrace = [line[:-1].split(',') for line in open(icacheFile, 'r').readlines()[:-1]]
        dcacheTrace = [line[:-1].split(',') for line in open(dcacheFile, 'r').readlines()[:-1]]
        
        criticalCacheTrace = []
        cachePointer = 0
        
        for pc, _, _, tick, _ in icacheTrace:
            if self.__inFunction(pc):
                self.stack += 1
            
            while cachePointer < len(dcacheTrace) and int(dcacheTrace[cachePointer][3]) < int(tick):
                if self.stack > 0:
                    criticalCacheTrace.append(cachePointer)
                cachePointer += 1
                
            if self.__outFunction(pc):
                self.stack -= 1
    
    def __inFunction(self, pc):
        # TODO: Could improve the algorithm in this one. Don't need to iterate everything. Maybe combine sets
        intPc = int(pc)
        
        for function in self.functions:
            if intPc == function.getFirst():
                return True
        return False
    
    def __outFunction(self, pc):
        # TODO: Could improve the algorithm in this one. Don't need to iterate everything. Maybe combine sets
        intPc = int(pc)
        
        for function in self.functions:
            if intPc in function.getRet():
                return True
        return False
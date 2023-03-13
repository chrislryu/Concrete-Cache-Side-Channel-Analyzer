from logStorage import logStorage
from assembly import *
from node import node
from multiprocessing import Pool
from hashlib import sha256

import networkx as nx

def runSingle(uuid, index, functions):
    path = 'data/' + uuid + '/logs/' + str(index) + '/'
    #depTraceFile = path + 'deptrace'
    #instTraceFile = path + 'insttrace'
    icacheFile = path + 'system.cpu.icache.csv'
    dcacheFile = path + 'system.cpu.dcache.csv'
    
    #depTrace = (line[:-1].replace(':', ',').split(',') for line in open(depTraceFile, 'r').readlines() if len(line) > 1)
    #instTrace = [line[:-1].split(',')[1:] for line in open(instTraceFile, 'r').readlines() if len(line) > 1]
    icacheTrace = [line[:-1].split(',') for line in open(icacheFile, 'r').readlines()[:-1]]
    dcacheTrace = [line[:-1].split(',') for line in open(dcacheFile, 'r').readlines()[:-1]]
    
    criticalCacheTrace = []
    cachePointer = 0
    stack = 0
    
    for pc, paddr, vaddr, tick, stat in icacheTrace:
        if inFunction(pc, functions):
            stack += 1
        
        while cachePointer < len(dcacheTrace) and int(dcacheTrace[cachePointer][3]) < int(tick):
            if stack > 0:
                dpc, dpaddr, dvaddr, _, dstat = dcacheTrace[cachePointer]
                criticalCacheTrace.append((dpc, dpaddr, dvaddr, dstat))
            cachePointer += 1
            
        if outFunction(pc, functions):
            stack -= 1
    
    return (index, criticalCacheTrace)


def inFunction(pc, functions):
    # TODO: Could improve the algorithm in this one. Don't need to iterate everything. Maybe combine sets
    intPc = int(pc)
    
    for function in functions:
        if intPc == function.getFirst():
            return True
    return False


def outFunction(pc, functions):
    # TODO: Could improve the algorithm in this one. Don't need to iterate everything. Maybe combine sets
    intPc = int(pc)
    
    for function in functions:
        if intPc in function.getRet():
            return True
    return False


class logAnalyzer:
    def __init__(self, logStorage, args, asmb):
        self.logStorage = logStorage
        self.args = args
        self.asmb = asmb
        self.uuid = args.uuid[0]
        self.functionNames = args.functions
        
        self.stack = 0
        self.functions = [self.asmb.get(functionName) for functionName in self.functionNames]
        self.results = []
        self.pool = Pool(processes=self.args.thread[0])
        
        
    def run(self, results):
        for index in results:
            self.__runSingle(index)
            #self.results.append(self.pool.apply_async(runSingle, args=(self.uuid, index, self.functions)))
        """
        results = []
        for result in self.results:
            if result.ready():
                index, criticalCacheTrace = result.get()
                self.results.remove(result)
                self.logStorage.store(index, criticalCacheTrace)
                results.append(index)
        """
        return results

        
    def __runSingle(self, index):
        path = 'data/' + self.uuid + '/logs/' + str(index) + '/'
        #depTraceFile = path + 'deptrace'
        #instTraceFile = path + 'insttrace'
        icacheFile = path + 'system.cpu.icache.csv'
        dcacheFile = path + 'system.cpu.dcache.csv'
        
        #depTrace = (line[:-1].replace(':', ',').split(',') for line in open(depTraceFile, 'r').readlines() if len(line) > 1)
        #instTrace = [line[:-1].split(',')[1:] for line in open(instTraceFile, 'r').readlines() if len(line) > 1]
        icacheTrace = [line[:-1].split(',') for line in open(icacheFile, 'r').readlines()[:-1]]
        dcacheTrace = [line[:-1].split(',') for line in open(dcacheFile, 'r').readlines()[:-1]]
        
        cachePointer = 0
        accessList = []
        hashList = []
        currIndex = None
        indexCount = 0
        
        # TODO: Temporary solution for callq being included. Find better way.
        skip = False
        
        for pc, _, _, tick, _ in icacheTrace:
            if self.__inFunction(pc):
                if self.stack == 0:
                    skip = True
                self.stack += 1
            
            # TODO: Check if <= or < or tick comparison!
            while cachePointer < len(dcacheTrace) and int(dcacheTrace[cachePointer][3]) <= int(tick):
                if self.stack > 0 and not skip:
                    dpc, dpaddr, dvaddr, _, dstat = dcacheTrace[cachePointer]
                    index = self.asmb.getIndex(int(dpc))
                    
                    if index != currIndex:
                        if index is not None:
                            hashList.append((currIndex, self.__hash(accessList)))
                            accessList = []
                        currIndex = index
                        indexCount += 1
                    
                    accessList.append(dpc, dpaddr, dvaddr, dstat)
                        
                cachePointer += 1
                skip = False
                
            if self.__outFunction(pc):
                self.stack -= 1
                
        if len(hashList) != indexCount:
            hashList.append((currIndex, self.__hash(accessList)))
        
        self.logStorage.store(index, hashList)
        #return (index, criticalCacheTrace)
    
    
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
    
    def __hash(self, accessList):
        return sha256(str(accessList).encode()).hexdigest()
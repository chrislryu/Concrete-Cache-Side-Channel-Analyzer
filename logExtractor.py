from logStorage import logStorage
from inputSelector import inputSelector

import os
import subprocess


class logExtractor:
    def __init__(self, logStorage, args):
        self.args = args
        self.logStorage = logStorage
        self.numProcesses = args.thread[0]
        self.binary = args.binary[0]
        self.uuid = args.uuid[0]
        self.inputSelector = inputSelector(logStorage, args)
        self.processes = []
        
    def run(self):
        while len(self.processes) < self.numProcesses:
            input = self.inputSelector.select()
            self.__execute(input)
        
        return self.__check()
        
    def __execute(self, input):
        gem5 = '../../../../gem5/build/X86/gem5.fast'
        gem5Script = '../../../../gem5/configs/example/se.py'
        cpuType = '--cpu-type=X86O3CPU'
        L1Cache = '--caches'
        L2Cache = '--l2cache'
        elasticTrace = '--elastic-trace-en'
        dataTraceFile = '--data-trace-file=deptrace.proto.gz'
        instructionTraceFile = '--inst-trace-file=fetchtrace.proto.gz'
        memoryType = '--mem-type=SimpleMemory'
        binary = '--cmd=../../../../' + self.binary
        index = self.__createFolder()
        
        with open(os.path.join(self.__joinPath__(index), 'stdin'), 'wb') as stdin:
            stdin.write(input.encode())
        
        stdin = open(os.path.join(self.__joinPath__(index), 'stdin'), 'r')
        stdout = open(os.path.join(self.__joinPath__(index), 'stdout'), 'w')
        stderr = open(os.path.join(self.__joinPath__(index), 'stderr'), 'w')
        
        cmd = [gem5, gem5Script, cpuType, L1Cache, L2Cache, elasticTrace, dataTraceFile, instructionTraceFile, memoryType, binary]
        process = subprocess.Popen(cmd, stdin=stdin, stdout=stdout, stderr=stderr, cwd='data/'+self.uuid+'/logs/'+str(index))
        self.processes.append((index, process, stdin, stdout, stderr))
        
    def __check(self):
        results = []
        
        for index, process, stdin, stdout, stderr in self.processes:
            if process.poll() is not None:
                stdin.close()
                stdout.close()
                stderr.close()
                results.append(index)
        
        self.processes = [(index, process, stdin, stdout, stderr) for index, process, stdin, stdout, stderr in self.processes if index not in results]
        
        return results
        
    def __createFolder(self):
        index = 0
        while os.path.isdir(self.__joinPath__(index)):
            index += 1
        os.mkdir(self.__joinPath__(index))
        return index
    
    def __joinPath__(self, index):
        return os.path.join(os.path.join('data', self.uuid), os.path.join('logs', str(index)))
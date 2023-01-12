from logStorage import logStorage


class logAnalyzer:
    def __init__(self, logStorage, args, asmb):
        self.logStorage = logStorage
        self.args = args
        self.asmb = asmb
        self.uuid = args.uuid[0]
        
    def run(self, results):
        for index in results:
            self.__runSingle(index)
            
    def __runSingle(self, index):
        path = 'data/' + self.uuid + '/logs/' + str(index) + '/'
        deptraceFile = path + 'deptrace'
        insttraceFile = path + 'insttrace'
        
        deptrace = [line[:-1].replace(':', ',').split(',') for line in open(deptraceFile, 'r').readlines() if len(line) > 1]
        insttrace = [line[:-1].split(',') for line in open(insttraceFile, 'r').readlines() if len(line) > 1]
        
        print(deptrace)
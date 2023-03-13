import os, shutil
import networkx as nx
from hashlib import sha256

class logStorage:
    def __init__(self, args):
        self.args = args
        self.uuid = args.uuid[0]
        os.mkdir(self.__hashPath())
    
    def __hashPath(self):
        return os.path.join(self.__path(), 'hash')
    
    def __logPath(self, index):
        return os.path.join(self.__path(), 'logs', str(index))
    
    def __path(self):
        return os.path.join('data', self.uuid)
    
    def __convertData(self, data):
        return str(data).encode()
    
    def store(self, index, data):
        lPath = self.__logPath(index)
        hPath = self.__hashPath()
        
        cData = self.__convertData(data)
        hash = hashlib.sha512(cData).hexdigest()
        
        hPath = os.path.join(self.__hashPath(), hash)
        
        if os.path.isdir(hPath):
            self.__store(lPath, hPath, data)
        else:
            os.mkdir(hPath)
            os.mkdir(os.path.join(hPath, 'stdin'))
            os.mkdir(os.path.join(hPath, 'stdout'))
            self.__store(lPath, hPath, data)
            
    def __store(self, lPath, hPath, data):
        shutil.copyfile(os.path.join(lPath, 'stdin'), self.__find(hPath, 'stdin'))
        shutil.copyfile(os.path.join(lPath, 'stdout'), self.__find(hPath, 'stdout'))
        with open(os.path.join(hPath, 'l1log'), 'w') as file:
            for line in data:
                file.write(','.join(line))
                file.write('\n')
        
    def __find(self, hPath, folder):
        index = 0
        while os.path.isfile(os.path.join(hPath, folder, str(index))):
            index += 1
        return os.path.join(hPath, folder, str(index))
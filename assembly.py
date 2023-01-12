import os
import re

class assembly:
    def __init__(self, path):
        self.sectionDict = dict()
        self.__parse(path)
            
    def __parse(self, path):
        assemblyFile = open(os.path.join(path, 'assembly'), 'r')
        assemblyString = assemblyFile.read()
        assemblyList = assemblyString.split('\n\n')
        
        section = None
        
        for item in assemblyList:
            if len(item) > 0 and item[0].isnumeric():
                m = method(item, section)
                self.sectionDict[m.name] = m
            elif "Disassembly of section" in item:
                section = item[23:][:-1]
                
    def get(self, method):
        return self.sectionDict[method]

class method:
    def __init__(self, methodString, section = None, offset = 0):
        self.section = section
        self.offset = offset
        self.instDict = dict()
        self.retList = list()
        self.__parse(methodString)
    
    def __parse(self, methodString):
        lines = methodString.splitlines()
        header = lines[0][:-1].split()
        body = lines[1:]
        
        self.start = header[0]
        self.name = header[1][1:][:-1]
        
        for item in body:
            srtAdrStr, hexStr, *asmStr = [re.sub(r' {2,}', '',  s) for s in re.split(r'\t+', item)]
            asmStr = asmStr or None
            adrStr = self.__convert(self.__replace(srtAdrStr))
            self.instDict[adrStr] = (hexStr, asmStr)
            
            if asmStr:
                if 'retq' in asmStr:
                    self.retList.append(adrStr)
            
    def __replace(self, srtAdrStr):
        return self.start[:-len(srtAdrStr)] + srtAdrStr
    
    def __convert(self, adrStr):
        return adrStr
    
    def getRet(self):
        return self.retList
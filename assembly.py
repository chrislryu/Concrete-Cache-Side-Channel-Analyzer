import os
import re

jmpInstSet = set(['jmpq', 'jmp', 'je', 'jne', 'jg', 'jge', 'ja', 'jae', 'jl', 'jle', 'jb', 'jbe', 'jz', 'jnz', 'js', 'jns', 'jc', 'jnc', 'jo', 'jno', 'jcxz', 'jecxz', 'jrcxz', 'callq', 'retq'])

class assembly:
    def __init__(self, path):
        self.sectionDict = dict()
        self.basicBlocks = dict()
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
        
        self.__defineBasicBlocks()
        
    def __defineBasicBlocks(self):
        basicBlockIndex = 0
        for section in self.sectionDict.values():
            for i, j in section.getBasicBlocks():
                for x in range(i, j + 1):
                    self.basicBlocks[x] = basicBlockIndex
                basicBlockIndex+=1
                
    def get(self, method):
        return self.sectionDict[method]
    
    def getIndex(self, pc):
        return self.basicBlocks[pc] if pc in self.basicBlocks else None


class method:
    def __init__(self, methodString, section = None, offset = 0):
        self.section = section
        self.offset = offset
        self.retList = set()
        self.first = None
        self.basicBlocks = []
        self.__parse(methodString)
    
    def __parse(self, methodString):
        lines = methodString.splitlines()
        header = lines[0][:-1].split()
        body = lines[1:]
        
        self.start = header[0]
        self.name = header[1][1:][:-1]
        
        basicBlockStart = None
        adrInt = None
        
        for item in body:
            if item.find('...') != -1:
                continue
            
            srtAdrStr, hexStr, *asmStr = [s for s in re.split(r'\t+', item)]
            srtAdrStr = re.sub(r' {2,}', '',  srtAdrStr)
            asmStr = asmStr or None
            if asmStr:
                asmStr = asmStr[0].replace('  ', ' ').split(' ')[0]
            adrInt = self.__convert(self.__replace(srtAdrStr))
            
            if basicBlockStart is None:
                basicBlockStart = adrInt
            
            if asmStr and asmStr in jmpInstSet:
                self.basicBlocks.append((basicBlockStart, adrInt))
                basicBlockStart = None
            
            if asmStr and 'retq' in asmStr:
                self.retList.add(adrInt)
                    
            if self.first is None:
                self.first = adrInt
        
        if basicBlockStart is not None:
            self.basicBlocks.append((basicBlockStart, adrInt))
            
    def __replace(self, srtAdrStr):
        return int(self.start[:-len(srtAdrStr)] + srtAdrStr.replace(':', ''), 16)
    
    def __convert(self, adrStr):
        return adrStr
    
    def getRet(self):
        return self.retList
    
    def getFirst(self):
        return self.first
    
    def getBasicBlocks(self):
        return self.basicBlocks
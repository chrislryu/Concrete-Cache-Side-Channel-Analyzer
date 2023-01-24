#!/usr/bin/python3

from logStorage import logStorage
from logExtractor import logExtractor
from logParser import logParser
from logAnalyzer import logAnalyzer
from logCleaner import logCleaner
from assembly import *

from time import sleep
from uuid import uuid4
from multiprocessing import Process
from multiprocessing import Queue

import os
import pathlib
import argparse
import signal
import sys
import subprocess


class wrapper:
    
    
    def __init__(self, args):
        self.args = args
        self.userSignal = False
        
        if not self.__createDataPath():
            asmb = self.__preAnalysis()
            self.logStorage = logStorage(self.args)
            self.logExtractor = logExtractor(self.logStorage, self.args)
            self.logParser = logParser(self.logStorage, self.args)
            self.logAnalyzer = logAnalyzer(self.logStorage, self.args, asmb)
            self.logCleaner = logCleaner(self.args)
        else:
            self.__load()
            # TODO: create class instances with loaded data
            
        self.__uuid()
        
        
    def __cleanUp(self):
        sys.exit(0)
        
        
    def __createDataPath(self):
        self.path = os.path.join('data', self.args.uuid[0])
        self.logPath = os.path.join(self.path, 'logs')
        
        if not os.path.exists(self.path):
            self.args.uuid[0] = str(uuid4())
            self.path = os.path.join('data', self.args.uuid[0])
            self.logPath = os.path.join(self.path, 'logs')
            
            os.mkdir(self.path)
            os.mkdir(self.logPath)
            
            return True
        
        return False
    
    
    def __uuid(self):
        print(self.args.uuid[0])
    
    
    def __load(self):
        # TODO: load previous data
        pass
        
        
    def __preAnalysis(self):
        #self.__objdump()
        return self.__assembly()
        
        
    def __objdump(self):
        cmd = ['objdump', '-d', self.args.binary[0]]
        stdout = open(os.path.join(self.path, 'assembly'), 'w')
        process = subprocess.Popen(cmd, stdout=stdout)
        process.wait()
        # TODO: check return code
        
        
    def __assembly(self):
        return assembly(self.path)
    
    
    def run(self):
        # TODO: Detecting signal is sometimes finicky -- not super critical but fix if possible
        def userSignalHandler(signal, frame):
            self.userSignal = True
        
        signal.signal(signal.SIGUSR1, userSignalHandler)
        
        while not self.userSignal:
            results = [0]
            #results = self.logExtractor.run()
            #self.logParser.run(results)
            self.logAnalyzer.run(results)
            #self.logCleaner.run(results)
            sleep(0.01)
            
            if len(results) > 0:
                break
        
        self.__cleanUp()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='CCSD', description='Concrete Cache Side-Channel Detector')
    parser.add_argument('-t', '--thread', nargs=1, type=int, default=[1], help='Number of threads to use')
    parser.add_argument('-b', '--binary', nargs=1, type=str, help='Relative path of binary to analyze', required=True)
    parser.add_argument('-u', '--uuid', nargs=1, type=str, default=['uuid'], help='UUID of previous run')
    parser.add_argument('-f', '--functions', nargs=1, type=str, help='Function(s) to flag', required=True)
    args = parser.parse_args()
    
    wrapperInstance = wrapper(args)
    wrapperInstance.run()
    
    # "wrapper" -> generates input -> blowfish (separate process) : gem5 analyzes binary
    # "wrapper" -> main method that generates inputs for blowfish by importing blowfish and calling it -> compile that
    # "wrapper" -> "new wrapper" know about previous data? 
    
    # "wrapper1" -> running gem5 and analyzing results and storing results
    # "wrapper2" -> reading results and generating inputs for binary
    
    # locking between two processes 
    # assumption1 -> we assume that there would be no security issues in reading stdin/stdout
    # assumption2 -> we assume that the cache from previous run doesn't matter
    
    # -- randomization appporach --
    # randomization of cache -> user to flag a instruction -> gem5: at that instruction, randomize cache state
    
    # -- consistent approach --
    # input -> for loop (encrypts input1, input2 ...) -> ends
    # standard library -> chances cache state -> flag this point at which -> 1st run -> save -> 2nd or next run -> restore the saved cache state
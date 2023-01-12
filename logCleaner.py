import shutil
import os

class logCleaner:
    def __init__(self, args):
        self.args = args
        self.uuid = args.uuid[0]
        
    def run(self, results):
        for index in results:
            self.__runSingle__(index)
            
    def __runSingle__(self, index):
        shutil.rmtree(os.path.join(os.path.join('data', self.uuid), os.path.join('logs', str(index))))
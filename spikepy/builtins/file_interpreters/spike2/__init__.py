

from spikepy.developer.file_interpreter import FileInterpreter
from .sonpy import son

class Spike2(FileInterpreter):
    def __init__(self):
        self.name = "Spike2 Format"
        self.extentions = ['.smr']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''Cambridge Electronic Design's Spike2 or (Son) format.'''

    def read_data_file(self, fullpath):
        header = son.FileHeader(fullpath)
        print dir(header)
        chan = son.Channel(1, fullpath)
        data = chan.data()
        chan_info = chan.info


from spikepy.developer.file_interpreter import FileInterpreter, Trial,\
        Strategy

class SpikepyStrategy(FileInterpreter):
    def __init__(self):
        self.name = 'Spikepy Strategy'
        self.extentions = ['.strategy']
        # higher priority means will be used in ambiguous cases
        self.priority = 10 
        self.description = '''A previously saved spikepy strategy.'''

    def read_data_file(self, fullpath):
        strategy = Strategy.from_file(fullpath)
        strategy.fullpath = None
        return [strategy]

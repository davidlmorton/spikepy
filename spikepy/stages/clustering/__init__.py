import os

methods = []

this_file = __file__
this_dir = os.path.split(this_file)[0] 

files_in_this_dir = os.listdir(this_dir)
for file in files_in_this_dir:
    if (os.path.isdir(os.path.join(this_dir, file)) and 
        not file.startswith(".")):
        exec('from . import %s' % file)
        methods.append(eval(file))
